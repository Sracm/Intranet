import os
import json
import shutil

def build_static_demo_portfolio(dist_dir='portfolio_standalone'):
    """
    Gera a versão 100% estática do portfólio.
    Como as contas Power BI serão deletadas e recrutadores não possuem login,
    todos os dashboards do Power BI são apresentados em modo galeria estática
    (visualização da tela em alta resolução, zoom interativo e ficha técnica completa).
    """
    os.makedirs(dist_dir, exist_ok=True)
    screenshots_dist = os.path.join(dist_dir, 'static', 'portfolio_screenshots')
    os.makedirs(screenshots_dist, exist_ok=True)

    # Copia imagens dos screenshots
    screenshots_src = 'static/portfolio_screenshots'
    if os.path.exists(screenshots_src):
        for f in os.listdir(screenshots_src):
            if f.endswith('.jpg') or f.endswith('.png'):
                shutil.copy2(os.path.join(screenshots_src, f), os.path.join(screenshots_dist, f))

    # Copia arquivos para download
    if os.path.exists('static/portfolio_anderson_mello.pdf'):
        shutil.copy2('static/portfolio_anderson_mello.pdf', os.path.join(dist_dir, 'Portfolio_Anderson_Mello_BI_Executive.pdf'))
    if os.path.exists('static/Portfolio_Anderson_Mello_BI_Executive.pptx'):
        shutil.copy2('static/Portfolio_Anderson_Mello_BI_Executive.pptx', os.path.join(dist_dir, 'Portfolio_Anderson_Mello_BI_Executive.pptx'))

    # Lê template base
    with open('templates/portfolio.html', 'r', encoding='utf-8') as f:
        html = f.read()

    with open('portfolio_final_dataset.json', 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    # No dataset, marca claramente se é estático para o visualizador
    for d in dataset:
        if 'Power BI' in d.get('tech', ''):
            d['is_static'] = True
            d['badge_detail'] = 'Visualização Estática (Demonstração)'
        else:
            d['is_static'] = False
            d['badge_detail'] = 'Módulo Web Interativo'

    # Injeta os dados
    html = html.replace('{{ dashboards_json|safe }}', json.dumps(dataset, ensure_ascii=False))

    # Ajusta links de download
    html = html.replace('href="/portfolio/download-pptx"', 'href="Portfolio_Anderson_Mello_BI_Executive.pptx" download')
    html = html.replace('href="/portfolio/download-pdf"', 'href="Portfolio_Anderson_Mello_BI_Executive.pdf" download')

    # Remove o link de retorno para intranet interna
    html = html.replace('<a href="/" class="btn btn-outline">\n        <i class="fa-solid fa-house"></i> Intranet\n      </a>', '')
    html = html.replace('<a href="/" class="btn btn-outline">\r\n        <i class="fa-solid fa-house"></i> Intranet\r\n      </a>', '')

    # MODIFICAÇÃO DO BOTÃO NO CARD E NO LIGHTBOX PARA MODO ESTÁTICO:
    # Em vez de enviar para link quebrado do Power BI deletado, abre o zoom da tela ou abre modal
    old_card_action = """              <div class="card-action">
                <a href="${d.url}" target="_blank" class="btn-card btn-card-primary">
                  <i class="fa-solid fa-arrow-up-right-from-square"></i> Acessar Painel
                </a>
              </div>"""

    new_card_action = """              <div class="card-action">
                <button onclick="openLightbox('${imgUrl}', '${d.title.replace(/'/g, "\\\\'")}', '${d.department}')" class="btn-card btn-card-primary" style="border: none; cursor: pointer; width: 100%;">
                  <i class="fa-solid fa-magnifying-glass-plus"></i> Ver Tela do Dashboard
                </button>
              </div>"""

    html = html.replace(old_card_action, new_card_action)

    # Atualiza o modal Lightbox para focar na tela e no departamento
    old_lightbox_caption = """      <div class="lightbox-caption">
        <span id="lightboxTitle" style="font-weight: 700;">Título do Dashboard</span>
        <a id="lightboxLink" href="#" target="_blank" class="btn btn-gold" style="padding: 6px 12px; font-size: 0.75rem;">
          <i class="fa-solid fa-external-link"></i> Abrir Painel
        </a>
      </div>"""

    new_lightbox_caption = """      <div class="lightbox-caption">
        <div>
          <span id="lightboxTitle" style="font-weight: 700; font-size: 1rem; color: #fff;">Título do Dashboard</span>
          <span id="lightboxDept" style="display: block; font-size: 0.75rem; color: #CB9727; font-weight: 600;">Departamento</span>
        </div>
        <div style="font-size: 0.75rem; color: #999; background: #222; padding: 4px 10px; border-radius: 4px; border: 1px solid #444;">
          <i class="fa-solid fa-image"></i> Demonstração Visual Estática
        </div>
      </div>"""

    html = html.replace(old_lightbox_caption, new_lightbox_caption)

    # Ajusta os controllers do Lightbox
    old_lightbox_fn = """    function openLightbox(imgSrc, title, linkUrl) {
      document.getElementById('lightboxImg').src = imgSrc;
      document.getElementById('lightboxTitle').textContent = title;
      document.getElementById('lightboxLink').href = linkUrl;
      document.getElementById('lightboxModal').classList.add('active');
      document.body.style.overflow = 'hidden';
    }"""

    new_lightbox_fn = """    function openLightbox(imgSrc, title, dept) {
      document.getElementById('lightboxImg').src = imgSrc;
      document.getElementById('lightboxTitle').textContent = title;
      const deptEl = document.getElementById('lightboxDept');
      if (deptEl) deptEl.textContent = dept || 'Demonstração Executiva';
      document.getElementById('lightboxModal').classList.add('active');
      document.body.style.overflow = 'hidden';
    }"""

    html = html.replace(old_lightbox_fn, new_lightbox_fn)

    out_file = os.path.join(dist_dir, 'index.html')
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(html)

    # Também atualiza templates/portfolio.html local para ficar alinhado
    with open('templates/portfolio.html', 'w', encoding='utf-8') as f:
        f.write(html.replace('href="Portfolio_Anderson_Mello_BI_Executive.pptx" download', 'href="/portfolio/download-pptx"')
                    .replace('href="Portfolio_Anderson_Mello_BI_Executive.pdf" download', 'href="/portfolio/download-pdf"'))

    print(f"Portfólio estático gerado com sucesso em: {out_file}")

if __name__ == '__main__':
    build_static_demo_portfolio()
