import os
import json
import shutil
import re
import urllib.request

ECOM_DIR = r"c:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\ANTIGRAVITY\PROJETOS\Dir.Ecommerce"
TV_DIR = r"c:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\ANTIGRAVITY\PROJETOS\DASHBOARD_tv"
INTRANET_DIR = r"c:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\ANTIGRAVITY\PROJETOS\INTRANET"
PORTFOLIO_DIR = os.path.join(INTRANET_DIR, "portfolio_standalone")

def fetch_json(url, timeout=30):
    try:
        req = urllib.request.urlopen(url, timeout=timeout)
        return json.loads(req.read().decode("utf-8"))
    except Exception as e:
        print(f"   [WARN] Falha em {url}: {e}")
        return None


def build_ecommerce_standalone():
    print("1. Construindo E-commerce standalone para o Portfólio...")
    out_dir = os.path.join(PORTFOLIO_DIR, "ecommerce")
    os.makedirs(os.path.join(out_dir, "static", "css"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "static", "js"), exist_ok=True)
    os.makedirs(os.path.join(out_dir, "static", "assets"), exist_ok=True)

    # Copia estáticos
    shutil.copy2(os.path.join(ECOM_DIR, "static", "css", "style.css"), os.path.join(out_dir, "static", "css", "style.css"))
    for js_f in ["app.js", "chart.umd.min.js", "lucide.min.js"]:
        src = os.path.join(ECOM_DIR, "static", "js", js_f)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(out_dir, "static", "js", js_f))
    svg_src = os.path.join(ECOM_DIR, "static", "assets", "a2ae7eaafd5d53c3ac8f9dcc3513af5c8beb9482.svg")
    if os.path.exists(svg_src):
        shutil.copy2(svg_src, os.path.join(out_dir, "static", "assets", "a2ae7eaafd5d53c3ac8f9dcc3513af5c8beb9482.svg"))

    # Captura respostas reais da API local :5200 para os meses principais de 2026
    resumo_map = {}
    from datetime import datetime
    hoje = datetime.now()
    for m in [8, 9, 10]:
        dfim = hoje.day if m == hoje.month else (30 if m in (4, 6, 9, 11) else 31)
        data = fetch_json(f"http://localhost:5200/api/resumo?anos=2026&meses={m}&dia_ini=1&dia_fim={dfim}&marca=Todas&force=true")
        if data and data.get("status") == "success":
            resumo_map[f"2026_{m}_Todas"] = data
            print(f"   -> Capturado E-commerce 2026/{m} (dia 1 até {dfim})")

    default_key = "2026_10_Todas" if "2026_10_Todas" in resumo_map else (list(resumo_map.keys())[0] if resumo_map else None)

    ecom_engine = """// ============================================================================
// E-COMMERCE — STANDALONE ENGINE (GitHub Pages / Portfólio)
// ============================================================================
(function() {
  const DB = window.__ECOM_DB__ || {};
  const DEFAULT_DATA = DB[window.__ECOM_DEFAULT_KEY__] || Object.values(DB)[0] || { status: "success" };

  const origFetch = window.fetch.bind(window);
  window.fetch = async function(input, init) {
    const rawUrl = typeof input === "string" ? input : (input && input.url ? input.url : "");
    if (rawUrl.includes("/api/resumo")) {
      const u = new URL(rawUrl, window.location.origin);
      const anos = u.searchParams.get("anos") || "2026";
      const meses = u.searchParams.get("meses") || "10";
      const marca = u.searchParams.get("marca") || "Todas";
      const key = `${anos}_${meses}_${marca}`;
      const fallbackKey = `2026_${meses.split(",")[0]}_Todas`;
      const payload = DB[key] || DB[fallbackKey] || DEFAULT_DATA;
      return new Response(JSON.stringify(payload), {
        status: 200, headers: { "Content-Type": "application/json" }
      });
    }
    if (rawUrl.includes("/api/sincronizar")) {
      return new Response(JSON.stringify({ status: "idle", running: false }), {
        status: 200, headers: { "Content-Type": "application/json" }
      });
    }
    return origFetch(input, init);
  };
})();
"""

    with open(os.path.join(out_dir, "static", "js", "ecom_data.js"), "w", encoding="utf-8") as f:
        f.write(f"window.__ECOM_DEFAULT_KEY__ = {json.dumps(default_key)};\n")
        f.write("window.__ECOM_DB__ = " + json.dumps(resumo_map, ensure_ascii=False, separators=(",", ":")) + ";\n")

    with open(os.path.join(out_dir, "static", "js", "ecom_engine.js"), "w", encoding="utf-8") as f:
        f.write(ecom_engine)

    # Renderiza HTML do localhost:5200 e adapta links para relativo
    req = urllib.request.urlopen("http://localhost:5200/", timeout=60)
    html = req.read().decode("utf-8")
    html = html.replace('href="/static/', 'href="static/')
    html = html.replace('src="/static/', 'src="static/')
    html = html.replace('href="http://localhost:5080/portal"', 'href="../index.html"')
    html = html.replace(
        '<script src="static/js/app.js',
        '<script src="static/js/ecom_data.js?v=20261028"></script>\n'
        '    <script src="static/js/ecom_engine.js?v=20261028"></script>\n'
        '    <script src="static/js/app.js'
    )

    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"   -> E-commerce standalone salvo em: {out_dir}")


def build_dashboard_tv_standalone():
    print("2. Construindo Dashboard TV standalone (todas as 19 telas) para o Portfólio...")
    out_dir = os.path.join(PORTFOLIO_DIR, "dashboard_tv")
    os.makedirs(out_dir, exist_ok=True)

    # Copia toda a pasta static do DASHBOARD_tv (exceto arquivos pesados desnecessários)
    src_static = os.path.join(TV_DIR, "static")
    dst_static = os.path.join(out_dir, "static")
    shutil.copytree(src_static, dst_static, dirs_exist_ok=True)

    # Coleta os JSONs das APIs do servidor local :5050
    tv_api_db = {}
    api_endpoints = [
        "/api/vendas_tv?mes=10&ano=2026",
        "/api/vendas_tv?mes=9&ano=2026",
        "/api/acumulado_tv?ano=2026&mes=10",
        "/api/trimestre_tv?ano=2026&mes=10",
        "/api/canais_trimestre_tv?ano=2026&mes=10",
        "/api/categorias_dados?mes=10&ano=2026",
        "/api/paises_dados?mes=10&ano=2026",
        "/api/mapa_regionais?mes=10&ano=2026",
        "/api/empresa_tv?mes=10&ano=2026",
        "/api/diario_canal?mes=10&ano=2026",
        "/api/diario_marcas?mes=10&ano=2026",
        "/api/teste_estoque",
        "/api/estoque_previsao",
        "/api/estoque",
    ]
    canais_slugs = [
        "distribuicao", "ecommerce_mq", "varejo_sp", "comex",
        "regional_no_nd", "regional_rj_mg_es", "regional_sul"
    ]
    for slug in canais_slugs:
        api_endpoints.append(f"/api/canal_dados?canal={slug}&mes=10&ano=2026")

    for ep in api_endpoints:
        data = fetch_json(f"http://localhost:5050{ep}", timeout=30)
        if data is not None:
            tv_api_db[ep] = data
            # Registra também chave base sem query string como fallback
            base_path = ep.split("?")[0]
            if base_path not in tv_api_db:
                tv_api_db[base_path] = data
            print(f"   -> Capturado TV API: {ep}")

    tv_engine = """// ============================================================================
// DASHBOARD TV — STANDALONE ENGINE (GitHub Pages / Portfólio)
// ============================================================================
(function() {
  const DB = window.__TV_API_DB__ || {};

  // Sobrescreve navigateTab para navegar entre os arquivos HTML estáticos do Portfólio
  window.addEventListener("DOMContentLoaded", () => {
    window.navigateTab = function(path) {
      if (typeof pararTodosAudios === "function") {
        try { pararTodosAudios(); } catch(e) {}
      }
      const clean = path.replace(/^\\//, "").replace(/\\//g, "_");
      const file = (!clean || clean === "tv") ? "tv.html" : `${clean}.html`;
      window.location.href = file;
    };
  });

  const origFetch = window.fetch.bind(window);
  window.fetch = async function(input, init) {
    const rawUrl = typeof input === "string" ? input : (input && input.url ? input.url : "");
    if (rawUrl.includes("/api/")) {
      const u = new URL(rawUrl, window.location.origin);
      const pathAndQuery = u.pathname + u.search;
      const canal = u.searchParams.get("canal");
      const mes = u.searchParams.get("mes") || "10";
      const ano = u.searchParams.get("ano") || "2026";

      let payload = DB[pathAndQuery];
      if (!payload && canal) {
        payload = DB[`${u.pathname}?canal=${canal}&mes=10&ano=2026`];
      }
      if (!payload) {
        payload = DB[`${u.pathname}?mes=${mes}&ano=${ano}`] ||
                  DB[`${u.pathname}?ano=${ano}&mes=${mes}`] ||
                  DB[`${u.pathname}?mes=10&ano=2026`] ||
                  DB[`${u.pathname}?ano=2026&mes=10`] ||
                  DB[u.pathname];
      }
      if (payload !== undefined) {
        return new Response(JSON.stringify(payload), {
          status: 200, headers: { "Content-Type": "application/json" }
        });
      }
    }
    return origFetch(input, init);
  };
})();
"""

    with open(os.path.join(out_dir, "static", "js", "tv_data.js"), "w", encoding="utf-8") as f:
        f.write("window.__TV_API_DB__ = " + json.dumps(tv_api_db, ensure_ascii=False, separators=(",", ":")) + ";\n")

    with open(os.path.join(out_dir, "static", "js", "tv_engine.js"), "w", encoding="utf-8") as f:
        f.write(tv_engine)

    # Renderiza as 19 páginas HTML do servidor local :5050 e converte para estático
    tv_pages = [
        "/tv", "/acumulado", "/trimestre", "/todos_canais", "/categorias", "/marcas",
        "/canal/distribuicao", "/canal/ecommerce_mq", "/canal/varejo_sp", "/canal/comex",
        "/canal/regional_no_nd", "/canal/regional_rj_mg_es", "/canal/regional_sul",
        "/mapa_regionais", "/empresa", "/diario_canal", "/diario_marcas", "/paises", "/teste_estoque"
    ]

    for route in tv_pages:
        try:
            req = urllib.request.urlopen(f"http://localhost:5050{route}", timeout=20)
            html = req.read().decode("utf-8")
            html = html.replace('href="/static/', 'href="static/')
            html = html.replace('src="/static/', 'src="static/')
            html = html.replace("'/static/", "'static/")
            html = html.replace('"/static/', '"static/')

            # Injeta tv_data.js e tv_engine.js antes do fechamento do </head>
            inject_scripts = (
                '    <script src="static/js/tv_data.js?v=20261028"></script>\n'
                '    <script src="static/js/tv_engine.js?v=20261028"></script>\n'
                '</head>'
            )
            html = html.replace("</head>", inject_scripts, 1)

            fname = route.lstrip("/").replace("/", "_") + ".html"
            with open(os.path.join(out_dir, fname), "w", encoding="utf-8") as f:
                f.write(html)
            if route == "/tv":
                with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
                    f.write(html)
            print(f"   -> Página TV gerada: {fname}")
        except Exception as e:
            print(f"   [WARN] Erro ao gerar página TV {route}: {e}")


if __name__ == "__main__":
    build_ecommerce_standalone()
    build_dashboard_tv_standalone()

