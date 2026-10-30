import os
import sys
import json
import shutil
import re

DRE_EMP_DIR = r"c:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\ANTIGRAVITY\PROJETOS\Dre_Empresa"
INTRANET_DIR = r"c:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\ANTIGRAVITY\PROJETOS\INTRANET"
PORTFOLIO_DIR = os.path.join(INTRANET_DIR, "portfolio_standalone")

sys.path.insert(0, DRE_EMP_DIR)
from db import get_db_connection

ALLOWED_COMPANIES = [
    'Consolidação', 'FORX SC', 'MCR - FABRICA', 'MCR - FILIAL 03',
    'MCR - MATRIZ', 'MCR - SC', 'QUALITY - RJ', 'QUALITY MATRIZ',
    'SL ONLINE - SP', 'VLS - RJ', 'VLS - SP', 'FORX MG'
]

def sanitize_account_name(name):
    if not name:
        return ""
    val = name.strip()
    val = re.sub(r'\bMQ\s*PROFESSIONAL\b', 'LINHA 01', val, flags=re.IGNORECASE)
    val = re.sub(r'\bMQ\s*BEAUTY\b', 'LINHA 02', val, flags=re.IGNORECASE)
    val = re.sub(r'\bMQ\s*HAIR\b', '', val, flags=re.IGNORECASE)
    val = re.sub(r'\bMQ\b', '', val, flags=re.IGNORECASE)
    val = re.sub(r'\bMCR\b', 'OPERACIONAL', val, flags=re.IGNORECASE)
    val = re.sub(r'\s{2,}', ' ', val).strip(' -')
    return val

def extract_dre_empresa_data():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT ano FROM dre_filtros_anos
        WHERE ano >= 2024 AND ano <= 2027
        ORDER BY ano DESC
    """)
    anos = [int(r["ano"]) for r in cur.fetchall()]
    if not anos:
        anos = [2026, 2025, 2024]

    placeholders = ",".join(["%s"] * len(ALLOWED_COMPANIES))
    cur.execute(f"""
        SELECT nome FROM dre_filtros_empresas
        WHERE nome IN ({placeholders})
        ORDER BY nome
    """, ALLOWED_COMPANIES)
    
    # Anonymize empresas: Empresa 01, Empresa 02...
    raw_empresas = cur.fetchall()
    empresas = []
    emp_anon_map = {}
    for idx, r in enumerate(raw_empresas):
        nome_orig = r["nome"]
        if "consolida" in nome_orig.lower():
            nome_anon = "Consolidação Geral"
        else:
            nome_anon = f"Empresa {idx:02d}"
        empresas.append({"CODEMP": nome_orig, "NOME": nome_anon})
        emp_anon_map[nome_orig] = nome_anon

    # Unique centros deduplicated by codcencus
    cur.execute("""
        SELECT DISTINCT codcencus FROM dre_filtros_centros
        WHERE codcencus > 0 AND codcencus != 21010000
        ORDER BY codcencus
    """)
    centros_rows = cur.fetchall()
    centros = [
        {"CODCENCUS": int(r["codcencus"]), "NOME": f"Centro de Resultado {idx+1:02d}"}
        for idx, r in enumerate(centros_rows)
    ]

    # 1. Linhas agrupadas por (ano, mes, empresa, bloco, titulo, descrnat)
    cur.execute(f"""
        SELECT ano, mes, empresa, bloco, titulo, descrnat,
               ROUND(SUM(orcado), 2) AS orcado,
               ROUND(SUM(realizado), 2) AS realizado
        FROM dre_data
        WHERE ano >= 2024
          AND codcencus != 21010000
          AND empresa IN ({placeholders})
          AND (ABS(orcado) > 0.001 OR ABS(realizado) > 0.001)
        GROUP BY ano, mes, empresa, bloco, titulo, descrnat
        ORDER BY bloco, titulo, descrnat
    """, ALLOWED_COMPANIES)
    emp_rows = [dict(r) for r in cur.fetchall()]

    # 2. Resumo por centro de custo para /api/dre/tabela-mensal
    cur.execute(f"""
        SELECT ano, mes, empresa, codcencus, descrcencus, bloco,
               ROUND(SUM(orcado), 2) AS orcado,
               ROUND(SUM(realizado), 2) AS realizado
        FROM dre_data
        WHERE ano >= 2024
          AND codcencus != 21010000
          AND codcencus != 0
          AND empresa IN ({placeholders})
          AND descrcencus IS NOT NULL
          AND TRIM(descrcencus) != ''
          AND descrcencus != 'Consolidado PBI'
          AND descrnat != 'AJUSTE PBI'
          AND (ABS(orcado) > 0.001 OR ABS(realizado) > 0.001)
        GROUP BY ano, mes, empresa, codcencus, descrcencus, bloco
        ORDER BY descrcencus, bloco
    """, ALLOWED_COMPANIES)
    cenc_rows = [dict(r) for r in cur.fetchall()]

    conn.close()

    emp_list, blocos, titulos, descrnats, descrcencs = [], [], [], [], []
    e_map, b_map, t_map, d_map, dc_map = {}, {}, {}, {}, {}
    compact_rows = []
    compact_cenc_rows = []

    # Pre-map distinct descrcencs to Centro de Resultado 01, 02...
    distinct_dc = sorted(list(set((r["descrcencus"] or "").strip() for r in cenc_rows if (r["descrcencus"] or "").strip())))
    dc_name_map = {}
    for idx, dc in enumerate(distinct_dc):
        anon_name = f"Centro de Resultado {idx+1:02d}"
        dc_name_map[dc] = anon_name
        dc_map[anon_name] = len(descrcencs)
        descrcencs.append(anon_name)

    for r in emp_rows:
        e = (r["empresa"] or "").strip()
        b = (r["bloco"] or "").strip()
        t = sanitize_account_name(r["titulo"])
        d = sanitize_account_name(r["descrnat"])
        if e not in e_map:
            e_map[e] = len(emp_list)
            emp_list.append(e)
        if b not in b_map:
            b_map[b] = len(blocos)
            blocos.append(b)
        if t not in t_map:
            t_map[t] = len(titulos)
            titulos.append(t)
        if d not in d_map:
            d_map[d] = len(descrnats)
            descrnats.append(d)

        compact_rows.append([
            int(r["ano"]),
            int(r["mes"]),
            e_map[e],
            b_map[b],
            t_map[t],
            d_map[d],
            round(float(r["orcado"] or 0), 2),
            round(float(r["realizado"] or 0), 2)
        ])

    for r in cenc_rows:
        e = (r["empresa"] or "").strip()
        b = (r["bloco"] or "").strip()
        dc_raw = (r["descrcencus"] or "").strip()
        dc_anon = dc_name_map.get(dc_raw, f"Centro de Resultado {len(descrcencs)+1:02d}")

        if e not in e_map:
            e_map[e] = len(emp_list)
            emp_list.append(e)
        if b not in b_map:
            b_map[b] = len(blocos)
            blocos.append(b)

        compact_cenc_rows.append([
            int(r["ano"]),
            int(r["mes"]),
            e_map[e],
            int(r["codcencus"]),
            dc_map[dc_anon],
            b_map[b],
            round(float(r["orcado"] or 0), 2),
            round(float(r["realizado"] or 0), 2)
        ])

    return {
        "anos": anos,
        "empresas": empresas,
        "centros": centros,
        "emp_list": emp_list,
        "blocos": blocos,
        "titulos": titulos,
        "descrnats": descrnats,
        "descrcencs": descrcencs,
        "rows": compact_rows,
        "cenc_rows": compact_cenc_rows
    }


JS_ENGINE = """// ============================================================================
// DRE CONSOLIDADO EMPRESA — STANDALONE ENGINE (Portfólio Executivo)
// ============================================================================
(function() {
  const DB = window.__DRE_EMPRESA_DB__;

  const MESES_LISTA = [
    { NUM: 1, NOME: "Janeiro" }, { NUM: 2, NOME: "Fevereiro" },
    { NUM: 3, NOME: "Março" }, { NUM: 4, NOME: "Abril" },
    { NUM: 5, NOME: "Maio" }, { NUM: 6, NOME: "Junho" },
    { NUM: 7, NOME: "Julho" }, { NUM: 8, NOME: "Agosto" },
    { NUM: 9, NOME: "Setembro" }, { NUM: 10, NOME: "Outubro" },
    { NUM: 11, NOME: "Novembro" }, { NUM: 12, NOME: "Dezembro" }
  ];

  function parseIntList(raw, defVal) {
    if (!raw || raw === "ALL") return defVal ? [...defVal] : [];
    const out = [];
    String(raw).split(",").forEach(part => {
      const p = part.trim();
      if (p && p !== "ALL") {
        const n = parseInt(p, 10);
        if (!isNaN(n)) out.push(n);
      }
    });
    return out.length ? out : (defVal ? [...defVal] : []);
  }

  function parseStrList(raw) {
    if (!raw || raw === "ALL") return [];
    const out = [];
    String(raw).split(",").forEach(part => {
      const p = part.trim();
      if (p && p !== "ALL") out.push(p);
    });
    return out;
  }

  function isCostOrExpense(bloco, titulo) {
    const b = (bloco || "").toLowerCase();
    const t = (titulo || "").toLowerCase();
    if (b.includes("custo") || b.includes("despesa")) return true;
    const kw = ["devolução", "devolucao", "imposto", "irpj", "csll", "desc financeiro", "cpv", "frete"];
    return kw.some(k => t.includes(k));
  }

  function calcVar(r, b, isDesp) {
    if (b === null || b === undefined || Math.abs(b) < 0.001) return null;
    if (isDesp) {
      const diff = Math.abs(r) - Math.abs(b);
      return Number(((diff / Math.abs(b)) * 100).toFixed(2));
    }
    return Number((((r - b) / Math.abs(b)) * 100).toFixed(2));
  }

  function calcRo(r, o) {
    if (!o || Math.abs(o) < 0.001) return null;
    return Number((((r - o) / o) * 100).toFixed(2));
  }

  function pct(n, d) {
    if (!d || Math.abs(d) < 1.0 || n === null || n === undefined) return null;
    return Number(((n / d) * 100).toFixed(2));
  }

  function handleFiltros() {
    return {
      anos: DB.anos,
      meses: MESES_LISTA,
      empresas: DB.empresas,
      centros: DB.centros
    };
  }

  function handleDre(params) {
    const anos = parseIntList(params.get("ano"), [2026]);
    const meses = parseIntList(params.get("mes"), [9]);
    const emps = parseStrList(params.get("emp"));
    const empSet = emps.length ? new Set(emps) : null;

    const anoPrimario = Math.max(...anos);
    const mesPrimario = Math.max(...meses);
    const anoMom = mesPrimario > 1 ? anoPrimario : anoPrimario - 1;
    const mesMom = mesPrimario > 1 ? mesPrimario - 1 : 12;
    const anoYoy = anoPrimario - 1;

    const anosSet = new Set(anos);
    const mesesSet = new Set(meses);
    const mesesYtdSet = new Set();
    for (let m = 1; m <= mesPrimario; m++) mesesYtdSet.add(m);

    const groups = new Map();

    for (let i = 0; i < DB.rows.length; i++) {
      const row = DB.rows[i];
      const ano = row[0], mes = row[1], eIdx = row[2];
      if (empSet && !empSet.has(DB.emp_list[eIdx])) continue;

      const inAnos = anosSet.has(ano);
      const inMeses = mesesSet.has(mes);
      const inYtd = mesesYtdSet.has(mes);
      const isMom = (ano === anoMom && mes === mesMom);
      const isYoy = (ano === anoYoy);

      if (!((inAnos && inYtd) || (isYoy && inYtd) || isMom)) continue;

      const bIdx = row[3], tIdx = row[4], dIdx = row[5];
      const orc = row[6], real = row[7];
      const key = `${bIdx}|${tIdx}|${dIdx}`;
      let g = groups.get(key);
      if (!g) {
        g = {
          bloco: DB.blocos[bIdx],
          titulo: DB.titulos[tIdx],
          descrnat: DB.descrnats[dIdx],
          realizado: 0, orcado: 0, real_mom: 0, orc_mom: 0,
          real_yoy: 0, real_ytd: 0, real_ytd_ant: 0
        };
        groups.set(key, g);
      }

      if (inAnos && inMeses) { g.realizado += real; g.orcado += orc; }
      if (isMom) { g.real_mom += real; g.orc_mom += orc; }
      if (isYoy && inMeses) { g.real_yoy += real; }
      if (inAnos && inYtd) { g.real_ytd += real; }
      if (isYoy && inYtd) { g.real_ytd_ant += real; }
    }

    const sortedRows = Array.from(groups.values()).sort((a, b) => {
      if (a.bloco !== b.bloco) return a.bloco.localeCompare(b.bloco);
      if (a.titulo !== b.titulo) return a.titulo.localeCompare(b.titulo);
      return a.descrnat.localeCompare(b.descrnat);
    });

    let bonifTotal = 0;
    const blocosMap = new Map();

    for (const r of sortedRows) {
      if (r.titulo && r.titulo.toLowerCase().includes("bonif")) {
        bonifTotal += r.realizado;
      }
      if (Math.abs(r.realizado) < 0.001 && Math.abs(r.orcado) < 0.001 &&
          Math.abs(r.real_mom) < 0.001 && Math.abs(r.orc_mom) < 0.001 &&
          Math.abs(r.real_ytd) < 0.001 && Math.abs(r.real_yoy) < 0.001 &&
          Math.abs(r.real_ytd_ant) < 0.001) continue;

      let bd = blocosMap.get(r.bloco);
      if (!bd) {
        bd = {
          bloco: r.bloco, realizado: 0, orcado: 0, real_mom: 0, orc_mom: 0,
          real_yoy: 0, real_ytd: 0, real_ytd_ant: 0, titulos: new Map()
        };
        blocosMap.set(r.bloco, bd);
      }
      let td = bd.titulos.get(r.titulo);
      if (!td) {
        td = {
          titulo: r.titulo, realizado: 0, orcado: 0, real_mom: 0, orc_mom: 0,
          real_yoy: 0, real_ytd: 0, real_ytd_ant: 0, linhas: []
        };
        bd.titulos.set(r.titulo, td);
      }
      td.linhas.push({
        descr: r.descrnat, realizado: r.realizado, orcado: r.orcado,
        real_mom: r.real_mom, orc_mom: r.orc_mom, real_yoy: r.real_yoy,
        real_ytd: r.real_ytd, real_ytd_ant: r.real_ytd_ant
      });
      td.realizado += r.realizado; td.orcado += r.orcado;
      td.real_mom += r.real_mom; td.orc_mom += r.orc_mom;
      td.real_yoy += r.real_yoy; td.real_ytd += r.real_ytd; td.real_ytd_ant += r.real_ytd_ant;

      bd.realizado += r.realizado; bd.orcado += r.orcado;
      bd.real_mom += r.real_mom; bd.orc_mom += r.orc_mom;
      bd.real_yoy += r.real_yoy; bd.real_ytd += r.real_ytd; bd.real_ytd_ant += r.real_ytd_ant;
    }

    let vbReal = 0, vbOrc = 0;
    for (const [, bd] of blocosMap.entries()) {
      for (const [tName, td] of bd.titulos.entries()) {
        if (tName.toLowerCase().includes("venda bruta")) {
          vbReal = td.realizado; vbOrc = td.orcado; break;
        }
      }
      if (vbReal) break;
    }
    const vl = blocosMap.get("1.Venda Liquida") || { realizado: 0, orcado: 0, real_mom: 0, orc_mom: 0, real_yoy: 0, real_ytd: 0, real_ytd_ant: 0 };
    const cmv = blocosMap.get("2.Custo Mercadoria Vendida") || { realizado: 0, orcado: 0, real_mom: 0, orc_mom: 0, real_yoy: 0, real_ytd: 0, real_ytd_ant: 0 };
    if (!vbReal) { vbReal = vl.realizado; vbOrc = vl.orcado; }

    const mReal = vl.realizado + cmv.realizado;
    const mOrc = vl.orcado + cmv.orcado;
    const mRealMom = vl.real_mom + cmv.real_mom;
    const mOrcMom = vl.orc_mom + cmv.orc_mom;
    const mYoy = vl.real_yoy + cmv.real_yoy;
    const mYtd = vl.real_ytd + cmv.real_ytd;
    const mYtdAnt = vl.real_ytd_ant + cmv.real_ytd_ant;

    const isMultiMes = meses.length > 1;
    const result = [];

    if (blocosMap.size > 0) {
      result.push({
        bloco: "MARGEM DE CONTRIBUIÇÃO", is_total: true, is_despesa: false,
        realizado: mReal, orcado: mOrc, real_mom: mRealMom, orc_mom: mOrcMom, real_ytd: mYtd,
        mom: !isMultiMes ? calcVar(mReal, mRealMom, false) : null,
        yoy: calcVar(mReal, mYoy, false),
        ytd_yoy: calcVar(mYtd, mYtdAnt, false),
        pct_real: pct(mReal, vbReal), pct_orc: pct(mOrc, vbOrc),
        ro: calcRo(mReal, mOrc), titulos: []
      });

      const despBlocos = [
        "3.Despesas com Vendas", "4.Despesas Comercial Operacional",
        "5.Despesas Administrativa Operacional", "6.Receitas/Despesas Financeiras", "7.Vendas IC"
      ];
      let m2Real = mReal, m2Orc = mOrc, m2Ytd = mYtd, m2RealMom = mRealMom, m2OrcMom = mOrcMom, m2Yoy = mYoy, m2YtdAnt = mYtdAnt;
      for (const dk of despBlocos) {
        const bd2 = blocosMap.get(dk);
        if (bd2) {
          m2Real += bd2.realizado; m2Orc += bd2.orcado; m2Ytd += bd2.real_ytd;
          m2RealMom += bd2.real_mom; m2OrcMom += bd2.orc_mom;
          m2Yoy += bd2.real_yoy; m2YtdAnt += bd2.real_ytd_ant;
        }
      }
      result.push({
        bloco: "MARGEM", is_total: true, is_despesa: false,
        realizado: m2Real, orcado: m2Orc, real_mom: m2RealMom, orc_mom: m2OrcMom, real_ytd: m2Ytd,
        mom: !isMultiMes ? calcVar(m2Real, m2RealMom, false) : null,
        yoy: calcVar(m2Real, m2Yoy, false),
        ytd_yoy: calcVar(m2Ytd, m2YtdAnt, false),
        pct_real: pct(m2Real, vbReal), pct_orc: pct(m2Orc, vbOrc),
        ro: calcRo(m2Real, m2Orc), titulos: []
      });
    }

    for (const [bName, bd] of blocosMap.entries()) {
      const isDespB = isCostOrExpense(bName);
      const titulosOut = [];
      for (const [tName, td] of bd.titulos.entries()) {
        const isDespT = isCostOrExpense(bName, tName);
        const linhasOut = td.linhas.map(ln => ({
          descr: ln.descr, realizado: ln.realizado, orcado: ln.orcado,
          real_mom: ln.real_mom, orc_mom: ln.orc_mom, real_ytd: ln.real_ytd,
          is_despesa: isDespT,
          mom: !isMultiMes ? calcVar(ln.realizado, ln.real_mom, isDespT) : null,
          yoy: calcVar(ln.realizado, ln.real_yoy, isDespT),
          ytd_yoy: calcVar(ln.real_ytd, ln.real_ytd_ant, isDespT),
          pct_real: pct(ln.realizado, vbReal), pct_orc: pct(ln.orcado, vbOrc),
          ro: calcRo(ln.realizado, ln.orcado)
        }));
        titulosOut.push({
          titulo: tName, realizado: td.realizado, orcado: td.orcado,
          real_mom: td.real_mom, orc_mom: td.orc_mom, real_ytd: td.real_ytd,
          is_despesa: isDespT,
          mom: !isMultiMes ? calcVar(td.realizado, td.real_mom, isDespT) : null,
          yoy: calcVar(td.realizado, td.real_yoy, isDespT),
          ytd_yoy: calcVar(td.real_ytd, td.real_ytd_ant, isDespT),
          pct_real: pct(td.realizado, vbReal), pct_orc: pct(td.orcado, vbOrc),
          ro: calcRo(td.realizado, td.orcado), linhas: linhasOut
        });
      }
      result.push({
        bloco: bName, realizado: bd.realizado, orcado: bd.orcado,
        real_mom: bd.real_mom, orc_mom: bd.orc_mom, real_ytd: bd.real_ytd,
        is_despesa: isDespB,
        mom: !isMultiMes ? calcVar(bd.realizado, bd.real_mom, isDespB) : null,
        yoy: calcVar(bd.realizado, bd.real_yoy, isDespB),
        ytd_yoy: calcVar(bd.real_ytd, bd.real_ytd_ant, isDespB),
        pct_real: pct(bd.realizado, vbReal), pct_orc: pct(bd.orcado, vbOrc),
        ro: calcRo(bd.realizado, bd.orcado), titulos: titulosOut
      });
    }

    return { dre: result, bonif_total: bonifTotal };
  }

  function handleMensal(params) {
    const anos = new Set(parseIntList(params.get("ano"), [2026]));
    const emps = parseStrList(params.get("emp"));
    const empSet = emps.length ? new Set(emps) : null;
    const fBloco = params.get("bloco") || null;
    const fTitulo = params.get("titulo") || null;
    const fDescr = params.get("descrnat") || null;

    const groups = new Map();
    for (let i = 0; i < DB.rows.length; i++) {
      const row = DB.rows[i];
      const ano = row[0], mes = row[1], eIdx = row[2];
      if (!anos.has(ano)) continue;
      if (empSet && !empSet.has(DB.emp_list[eIdx])) continue;

      const bName = DB.blocos[row[3]];
      const tName = DB.titulos[row[4]];
      const dName = DB.descrnats[row[5]];

      if (fDescr && dName !== fDescr) continue;
      if (fTitulo && tName !== fTitulo) continue;
      if (fBloco && fBloco.toUpperCase() !== "MARGEM DE CONTRIBUIÇÃO" && bName !== fBloco) continue;

      const key = `${mes}|${bName}`;
      let g = groups.get(key);
      if (!g) {
        g = { MES: mes, BLOCO: bName, REALIZADO: 0, ORCADO: 0 };
        groups.set(key, g);
      }
      g.ORCADO += row[6];
      g.REALIZADO += row[7];
    }

    const out = Array.from(groups.values()).sort((a, b) => a.MES - b.MES || a.BLOCO.localeCompare(b.BLOCO));
    return { mensal: out };
  }

  function handleTabelaAcumulado(params) {
    const anos = parseIntList(params.get("ano"), [2026]);
    const meses = parseIntList(params.get("mes"), [9]);
    const emps = parseStrList(params.get("emp"));
    const empSet = emps.length ? new Set(emps) : null;
    const modo = (params.get("modo") || "mensal").toLowerCase();

    const anoVal = anos[0] || 2026;
    const mesVal = Math.max(...meses);
    const mesesSet = new Set(meses);

    const groups = new Map();
    for (let i = 0; i < DB.rows.length; i++) {
      const row = DB.rows[i];
      const ano = row[0], mes = row[1], eIdx = row[2];
      if (ano !== anoVal) continue;
      if (modo === "acumulado" ? (mes > mesVal) : !mesesSet.has(mes)) continue;
      if (empSet && !empSet.has(DB.emp_list[eIdx])) continue;

      const bName = DB.blocos[row[3]];
      const tName = DB.titulos[row[4]];
      const key = `${bName}|${tName}`;
      let g = groups.get(key);
      if (!g) {
        g = { bloco: bName, titulo: tName, orcado: 0, realizado: 0 };
        groups.set(key, g);
      }
      g.orcado += row[6];
      g.realizado += row[7];
    }

    const map = {};
    for (const g of groups.values()) {
      if (!map[g.bloco]) map[g.bloco] = [];
      map[g.bloco].push({
        titulo: g.titulo, orcado: g.orcado, realizado: g.realizado,
        dif: g.realizado - g.orcado,
        pct: Math.abs(g.orcado) > 0.001 ? ((g.realizado - g.orcado) / Math.abs(g.orcado) * 100) : 0
      });
    }

    return { ano: anoVal, mes: mesVal, modo: modo, grupos: map };
  }

  function handleTabelaMensal(params) {
    const anos = parseIntList(params.get("ano"), [2026]);
    const meses = parseIntList(params.get("mes"), [8]);
    const emps = parseStrList(params.get("emp"));
    const empSet = emps.length ? new Set(emps) : null;
    const soAmbos = (params.get("so_ambos") || "true").toLowerCase() !== "false";

    const anoVal = anos[0] || 2026;
    const mesesSet = new Set(meses);

    const cDict = new Map();
    for (let i = 0; i < DB.cenc_rows.length; i++) {
      const r = DB.cenc_rows[i];
      if (r[0] !== anoVal || !mesesSet.has(r[1])) continue;
      if (empSet && !empSet.has(DB.emp_list[r[2]])) continue;

      const cNome = DB.descrcencs[r[4]];
      const bNome = DB.blocos[r[5]];
      let ci = cDict.get(cNome);
      if (!ci) {
        ci = { nome: cNome, orcado: 0, realizado: 0, bMap: new Map() };
        cDict.set(cNome, ci);
      }
      ci.orcado += r[6]; ci.realizado += r[7];
      let bi = ci.bMap.get(bNome);
      if (!bi) { bi = { bloco: bNome, orcado: 0, realizado: 0 }; ci.bMap.set(bNome, bi); }
      bi.orcado += r[6]; bi.realizado += r[7];
    }

    const centrosList = [];
    let totOrc = 0, totReal = 0;
    for (const ci of cDict.values()) {
      if (soAmbos ? (Math.abs(ci.orcado) < 0.01 || Math.abs(ci.realizado) < 0.01) : (Math.abs(ci.orcado) < 0.01 && Math.abs(ci.realizado) < 0.01)) continue;
      totOrc += ci.orcado; totReal += ci.realizado;
      const blocos = Array.from(ci.bMap.values()).map(b => ({
        bloco: b.bloco, orcado: b.orcado, realizado: b.realizado,
        dif: b.realizado - b.orcado,
        pct: Math.abs(b.orcado) > 0.001 ? ((b.realizado - b.orcado) / Math.abs(b.orcado) * 100) : 0
      }));
      centrosList.push({
        nome: ci.nome, orcado: ci.orcado, realizado: ci.realizado,
        dif: ci.realizado - ci.orcado,
        pct: Math.abs(ci.orcado) > 0.001 ? ((ci.realizado - ci.orcado) / Math.abs(ci.orcado) * 100) : 0,
        blocos: blocos
      });
    }
    centrosList.sort((a, b) => b.realizado - a.realizado);

    return {
      ano: anoVal, mes: Math.max(...meses),
      total: {
        nome: "TOTAL CENTROS DE RESULTADO", orcado: totOrc, realizado: totReal,
        dif: totReal - totOrc, pct: Math.abs(totOrc) > 0.001 ? ((totReal - totOrc) / Math.abs(totOrc) * 100) : 0
      },
      centros: centrosList
    };
  }

  const origFetch = window.fetch.bind(window);
  window.fetch = async function(input, init) {
    const rawUrl = typeof input === "string" ? input : (input && input.url ? input.url : "");
    if (rawUrl) {
      const u = new URL(rawUrl, window.location.href);
      const path = u.pathname;
      const params = u.searchParams;

      if (path.endsWith("/api/filtros")) {
        return new Response(JSON.stringify(handleFiltros()), {
          status: 200, headers: { "Content-Type": "application/json" }
        });
      }
      if (path.endsWith("/api/dre") && !path.includes("mensal") && !path.includes("acumulado")) {
        return new Response(JSON.stringify(handleDre(params)), {
          status: 200, headers: { "Content-Type": "application/json" }
        });
      }
      if (path.endsWith("/api/dre/mensal")) {
        return new Response(JSON.stringify(handleMensal(params)), {
          status: 200, headers: { "Content-Type": "application/json" }
        });
      }
      if (path.endsWith("/api/dre/tabela-acumulado")) {
        return new Response(JSON.stringify(handleTabelaAcumulado(params)), {
          status: 200, headers: { "Content-Type": "application/json" }
        });
      }
      if (path.endsWith("/api/dre/tabela-mensal")) {
        return new Response(JSON.stringify(handleTabelaMensal(params)), {
          status: 200, headers: { "Content-Type": "application/json" }
        });
      }
    }
    return origFetch(input, init);
  };
})();
"""


def build_dre_empresa_standalone():
    print("1. Extraindo dados do DRE Consolidado Empresa (Whitelabel / Portfolio)...")
    data = extract_dre_empresa_data()
    print(f"   -> {len(data['rows'])} linhas por empresa | {len(data['cenc_rows'])} linhas por centro")

    out_dir = os.path.join(PORTFOLIO_DIR, "dre_empresa")
    os.makedirs(os.path.join(out_dir, "static", "css"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "static", "js"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "static", "assets"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "static", "img"), exist_ok=True)

    for css_f in ["tokens.css", "base.css", "components.css", "style.css", "responsive.css"]:
        src = os.path.join(DRE_EMP_DIR, "static", "css", css_f)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(out_dir, "static", "css", css_f))

    shutil.copy2(os.path.join(DRE_EMP_DIR, "static", "js", "app.js"), os.path.join(out_dir, "static", "js", "app.js"))

    avatar_src = os.path.join(DRE_EMP_DIR, "static", "img", "ai_avatar.png")
    if os.path.exists(avatar_src):
        shutil.copy2(avatar_src, os.path.join(out_dir, "static", "img", "ai_avatar.png"))

    tpl = open(os.path.join(DRE_EMP_DIR, "templates", "index.html"), "r", encoding="utf-8").read()
    html = re.sub(r"\{\{\s*url_for\('static',\s*filename='([^']+)'\)\s*\}\}", r"static/\1", tpl)
    html = html.replace('href="http://localhost:5080/portal"', 'href="../index.html"')
    html = html.replace('<span>Portal Intranet</span>', '<span>Voltar ao Portfólio</span>')

    # Remove qualquer conotação à MQ Hair Company no HTML
    html = html.replace('<title>DRE Empresa — MQ Hair</title>', '<title>DRE Consolidado — Demonstrativo de Resultado</title>')
    html = html.replace('Demonstrativo de Resultado do Exercício por Empresa MQ Hair — Realizado vs Orçado por centro de custo e empresa.', 'Demonstrativo de Resultado do Exercício Consolidado — Realizado vs Orçado por centro de resultado.')
    html = html.replace('Portal Corporativo • DRE Empresa', 'Portfólio Executivo • DRE Consolidado')
    html = html.replace('MQ PROFESSIONAL &bull; <span>DRE EMPRESA</span>', 'EXECUTIVE ANALYTICS &bull; <span>DRE CONSOLIDADO</span>')
    html = html.replace('<span>Desenvolvido por <strong>BI MQ Hair Company</strong></span>', '<span>Desenvolvido por <strong>Antonio Mello | BI Architecture</strong></span>')
    html = html.replace('Pesquisar conta (ex: Frete, Amazon, Parlux)...', 'Pesquisar conta (ex: Frete, Marketing, Logística)...')

    # Substituir Logo MQ Hair Company por Marca Executiva Limpa
    mq_logo_pattern = r'<div class="header-logo-box">.*?</div>'
    clean_logo_replacement = (
        '<div class="header-logo-box">\n'
        '        <a href="../index.html" title="Voltar ao Portfólio" style="text-decoration: none;">\n'
        '          <div style="font-family: \'Montserrat\', sans-serif; font-size: 15px; font-weight: 800; color: #fff; letter-spacing: 0.5px; display: flex; align-items: center; gap: 8px;">\n'
        '            <span style="color: var(--brand-secondary-dourado, #cb9727); font-size: 18px;">✦</span>\n'
        '            <span>EXECUTIVE <strong>ANALYTICS</strong></span>\n'
        '          </div>\n'
        '        </a>\n'
        '      </div>'
    )
    html = re.sub(mq_logo_pattern, clean_logo_replacement, html, flags=re.DOTALL)

    # Tirar o filtro Empresa (ocultar com display: none para não quebrar app.js)
    html = html.replace(
        '<div class="filtro-group filtro-empresa filter-field">',
        '<div class="filtro-group filtro-empresa filter-field" style="display: none !important;">'
    )

    # Renomear Filtro Centro de Custo para Centro de Resultado
    html = html.replace(
        '<label class="filter-label" style="color: #ffffff !important; font-weight: 700;">Centro de Custo</label>',
        '<label class="filter-label" style="color: #ffffff !important; font-weight: 700;">Centro de Resultado</label>'
    )
    html = html.replace('title="Clique para selecionar um ou mais Centros de Custo"', 'title="Clique para selecionar Centros de Resultado"')
    html = html.replace('Todos os Centros', 'Todos os Centros de Resultado')
    html = html.replace('Buscar centro...', 'Buscar centro de resultado...')
    html = html.replace('Carregando centros…', 'Carregando centros de resultado…')

    html = html.replace(
        '<script src="static/js/app.js?v=20261019_no_ytd"></script>',
        '<script src="static/js/dre_empresa_data.js?v=20261030_whitelabel"></script>\n'
        '<script src="static/js/dre_empresa_engine.js?v=20261030_whitelabel"></script>\n'
        '<script src="static/js/app.js?v=20261030_whitelabel"></script>'
    )

    with open(os.path.join(out_dir, "static", "js", "dre_empresa_data.js"), "w", encoding="utf-8") as f:
        f.write("window.__DRE_EMPRESA_DB__ = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n")

    with open(os.path.join(out_dir, "static", "js", "dre_empresa_engine.js"), "w", encoding="utf-8") as f:
        f.write(JS_ENGINE)

    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    print(f"2. DRE Consolidado Empresa whitelabel gerado com sucesso em: {out_dir}")


if __name__ == "__main__":
    build_dre_empresa_standalone()
