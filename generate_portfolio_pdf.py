import os
import json
from playwright.sync_api import sync_playwright

def generate_portfolio_pdf(dataset_path='portfolio_final_dataset.json', output_pdf_path='static/portfolio_anderson_mello.pdf'):
    """
    Gera um PDF executivo de alta fidelidade visual para vagas de emprego,
    contendo capa, sumário executivo, estatísticas de impacto e catálogo completo dos 66 dashboards.
    """
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Arquivo de dados {dataset_path} não encontrado.")

    with open(dataset_path, 'r', encoding='utf-8') as f:
        dashboards = json.load(f)

    # Agrupa por departamento
    depts = {}
    for d in dashboards:
        dept_name = d.get('department', 'Geral')
        if dept_name not in depts:
            depts[dept_name] = []
        depts[dept_name].append(d)

    total_dashboards = len(dashboards)
    total_depts = len(depts)
    total_fullstack = sum(1 for d in dashboards if 'Fullstack' in d.get('tech', ''))
    total_powerbi = sum(1 for d in dashboards if 'Power BI' in d.get('tech', ''))

    # Constrói HTML formatado especificamente para PDF executivo A4
    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&display=swap');
  
  @page {{
    size: A4 portrait;
    margin: 1.5cm 1.2cm;
    @bottom-right {{
      content: counter(page);
      font-family: 'Montserrat', sans-serif;
      font-size: 8pt;
      color: #777;
    }}
  }}

  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}

  body {{
    font-family: 'Montserrat', sans-serif;
    color: #1a1a1a;
    background: #fff;
    line-height: 1.4;
    font-size: 9pt;
  }}

  /* CAPA DO PORTFÓLIO */
  .cover-page {{
    page-break-after: always;
    height: 92vh;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 2.5cm 1.5cm;
    background: linear-gradient(145deg, #0d0d0d 0%, #171717 100%);
    color: #fff;
    border-radius: 8px;
    position: relative;
    border: 2px solid #CB9727;
  }}

  .cover-badge {{
    display: inline-block;
    background: linear-gradient(135deg, #CB9727 0%, #F5D372 50%, #A6781B 100%);
    color: #000;
    font-weight: 900;
    font-size: 10pt;
    padding: 6px 14px;
    border-radius: 4px;
    letter-spacing: 2px;
    text-transform: uppercase;
    width: fit-content;
  }}

  .cover-title {{
    font-size: 26pt;
    font-weight: 900;
    line-height: 1.15;
    margin-top: 1.5cm;
    color: #fff;
    letter-spacing: -0.5px;
  }}
  .cover-title span {{
    color: #CB9727;
  }}

  .cover-subtitle {{
    font-size: 12pt;
    color: #b0b5bc;
    margin-top: 0.8cm;
    font-weight: 400;
    max-width: 90%;
    line-height: 1.5;
  }}

  .cover-stats-box {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-top: 2cm;
    padding: 16px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(203, 151, 39, 0.3);
    border-radius: 8px;
  }}

  .cover-stat-item {{
    text-align: center;
  }}
  .cover-stat-val {{
    font-size: 20pt;
    font-weight: 900;
    color: #CB9727;
  }}
  .cover-stat-lbl {{
    font-size: 7.5pt;
    text-transform: uppercase;
    color: #999;
    font-weight: 600;
    letter-spacing: 0.5px;
    margin-top: 2px;
  }}

  .cover-footer {{
    border-top: 1px solid rgba(255, 255, 255, 0.15);
    padding-top: 1cm;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
  }}

  .author-name {{
    font-size: 14pt;
    font-weight: 800;
    color: #fff;
  }}
  .author-role {{
    font-size: 9pt;
    color: #CB9727;
    font-weight: 600;
    margin-top: 2px;
  }}
  .author-contact {{
    font-size: 8pt;
    color: #999;
    text-align: right;
    line-height: 1.5;
  }}

  /* PÁGINAS INTERNAS */
  .page-header {{
    border-bottom: 2px solid #CB9727;
    padding-bottom: 6px;
    margin-bottom: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}

  .page-title {{
    font-size: 13pt;
    font-weight: 800;
    color: #111;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}

  .page-subtitle {{
    font-size: 8pt;
    color: #666;
    font-weight: 600;
  }}

  /* SUMÁRIO EXECUTIVO */
  .executive-summary {{
    background: #f8f9fa;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #CB9727;
    padding: 12px 16px;
    border-radius: 6px;
    margin-bottom: 20px;
    font-size: 8.5pt;
    color: #333;
    line-height: 1.5;
  }}

  /* SEÇÕES DE DEPARTAMENTOS */
  .dept-section {{
    margin-bottom: 24px;
    page-break-inside: auto;
  }}

  .dept-header {{
    background: #111;
    color: #fff;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 9.5pt;
    font-weight: 800;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    border-left: 5px solid #CB9727;
  }}
  .dept-count {{
    background: #CB9727;
    color: #000;
    font-size: 7.5pt;
    padding: 2px 8px;
    border-radius: 3px;
    font-weight: 700;
  }}

  /* TABELA / CARDS DE DASHBOARDS */
  .dashboard-table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 14px;
  }}

  .dashboard-table tr {{
    page-break-inside: avoid;
    border-bottom: 1px solid #e9ecef;
  }}

  .dashboard-table td {{
    padding: 9px 8px;
    vertical-align: top;
  }}

  .cell-title {{
    width: 32%;
  }}
  .dash-name {{
    font-size: 8.5pt;
    font-weight: 700;
    color: #111;
    line-height: 1.25;
  }}
  .dash-tech {{
    display: inline-block;
    margin-top: 4px;
    font-size: 6.8pt;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 3px;
    text-transform: uppercase;
  }}
  .tech-pbi {{
    background: #fff8e1;
    color: #b78103;
    border: 1px solid #ffe082;
  }}
  .tech-full {{
    background: #e8f5e9;
    color: #2e7d32;
    border: 1px solid #a5d6a7;
  }}

  .cell-desc {{
    width: 44%;
    font-size: 8pt;
    color: #4a5568;
    line-height: 1.35;
  }}
  .impact-callout {{
    font-size: 7.5pt;
    color: #744210;
    background: #fffaf0;
    padding: 3px 6px;
    border-radius: 3px;
    margin-top: 4px;
    border-left: 2px solid #CB9727;
  }}

  .cell-stack {{
    width: 24%;
    font-size: 7.2pt;
    color: #666;
  }}
  .stack-pills {{
    display: flex;
    flex-wrap: wrap;
    gap: 3px;
  }}
  .pill {{
    background: #edf2f7;
    color: #4a5568;
    padding: 1px 5px;
    border-radius: 3px;
    font-weight: 500;
  }}
</style>
</head>
<body>

  <!-- CAPA -->
  <div class="cover-page">
    <div>
      <span class="cover-badge">Visão completa, controle total.</span>
      <h1 class="cover-title">Cockpit Executivo Estratégico</h1>
      <p class="cover-subtitle">
        Catálogo corporativo consolidado com mais de 60 soluções analíticas, englobando modelagem dimensional Star Schema, ETL robusto, governança, dashboards executivos Power BI e plataformas analíticas Fullstack sob medida.
      </p>

      <div class="cover-stats-box">
        <div class="cover-stat-item">
          <div class="cover-stat-val">{total_dashboards}</div>
          <div class="cover-stat-lbl">Dashboards Criados</div>
        </div>
        <div class="cover-stat-item">
          <div class="cover-stat-val">{total_depts}</div>
          <div class="cover-stat-lbl">Departamentos / Áreas</div>
        </div>
        <div class="cover-stat-item">
          <div class="cover-stat-val">{total_powerbi}</div>
          <div class="cover-stat-lbl">Modelos Power BI</div>
        </div>
        <div class="cover-stat-item">
          <div class="cover-stat-val">{total_fullstack}</div>
          <div class="cover-stat-lbl">Web Apps Python</div>
        </div>
      </div>
    </div>

    <div class="cover-footer">
      <div>
        <div class="author-name">Antonio Mello</div>
        <div class="author-role">Especialista em Business Intelligence & Engenharia de Dados</div>
      </div>
      <div class="author-contact">
        LinkedIn: linkedin.com/in/antonio-carlos-mello/<br>
        Contato / WhatsApp: (11) 99955-3359<br>
        E-mail: acmello.106@gmail.com<br>
        Localização: São Paulo, SP<br>
        Especialidades: Power BI • DAX • SQL • Python • Oracle • Modelagem Dimensional
      </div>
    </div>
  </div>

  <!-- PÁGINA INTERNA 1: SUMÁRIO EXECUTIVO & METODOLOGIA -->
  <div class="page-header">
    <div class="page-title">Sumário Executivo & Diferenciais Técnicos</div>
    <div class="page-subtitle">Antonio Mello • Portfólio de Business Intelligence</div>
  </div>

  <div class="executive-summary">
    <strong>Resumo de Competências & Perfil Profissional:</strong><br>
    Profissional com sólida trajetória no desenvolvimento de ecossistemas analíticos completos. Atuação direta com Diretorias Executivas, Gerentes e Líderes de Operação para traduzir desafios de negócios em painéis de alta disponibilidade com impacto direto em receita, contenção de despesas operacionais e otimização de estoque.
  </div>

  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 24px;">
    <div style="background: #fafafa; border: 1px solid #e0e0e0; padding: 10px; border-radius: 6px;">
      <h3 style="font-size: 8.5pt; font-weight: 800; color: #111; margin-bottom: 6px; color: #b78103;">
        ✦ ARQUITETURA & MODELAGEM DIMENSIONAL
      </h3>
      <p style="font-size: 7.8pt; color: #555; line-height: 1.4;">
        Criação de Data Warehouses e modelos Star Schema (Fatos e Dimensões) otimizados. Cálculos avançados com DAX estruturado, Time Intelligence e otimização de performance via VertiPaq.
      </p>
    </div>
    <div style="background: #fafafa; border: 1px solid #e0e0e0; padding: 10px; border-radius: 6px;">
      <h3 style="font-size: 8.5pt; font-weight: 800; color: #111; margin-bottom: 6px; color: #2e7d32;">
        ✦ ENGENHARIA & DESENVOLVIMENTO FULLSTACK
      </h3>
      <p style="font-size: 7.8pt; color: #555; line-height: 1.4;">
        Desenvolvimento de aplicações analíticas web em Python (Flask) conectadas nativamente a bancos relacionais (Oracle ERP Sankhya, MariaDB, PostgreSQL), proporcionando automação sem custo de licenças.
      </p>
    </div>
  </div>

  <!-- CATÁLOGO DETALHADO POR DEPARTAMENTO -->
  <div class="page-header" style="margin-top: 10px;">
    <div class="page-title">Catálogo Completo de Soluções Implementadas ({total_dashboards} Projetos)</div>
    <div class="page-subtitle">Página de Detalhamento Técnico</div>
  </div>
"""

    # Itera por departamento adicionando tabelas elegantes
    for dept_name, items in sorted(depts.items()):
        html_content += f"""
        <div class="dept-section">
          <div class="dept-header">
            <span>{dept_name}</span>
            <span class="dept-count">{len(items)} Painéis</span>
          </div>

          <table class="dashboard-table">
        """
        for item in items:
            is_fullstack = 'Fullstack' in item.get('tech', '')
            badge_class = 'tech-full' if is_fullstack else 'tech-pbi'
            badge_text = 'Web / Python' if is_fullstack else 'Power BI Pro'
            
            pills = "".join([f'<span class="pill">{stk}</span>' for stk in item.get('stack', [])[:4]])

            html_content += f"""
            <tr>
              <td class="cell-title">
                <div class="dash-name">{item['title']}</div>
                <span class="dash-tech {badge_class}">{badge_text}</span>
              </td>
              <td class="cell-desc">
                {item.get('description', 'Cockpit analítico para acompanhamento de KPIs estratégicos e tomada de decisão.')}
                <div class="impact-callout">
                  <strong>Impacto:</strong> {item.get('impact', 'Agilidade na gestão executiva.')}
                </div>
              </td>
              <td class="cell-stack">
                <div class="stack-pills">{pills}</div>
              </td>
            </tr>
            """
        html_content += """
          </table>
        </div>
        """

    html_content += """
</body>
</html>
"""

    # Grava arquivo HTML intermediário para debug e renderização
    temp_html = 'portfolio_pdf_render.html'
    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTML gerado em {temp_html}. Iniciando Playwright para converter em PDF A4...")
    
    os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        # Abre o arquivo HTML local
        abs_html_path = os.path.abspath(temp_html).replace('\\', '/')
        page.goto(f'file:///{abs_html_path}', wait_until='networkidle')
        
        page.pdf(
            path=output_pdf_path,
            format='A4',
            print_background=True,
            margin={'top': '1.2cm', 'bottom': '1.2cm', 'left': '1.2cm', 'right': '1.2cm'},
            display_header_footer=True,
            footer_template='<div style="font-family: Montserrat, sans-serif; font-size: 8pt; width: 100%; text-align: right; padding-right: 1.2cm; color: #888;">Antonio Mello • Portfólio de BI | Página <span class="pageNumber"></span> de <span class="totalPages"></span></div>',
            header_template='<div></div>'
        )
        browser.close()

    print(f"PDF executivo gerado com sucesso em: {output_pdf_path}")
    return output_pdf_path

if __name__ == '__main__':
    generate_portfolio_pdf()
