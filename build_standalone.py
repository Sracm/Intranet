import os
import json
import shutil

def build_standalone_portfolio(dist_dir='portfolio_standalone'):
    os.makedirs(dist_dir, exist_ok=True)
    screenshots_dist = os.path.join(dist_dir, 'static', 'portfolio_screenshots')
    os.makedirs(screenshots_dist, exist_ok=True)

    # 1. Copia imagens dos screenshots
    screenshots_src = 'static/portfolio_screenshots'
    for f in os.listdir(screenshots_src):
        if f.endswith('.jpg') or f.endswith('.png'):
            shutil.copy2(os.path.join(screenshots_src, f), os.path.join(screenshots_dist, f))

    # 2. Copia os arquivos de download (PDF e PPTX)
    if os.path.exists('static/portfolio_anderson_mello.pdf'):
        shutil.copy2('static/portfolio_anderson_mello.pdf', os.path.join(dist_dir, 'Portfolio_Anderson_Mello_BI_Executive.pdf'))
    if os.path.exists('static/Portfolio_Anderson_Mello_BI_Executive.pptx'):
        shutil.copy2('static/Portfolio_Anderson_Mello_BI_Executive.pptx', os.path.join(dist_dir, 'Portfolio_Anderson_Mello_BI_Executive.pptx'))

    # 3. Lê dados e template
    with open('templates/portfolio.html', 'r', encoding='utf-8') as f:
        html = f.read()

    with open('portfolio_final_dataset.json', 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    # Injeta os dados no JavaScript
    html = html.replace('{{ dashboards_json|safe }}', json.dumps(dataset, ensure_ascii=False))

    # Ajusta links de download para caminhos relativos para funcionar 100% no Vercel / GitHub Pages
    html = html.replace('href="/portfolio/download-pptx"', 'href="Portfolio_Anderson_Mello_BI_Executive.pptx" download')
    html = html.replace('href="/portfolio/download-pdf"', 'href="Portfolio_Anderson_Mello_BI_Executive.pdf" download')

    # Remove o link de retorno para intranet interna no modo demo público
    html = html.replace('<a href="/" class="btn btn-outline">\n        <i class="fa-solid fa-house"></i> Intranet\n      </a>', '')
    html = html.replace('<a href="/" class="btn btn-outline">\r\n        <i class="fa-solid fa-house"></i> Intranet\r\n      </a>', '')

    with open(os.path.join(dist_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Build do portfólio standalone concluído em: {dist_dir}/")
    print(f"- Total de imagens copiadas: {len(os.listdir(screenshots_dist))}")
    print(f"- Arquivo principal: {dist_dir}/index.html")

if __name__ == '__main__':
    build_standalone_portfolio()
