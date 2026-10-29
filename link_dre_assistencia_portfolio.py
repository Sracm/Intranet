import os
import re
import json

INTRANET_DIR = r"c:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\ANTIGRAVITY\PROJETOS\INTRANET"
PORTFOLIO_HTML = os.path.join(INTRANET_DIR, "portfolio_standalone", "index.html")
TPL_PORTFOLIO_HTML = os.path.join(INTRANET_DIR, "templates", "portfolio.html")
DATASET_JSON = os.path.join(INTRANET_DIR, "portfolio_final_dataset.json")

# Mapeamento EXCLUSIVO para o Portfólio Online (sracm.github.io/portfolio-bi) e /portfolio:
# Apenas os dashboards que estão no GitHub (Dre_Empresa, dre_gestores, dashboard-tv, dashboard-diretoria-ecommerce)
# ganham versão web interativa no Portfólio. Os demais cards permanecem exatamente como estavam.
GITHUB_PORTFOLIO_DASH_MAP = {
    # 1. Repositório: https://github.com/Sracm/Dre_Empresa
    25: "dre_empresa/index.html",

    # 2. Repositório: https://github.com/Sracm/dre_gestores
    24: "dre_assistencia/index.html?regional=assistencia",
    28: "dre_assistencia/index.html?regional=geral",
    13: "dre_assistencia/index.html?regional=geral",
    22: "dre_assistencia/index.html?regional=comex",
    69: "dre_assistencia/index.html?regional=produto",
    18: "dre_assistencia/index.html?regional=ecommerce",
    20: "dre_assistencia/index.html?regional=logistica",
    14: "dre_assistencia/index.html?regional=rh",
    12: "dre_assistencia/index.html?regional=regional.fsp",
    23: "dre_assistencia/index.html?regional=regional-sp",

    # 3. Repositório: https://github.com/Sracm/dashboard-diretoria-ecommerce
    48: "ecommerce/index.html",
}

def fix_mojibake(s):
    if not isinstance(s, str):
        return s
    try:
        return s.encode("latin1").decode("utf-8")
    except Exception:
        repls = {
            "Ã£": "ã", "Ã¡": "á", "Ã¢": "â", "Ã ": "à",
            "Ã©": "é", "Ãª": "ê", "Ã­": "í", "Ã³": "ó",
            "Ã´": "ô", "Ãµ": "õ", "Ãº": "ú", "Ã§": "ç",
            "Ãƒ": "Ã", "Ã‡": "Ç", "Ã‰": "É", "Ã“": "Ó",
            "â€”": "—", "â€“": "–", "â€¢": "•"
        }
        for k, v in repls.items():
            s = s.replace(k, v)
        return s

def update_portfolio_files():
    txt = open(PORTFOLIO_HTML, "r", encoding="utf-8").read()
    match = re.search(r"const DASHBOARDS = (\[.*?\]);", txt, flags=re.DOTALL)
    if not match:
        raise RuntimeError("DASHBOARDS array not found in portfolio_standalone/index.html")

    dashs = json.loads(match.group(1))
    dashs = [
        d for d in dashs
        if d.get("id") not in (6, 48, 70, 72, 78) and fix_mojibake(d.get("title", "")).strip().lower() not in (
            "acompanhamento de obrigações fiscais e sped",
            "análise de recorrência & recompra de clientes",
            "dir. assistec. dashboard forecast spare_parts vs05",
            "teste preditivos.",
            "dir.cml ecommerce.vs 7.1",
            "portal corporativo • e-commerce",
        )
    ]

    # Garante a presença do card MQ Professional — Painel Executivo E-commerce na guia E-commerce
    ecom_card = {
        "id": 48,
        "title": "MQ Professional — Painel Executivo E-commerce",
        "department": "E-commerce",
        "description": "Painel Executivo de Performance E-commerce: evolução diária acumulada (Meta vs Realizado), projeção de fechamento e indicadores por canal (Total E-commerce, Mercado Livre, VTEX e Shopee).",
        "url": "ecommerce/index.html",
        "tech": "Fullstack Flask / Python / SQL",
        "stack": ["Python 3", "Flask", "SQL (Oracle/MariaDB)", "HTML5/CSS3 Moderno", "Chart.js", "JavaScript"],
        "impact": "Solução web sob medida desenvolvida para automação em tempo real, sem custo de licença por usuário.",
        "image": "static/portfolio_screenshots/dash_48_portal_corporativo_____e-commerce.jpg?v=20261028_reab",
        "github_repo": "https://github.com/Sracm/dashboard-diretoria-ecommerce",
        "is_static": False,
        "live_url": "ecommerce/index.html",
    }
    # Insere no início da seção E-commerce
    ecom_idx = next((i for i, d in enumerate(dashs) if fix_mojibake(d.get("department", "")) == "E-commerce"), len(dashs))
    dashs.insert(ecom_idx, ecom_card)

    for d in dashs:
        d["title"] = fix_mojibake(d.get("title", ""))
        if d.get("id") == 73:
            d["title"] = "DASHBOARD RA"
        d["description"] = fix_mojibake(d.get("description", ""))
        d["department"] = fix_mojibake(d.get("department", ""))
        d["tech"] = fix_mojibake(d.get("tech", ""))
        d["impact"] = fix_mojibake(d.get("impact", ""))
        if d.get("image"):
            base_img = d["image"].split("?")[0]
            d["image"] = f"{base_img}?v=20261028_reab"

        did = d.get("id")
        url_tv = d.get("url_tv")

        # Limpa qualquer propriedade extra adicionada antes
        d.pop("local_url", None)

        if did in GITHUB_PORTFOLIO_DASH_MAP:
            live_u = GITHUB_PORTFOLIO_DASH_MAP[did]
            d["live_url"] = live_u
            d["url"] = live_u
            d["is_static"] = False
        elif url_tv:
            # 4. Repositório: https://github.com/Sracm/dashboard-tv (19 telas)
            fname = url_tv.lstrip("/").replace("/", "_") + ".html"
            live_u = f"dashboard_tv/{fname}"
            d["live_url"] = live_u
            d["url"] = live_u
            d["is_static"] = False
        else:
            # Todos os demais cards permanecem no modo galeria estática
            d["live_url"] = None
            d["github_repo"] = None
            d["url"] = "#"
            d["is_static"] = True

    new_json_str = json.dumps(dashs, ensure_ascii=False)
    txt = txt[:match.start(1)] + new_json_str + txt[match.end(1):]

    # Remove o botão "Ver Tela" no rodapé inferior de cada card, deixando apenas "Abrir Dashboard" quando aplicável
    pattern_footer = re.compile(
        r'<div class="card-action"[^>]*>\s*<button[^>]*>\s*<i[^>]*></i>\s*Ver Tela\s*</button>\s*\$\{targetDashUrl \? `.*?` : \'\'\}\s*</div>',
        re.S,
    )
    new_footer = """${targetDashUrl ? `
              <div class="card-action" style="display: flex; gap: 8px; width: 100%;">
                <a href="${targetDashUrl}" target="_blank" rel="noopener" class="btn-card btn-card-primary" style="flex: 1; text-decoration: none; border-radius: 6px; padding: 8px 6px; font-weight: 700; font-size: 0.74rem; display: flex; align-items: center; justify-content: center; gap: 6px;">
                  <i class="fa-solid fa-chart-line"></i> Abrir Dashboard
                </a>
              </div>
              ` : ''}"""
    txt = pattern_footer.sub(new_footer, txt)
    txt = txt.replace("ANDERSON MELLO", "ANTONIO MELLO").replace("Anderson Mello", "Antonio Mello")
    txt = re.sub(
        r'<div class="brand-logo">.*?</div>\s*</div>',
        '<div class="brand-logo">\n      <div class="brand-title">Antonio Mello <span>Business Intelligence</span></div>\n    </div>',
        txt,
        count=1,
        flags=re.S,
    )
    txt = re.sub(
        r'<div class="hero-tag">.*?</div>',
        '<div class="hero-tag">Visão completa, controle total.</div>',
        txt,
        count=1,
        flags=re.S,
    )
    txt = re.sub(
        r'<h1[^>]*>.*?</h1>',
        '<h1 style="color: #FFFFFF;">Cockpit Executivo Estratégico</h1>',
        txt,
        count=1,
        flags=re.S,
    )
    txt = txt.replace("<div class=\"stat-label\">Automação & Real-time</div>", "<div class=\"stat-label\">Automação</div>")
    txt = re.sub(
        r'\s*<div class="stat-card">\s*<div class="stat-number">0</div>\s*<div class="stat-label">Custo Licença em Módulos Web</div>\s*</div>',
        '',
        txt,
        flags=re.S,
    )
    txt = re.sub(r'\s*<a href="/portfolio/download-pdf"[^>]*>.*?Baixar PDF\s*</a>', '', txt, flags=re.S)
    txt = txt.replace("Baixar PPTX Editável", "Baixar")
    txt = txt.replace("fa-file-powerpoint", "fa-file-pdf")
    txt = txt.replace('title="Baixar PowerPoint editável com as telas"', 'title="Baixar PDF com as telas"')
    txt = re.sub(
        r'href="[^"]*\.(pptx|pdf)"(\s+download="[^"]*")?',
        'href="/static/Portfolio_Antonio_Mello_BI_Executive.pdf" download="Portfolio_Antonio_Mello_BI_Executive.pdf"',
        txt,
    )
    txt_standalone = txt.replace(
        'href="/static/Portfolio_Antonio_Mello_BI_Executive.pdf"',
        'href="https://sracm.github.io/portfolio-bi/Portfolio_Antonio_Mello_BI_Executive.pdf"',
    )

    with open(PORTFOLIO_HTML, "w", encoding="utf-8") as f:
        f.write(txt_standalone)

    with open(DATASET_JSON, "w", encoding="utf-8") as f:
        json.dump(dashs, f, ensure_ascii=False, indent=2)

    with open(TPL_PORTFOLIO_HTML, "w", encoding="utf-8") as f:
        f.write(txt)

    # Atualiza create_portfolio_pptx.py para ignorar ?v=... no caminho da imagem e gera o arquivo .pptx
    pptx_script = os.path.join(INTRANET_DIR, "create_portfolio_pptx.py")
    if os.path.exists(pptx_script):
        c_pptx = open(pptx_script, "r", encoding="utf-8").read()
        c_pptx = c_pptx.replace("dash.get('image', '').lstrip('/')", "dash.get('image', '').split('?')[0].lstrip('/')")
        c_pptx = c_pptx.replace('("100%", "Automação Real-time"),\n        ("0", "Custo Licença em Web Apps")', '("100%", "Automação")')
        c_pptx = c_pptx.replace('("100%", "Automação Real-time"),\r\n        ("0", "Custo Licença em Web Apps")', '("100%", "Automação")')
        c_pptx = c_pptx.replace('tb_badge.text = "EXECUTIVE BI PORTFOLIO"', 'tb_badge.text = "VISÃO COMPLETA, CONTROLE TOTAL."')
        c_pptx = c_pptx.replace('p1.text = "Portfólio de Business Intelligence"', 'p1.text = "Cockpit Executivo Estratégico"')
        open(pptx_script, "w", encoding="utf-8").write(c_pptx)
        from create_portfolio_pptx import create_portfolio_powerpoint
        import shutil
        out_pptx = os.path.join(INTRANET_DIR, "portfolio_standalone", "Portfolio_Antonio_Mello_BI_Executive.pptx")
        create_portfolio_powerpoint(dataset_path=DATASET_JSON, output_pptx=out_pptx)
        shutil.copy2(out_pptx, os.path.join(INTRANET_DIR, "static", "Portfolio_Antonio_Mello_BI_Executive.pptx"))
        shutil.copy2(out_pptx, os.path.join(INTRANET_DIR, "static", "Portfolio_Anderson_Mello_BI_Executive.pptx"))

    pdf_script = os.path.join(INTRANET_DIR, "generate_portfolio_pdf.py")
    if os.path.exists(pdf_script):
        c_pdf = open(pdf_script, "r", encoding="utf-8").read()
        c_pdf = c_pdf.replace("ANDERSON MELLO", "ANTONIO MELLO").replace("Anderson Mello", "Antonio Mello")
        c_pdf = c_pdf.replace("Executive BI Portfolio", "Visão completa, controle total.")
        c_pdf = c_pdf.replace("Portfólio de <span>Business Intelligence</span> & Engenharia de Dados", "Cockpit Executivo Estratégico")
        open(pdf_script, "w", encoding="utf-8").write(c_pdf)
        from generate_portfolio_pdf import generate_portfolio_pdf
        import shutil
        out_pdf = os.path.join(INTRANET_DIR, "portfolio_standalone", "Portfolio_Antonio_Mello_BI_Executive.pdf")
        generate_portfolio_pdf(dataset_path=DATASET_JSON, output_pdf_path=out_pdf)
        shutil.copy2(out_pdf, os.path.join(INTRANET_DIR, "static", "Portfolio_Antonio_Mello_BI_Executive.pdf"))
        shutil.copy2(out_pdf, os.path.join(INTRANET_DIR, "static", "portfolio_anderson_mello.pdf"))

    print("Portfólio atualizado com sucesso!")

if __name__ == "__main__":
    update_portfolio_files()
