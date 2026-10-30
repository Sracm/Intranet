import os
import json
import re

INTRANET_DIR = r"C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\ANTIGRAVITY\PROJETOS\INTRANET"
PORTFOLIO_DIR = os.path.join(INTRANET_DIR, "portfolio_standalone")

def sanitize_json_file(file_path):
    if not os.path.exists(file_path):
        return
    print(f"Sanitizing JSON: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    def sanitize_item(item):
        if not isinstance(item, dict):
            return item
        iid = item.get("id")
        title = item.get("title", "")
        desc = item.get("description", "")
        
        # ID 5
        if iid == 5 or "Cockpit Geral de Indicadores Estratégicos MQ" in title:
            item["title"] = "Cockpit Geral de Indicadores Estratégicos"
            item["description"] = "Visão macro corporativa com faturamento acumulado, pedidos totais e metas globais da empresa."
        # ID 263
        if iid == 263 or "Marcas Corporativas" in title:
            item["description"] = "Performance executiva e metas de faturamento por marcas corporativas do grupo."
        # ID 272
        if iid == 272 or "Canal E-commerce MQ" in title:
            item["title"] = "Dashboard TV - Canal E-commerce"
            item["description"] = "Painel em tempo real de vendas e metas do canal E-commerce."
            if "canal_ecommerce_mq.html" in str(item.get("url", "")):
                item["url"] = "dashboard_tv/canal_ecommerce.html"
            if "canal_ecommerce_mq.html" in str(item.get("live_url", "")):
                item["live_url"] = "dashboard_tv/canal_ecommerce.html"
            if item.get("url_tv") == "/canal/ecommerce_mq":
                item["url_tv"] = "/canal/ecommerce"
        # ID 48
        if iid == 48 or "MQ Professional" in title:
            item["title"] = "Painel Executivo E-commerce Multi-Canal"
        # ID 13
        if iid == 13 or "DRE Gestores - Geral" in title:
            item["description"] = "Demonstrativo de Resultados do Exercício Consolidado (Diretoria e Gestores). Acompanhamento de faturamento, custos e margem."
        # ID 31
        if iid == 31 or "DRE MQ.2.1" in title:
            item["title"] = "DRE 2.1 - VAREJO_FORASP_DISTRIBUICAO"

        # General regex cleanup in title and description
        if item.get("title"):
            item["title"] = re.sub(r'\bMQ\s*Hair\s*Company\b', 'Grupo Empresarial', item["title"], flags=re.I)
            item["title"] = re.sub(r'\bMQ\s*Hair\b', 'Empresa', item["title"], flags=re.I)
            item["title"] = re.sub(r'\bMQ\s*Professional\b', 'Executive Analytics', item["title"], flags=re.I)
        if item.get("description"):
            item["description"] = re.sub(r'\bMQ\s*Hair\s*Company\b', 'Grupo Empresarial', item["description"], flags=re.I)
            item["description"] = re.sub(r'\bMQ\s*Hair\b', 'Empresa', item["description"], flags=re.I)
            item["description"] = re.sub(r'\bMQ\s*Professional\b', 'Executive Analytics', item["description"], flags=re.I)
        return item

    if isinstance(data, list):
        data = [sanitize_item(it) for it in data]
    elif isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, list):
                data[k] = [sanitize_item(it) for it in v]

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 1. Sanitize JSON files
for jf in [
    "portfolio_final_dataset.json",
    "dashboards_portfolio_data.json",
    "portfolio_clean_data.json",
    "portfolio_by_department.json"
]:
    sanitize_json_file(os.path.join(INTRANET_DIR, jf))

# 2. Sanitize HTML templates: portfolio.html, index.html, mobile.html
def sanitize_portfolio_html(file_path):
    if not os.path.exists(file_path):
        return
    print(f"Sanitizing HTML: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Footer
    content = re.sub(
        r'Desenvolvido sob o MQ Professional Design System',
        'Executive Analytics & BI Architecture',
        content,
        flags=re.I
    )
    # Inline DASHBOARDS array in HTML
    content = content.replace("Cockpit Geral de Indicadores Estratégicos MQ", "Cockpit Geral de Indicadores Estratégicos")
    content = content.replace("MQ Hair, Parlux", "Marcas Corporativas do Grupo")
    content = content.replace("Canal E-commerce MQ", "Canal E-commerce")
    content = content.replace("MQ Professional – Painel Executivo E-commerce", "Painel Executivo E-commerce Multi-Canal")
    content = content.replace("MQ Professional - Painel Executivo E-commerce", "Painel Executivo E-commerce Multi-Canal")
    content = content.replace("Consolidado MQ Professional", "Consolidado")
    content = content.replace("DRE MQ.2.1", "DRE 2.1")
    content = content.replace("canal_ecommerce_mq.html", "canal_ecommerce.html")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

sanitize_portfolio_html(os.path.join(INTRANET_DIR, "templates", "portfolio.html"))
sanitize_portfolio_html(os.path.join(PORTFOLIO_DIR, "index.html"))
sanitize_portfolio_html(os.path.join(PORTFOLIO_DIR, "mobile.html"))

# 3. Sanitize curriculo.html
for cf in [
    os.path.join(PORTFOLIO_DIR, "curriculo.html"),
    os.path.join(INTRANET_DIR, "curriculo_antonio_mello.html")
]:
    if os.path.exists(cf):
        print(f"Sanitizing Curriculo: {cf}")
        with open(cf, "r", encoding="utf-8") as f:
            c_text = f.read()
        c_text = re.sub(r'MQ Hair Company', 'Empresa Confidencial (Líder em Eletroportáteis & Beleza)', c_text)
        with open(cf, "w", encoding="utf-8") as f:
            f.write(c_text)

# 4. Sanitize DRE Empresa standalone
dre_emp_html = os.path.join(PORTFOLIO_DIR, "dre_empresa", "index.html")
if os.path.exists(dre_emp_html):
    print(f"Sanitizing DRE Empresa HTML: {dre_emp_html}")
    with open(dre_emp_html, "r", encoding="utf-8") as f:
        h = f.read()

    # Ocultar filtro Empresa
    h = re.sub(
        r'<div class="filtro-group filtro-empresa filter-field"[^>]*>',
        '<div class="filtro-group filtro-empresa filter-field" style="display: none !important;">',
        h
    )

    # Renomear Filtro Centro de Custo para Centro de Resultado
    h = re.sub(
        r'<label class="filter-label"[^>]*>Centro de Custo</label>',
        '<label class="filter-label" style="color: #ffffff !important; font-weight: 700;">Centro de Resultado</label>',
        h
    )
    h = h.replace('Todos os Centros', 'Todos os Centros de Resultado')
    h = h.replace('Buscar centro...', 'Buscar centro de resultado...')
    h = h.replace('Carregando centros…', 'Carregando centros de resultado…')

    # Header branding
    clean_brand = (
        '<div class="header-logo-box">\n'
        '        <a href="../index.html" title="Voltar ao Portfólio" style="text-decoration: none;">\n'
        '          <div style="font-family: \'Montserrat\', sans-serif; font-size: 15px; font-weight: 800; color: #fff; letter-spacing: 0.5px; display: flex; align-items: center; gap: 8px;">\n'
        '            <span style="color: var(--brand-secondary-dourado, #cb9727); font-size: 18px;">✦</span>\n'
        '            <span>EXECUTIVE <strong>ANALYTICS</strong></span>\n'
        '          </div>\n'
        '        </a>\n'
        '      </div>'
    )
    h = re.sub(r'<div class="header-logo-box">.*?</div>', clean_brand, h, flags=re.DOTALL)
    h = re.sub(r'title="Voltar ao Portal MQ"', 'title="Voltar ao Portfólio"', h)

    # Titulos e textos
    h = re.sub(r'<title>.*?</title>', '<title>DRE Consolidado — Demonstrativo de Resultado</title>', h)
    h = re.sub(r'MQ PROFESSIONAL', 'EXECUTIVE ANALYTICS', h)
    h = re.sub(r'BI MQ Hair Company', 'Antonio Mello | BI Architecture', h)
    h = re.sub(r'Portal Corporativo • DRE Empresa', 'Portfólio Executivo • DRE Consolidado', h)
    h = re.sub(r'MQ Hair', 'Empresa', h)
    h = re.sub(r'MQIA', 'Virtual Analytics', h)
    h = re.sub(r'Assistente MQIA', 'Assistente Virtual BI', h)
    h = re.sub(r'ex: Frete, Amazon, Parlux', 'ex: Frete, Marketing, Logística', h)

    with open(dre_emp_html, "w", encoding="utf-8") as f:
        f.write(h)

# 5. Sanitize DRE Assistencia standalone
dre_ast_html = os.path.join(PORTFOLIO_DIR, "dre_assistencia", "index.html")
if os.path.exists(dre_ast_html):
    print(f"Sanitizing DRE Assistencia HTML: {dre_ast_html}")
    with open(dre_ast_html, "r", encoding="utf-8") as f:
        h = f.read()

    clean_brand = (
        '<div class="header-logo-box">\n'
        '        <a href="../index.html" title="Voltar ao Portfólio" style="text-decoration: none;">\n'
        '          <div style="font-family: \'Montserrat\', sans-serif; font-size: 15px; font-weight: 800; color: #fff; letter-spacing: 0.5px; display: flex; align-items: center; gap: 8px;">\n'
        '            <span style="color: var(--brand-secondary-dourado, #cb9727); font-size: 18px;">✦</span>\n'
        '            <span>EXECUTIVE <strong>ANALYTICS</strong></span>\n'
        '          </div>\n'
        '        </a>\n'
        '      </div>'
    )
    h = re.sub(r'<div class="header-logo-box">.*?</div>', clean_brand, h, flags=re.DOTALL)
    h = re.sub(r'title="Voltar ao Portal MQ"', 'title="Voltar ao Portfólio"', h)
    h = re.sub(r'<title>.*?</title>', '<title>DRE Gestores — Gestão de Resultados</title>', h)
    h = re.sub(r'MQ PROFESSIONAL', 'EXECUTIVE ANALYTICS', h)
    h = re.sub(r'BI MQ Hair Company', 'Antonio Mello | BI Architecture', h)
    h = re.sub(r'MQ Hair', 'Empresa', h)
    h = re.sub(r'MQ\.2\.1', '2.1', h)

    with open(dre_ast_html, "w", encoding="utf-8") as f:
        f.write(h)

# 6. Sanitize Ecommerce standalone
ecom_html = os.path.join(PORTFOLIO_DIR, "ecommerce", "index.html")
if os.path.exists(ecom_html):
    print(f"Sanitizing Ecommerce HTML: {ecom_html}")
    with open(ecom_html, "r", encoding="utf-8") as f:
        h = f.read()

    clean_brand = (
        '<div class="header-logo-box">\n'
        '        <a href="../index.html" title="Voltar ao Portfólio" style="text-decoration: none;">\n'
        '          <div style="font-family: \'Montserrat\', sans-serif; font-size: 15px; font-weight: 800; color: #fff; letter-spacing: 0.5px; display: flex; align-items: center; gap: 8px;">\n'
        '            <span style="color: var(--brand-secondary-dourado, #cb9727); font-size: 18px;">✦</span>\n'
        '            <span>EXECUTIVE <strong>ANALYTICS</strong></span>\n'
        '          </div>\n'
        '        </a>\n'
        '      </div>'
    )
    h = re.sub(r'<div class="header-logo-box">.*?</div>', clean_brand, h, flags=re.DOTALL)
    h = re.sub(r'title="Voltar ao Portal MQ"', 'title="Voltar ao Portfólio"', h)
    h = re.sub(r'<title>.*?</title>', '<title>Painel Executivo E-commerce Multi-Canal</title>', h)
    h = re.sub(r'MQ PROFESSIONAL', 'EXECUTIVE ANALYTICS', h)
    h = re.sub(r'BI MQ Hair Company', 'Antonio Mello | BI Architecture', h)
    h = re.sub(r'<option value="MQ PRO">MQ PRO</option>', '<option value="CANAL 01">CANAL 01</option>', h)
    h = re.sub(r'MQ PRO', 'CANAL 01', h)

    with open(ecom_html, "w", encoding="utf-8") as f:
        f.write(h)

# 7. Sanitize Dashboard TV files (canal_ecommerce.html, mapa_regionais, paises)
tv_dir = os.path.join(PORTFOLIO_DIR, "dashboard_tv")
if os.path.exists(tv_dir):
    mq_canal = os.path.join(tv_dir, "canal_ecommerce_mq.html")
    clean_canal = os.path.join(tv_dir, "canal_ecommerce.html")
    if os.path.exists(mq_canal):
        with open(mq_canal, "r", encoding="utf-8") as f:
            c = f.read()
        c = re.sub(r'E-COMMERCE - MQ', 'E-COMMERCE', c)
        c = re.sub(r'E-commerce MQ', 'E-commerce Principal', c)
        c = re.sub(r'ecommerce_mq', 'ecommerce', c)
        c = re.sub(r'MQ Design System', 'Executive Design System', c)
        with open(clean_canal, "w", encoding="utf-8") as f:
            f.write(c)
        with open(mq_canal, "w", encoding="utf-8") as f:
            f.write(c)

    # static js in dashboard_tv
    for jsf in ["paises.js", "mapa_regionais.js", "teste_estoque.js", "tv_rotator.js"]:
        jspath = os.path.join(tv_dir, "static", "js", jsf)
        if os.path.exists(jspath):
            with open(jspath, "r", encoding="utf-8") as f:
                jst = f.read()
            jst = re.sub(r'MQ HAIR COMPANY', 'EXECUTIVE ANALYTICS', jst, flags=re.I)
            jst = re.sub(r'MQ HAIR', 'COMEX', jst, flags=re.I)
            jst = re.sub(r'MQ Professional', 'Executive Analytics', jst, flags=re.I)
            with open(jspath, "w", encoding="utf-8") as f:
                f.write(jst)

print("Full portfolio anonymization completed successfully!")

