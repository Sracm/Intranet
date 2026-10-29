import os
import json
import base64
from playwright.sync_api import sync_playwright

def get_base64_image(image_path):
    if not os.path.exists(image_path):
        return None
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/jpeg;base64,{encoded_string}"
    except Exception:
        return None

def generate_portfolio_visual_pdf(dataset_path='portfolio_final_dataset.json', output_pdf_path='static/Portfolio_Antonio_Mello_BI_Executive.pdf'):
    """
    Gera o PDF Executivo Visual de alta fidelidade para envio a vagas de emprego,
    com capa executiva, sumário e catálogo com AS TELAS REAIS de cada dashboard embutidas em alta definição.
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

    # Converte a imagem fallback para base64
    fallback_b64 = get_base64_image('static/portfolio_screenshots/pbi_sample.jpg')

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&display=swap');
  
  @page {{
    size: A4 portrait;
    margin: 1.2cm 1cm;
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
    font-size: 8.5pt;
  }}

  /* CAPA DO PORTFÓLIO */
  .cover-page {{
    page-break-after: always;
    height: 92vh;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 2.5cm 1.5cm;
    background: linear-gradient(145deg, #0a0a0a 0%, #171717 100%);
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
    font-size: 11.5pt;
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

  /* HEADER DE PÁGINA */
  .page-header {{
    border-bottom: 2px solid #CB9727;
    padding-bottom: 5px;
    margin-bottom: 15px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .page-title {{
    font-size: 12pt;
    font-weight: 800;
    color: #111;
    text-transform: uppercase;
  }}
  .page-subtitle {{
    font-size: 7.5pt;
    color: #666;
    font-weight: 600;
  }}

  /* SUMÁRIO */
  .executive-summary {{
    background: #f8f9fa;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #CB9727;
    padding: 10px 14px;
    border-radius: 6px;
    margin-bottom: 18px;
    font-size: 8.2pt;
    color: #333;
    line-height: 1.45;
  }}

  /* SEÇÕES E CARDS VISUAIS COM SCREENSHOT */
  .dept-section {{
    margin-bottom: 22px;
  }}

  .dept-header {{
    background: #111;
    color: #fff;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 9pt;
    font-weight: 800;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    border-left: 4px solid #CB9727;
  }}
  .dept-count {{
    background: #CB9727;
    color: #000;
    font-size: 7pt;
    padding: 2px 7px;
    border-radius: 3px;
    font-weight: 700;
  }}

  .visual-card {{
    page-break-inside: avoid;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 10px;
    margin-bottom: 12px;
    background: #fafafa;
    display: flex;
    gap: 14px;
  }}

  .visual-img-box {{
    width: 220px;
    height: 125px;
    flex-shrink: 0;
    border-radius: 4px;
    overflow: hidden;
    border: 1px solid #cbd5e1;
    background: #000;
  }}
  .visual-img-box img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: top center;
    display: block;
  }}

  .visual-info {{
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}

  .dash-name {{
    font-size: 9.5pt;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.2;
    margin-bottom: 4px;
  }}

  .tech-badge {{
    display: inline-block;
    font-size: 6.5pt;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 3px;
    text-transform: uppercase;
    margin-bottom: 6px;
    width: fit-content;
  }}
  .tech-pbi {{ background: #fff8e1; color: #b78103; border: 1px solid #ffe082; }}
  .tech-full {{ background: #e8f5e9; color: #2e7d32; border: 1px solid #a5d6a7; }}

  .dash-desc {{
    font-size: 7.8pt;
    color: #475569;
    line-height: 1.35;
    margin-bottom: 6px;
  }}

  .dash-impact {{
    font-size: 7.2pt;
    color: #744210;
    background: #fffaf0;
    padding: 3px 6px;
    border-radius: 3px;
    border-left: 2px solid #CB9727;
    margin-bottom: 6px;
  }}

  .dash-stack {{
    font-size: 6.8pt;
    color: #64748b;
  }}
</style>
</head>
<body>

  <!-- CAPA -->
  <div class="cover-page">
    <div>
      <span class="cover-badge">Executive Visual Portfolio</span>
      <h1 class="cover-title">Portfólio de <span>Business Intelligence</span> & Soluções Analíticas</h1>
      <p class="cover-subtitle">
        Catálogo executivo de alto impacto com captura de tela real de cada uma das 66 soluções desenvolvidas em Power BI Service e Web Applications Python/Flask.
      </p>

      <div class="cover-stats-box">
        <div class="cover-stat-item">
          <div class="cover-stat-val">{total_dashboards}</div>
          <div class="cover-stat-lbl">Dashboards & Telas</div>
        </div>
        <div class="cover-stat-item">
          <div class="cover-stat-val">{total_depts}</div>
          <div class="cover-stat-lbl">Áreas Corporativas</div>
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
        Competências: Power BI • DAX • SQL • Python • Modelagem Dimensional • Oracle Sankhya
      </div>
    </div>
  </div>

  <!-- PÁGINA 1: SUMÁRIO EXECUTIVO -->
  <div class="page-header">
    <div class="page-title">Sumário Executivo & Diferenciais</div>
    <div class="page-subtitle">Antonio Mello • Portfólio Visual de BI</div>
  </div>

  <div class="executive-summary">
    <strong>Abordagem Analítica & Arquitetura Visual:</strong><br>
    Cada painel apresentado neste portfólio foi desenhado com base em princípios rigorosos de usabilidade e hierarquia visual (Data Storytelling). Todas as soluções conectam diretamente a bancos de dados transacionais e analíticos, convertendo volumes expressivos de dados em insights de negócio para Diretores, Gerentes e Operação.
  </div>

  <div class="page-header" style="margin-top: 10px;">
    <div class="page-title">Galeria Visual dos 66 Dashboards Implementados</div>
    <div class="page-subtitle">Demonstração com Telas Reais</div>
  </div>
"""

    # Itera por departamento adicionando cards com imagens
    for dept_name, items in sorted(depts.items()):
        html_content += f"""
        <div class="dept-section">
          <div class="dept-header">
            <span>{dept_name}</span>
            <span class="dept-count">{len(items)} Painéis</span>
          </div>
        """
        for item in items:
            is_fullstack = 'Fullstack' in item.get('tech', '')
            badge_class = 'tech-full' if is_fullstack else 'tech-pbi'
            badge_text = 'Web Python / Flask' if is_fullstack else 'Power BI Pro'
            
            # Carrega imagem em base64 para o PDF ficar 100% autocontido
            img_rel = item.get('image', '').lstrip('/')
            img_b64 = get_base64_image(img_rel) if img_rel else None
            if not img_b64:
                img_b64 = fallback_b64

            stack_str = " • ".join(item.get('stack', [])[:4])

            html_content += f"""
            <div class="visual-card">
              <div class="visual-img-box">
                <img src="{img_b64}" alt="{item['title']}">
              </div>
              <div class="visual-info">
                <div>
                  <div class="dash-name">{item['title']}</div>
                  <span class="tech-badge {badge_class}">{badge_text}</span>
                  <div class="dash-desc">{item.get('description', 'Cockpit analítico para monitoramento de KPIs estratégicos e tomada de decisão.')}</div>
                  <div class="dash-impact"><strong>Impacto:</strong> {item.get('impact', 'Agilidade analítica na gestão.')}</div>
                </div>
                <div class="dash-stack"><strong>Stack:</strong> {stack_str}</div>
              </div>
            </div>
            """
        html_content += """
        </div>
        """

    html_content += """
</body>
</html>
"""

    temp_html = 'portfolio_visual_pdf_render.html'
    with open(temp_html, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("Gerando PDF com as telas embutidas em alta resolução...")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        abs_html_path = os.path.abspath(temp_html).replace('\\', '/')
        page.goto(f'file:///{abs_html_path}', wait_until='load')
        
        page.pdf(
            path=output_pdf_path,
            format='A4',
            print_background=True,
            margin={'top': '1.2cm', 'bottom': '1.2cm', 'left': '1cm', 'right': '1cm'},
            display_header_footer=True,
            footer_template='<div style="font-family: Montserrat, sans-serif; font-size: 8pt; width: 100%; text-align: right; padding-right: 1cm; color: #888;">Antonio Mello • Portfólio de BI | Página <span class="pageNumber"></span> de <span class="totalPages"></span></div>',
            header_template='<div></div>'
        )
        browser.close()

    standalone_dest = os.path.join('portfolio_standalone', os.path.basename(output_pdf_path))
    if os.path.exists('portfolio_standalone'):
        import shutil
        shutil.copy2(output_pdf_path, standalone_dest)
        print(f"Copiado para standalone: {standalone_dest}")

    print(f"PDF Visual gerado com sucesso em: {output_pdf_path}")
    return output_pdf_path

if __name__ == '__main__':
    generate_portfolio_visual_pdf()
