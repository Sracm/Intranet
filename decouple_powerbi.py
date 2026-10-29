import os
import json
import shutil

def sanitize_and_decouple_powerbi(dist_dir='portfolio_standalone'):
    """
    Remove completamente qualquer URL, link ou requisição externa à Microsoft/Power BI.
    Todos os 66 dashboards ficam 100% autocontidos no próprio site estático.
    """
    # 1. Carrega o dataset original e remove/zera URLs da Power BI
    dataset_file = 'portfolio_final_dataset.json'
    with open(dataset_file, 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    for d in dataset:
        # Apaga qualquer link para app.powerbi.com
        d['url'] = '#'
        # Se for Power BI, indica claramente que é Modelo Estático Demonstrativo
        if 'Power BI' in d.get('tech', ''):
            d['tech'] = 'Power BI (Demonstração Estática)'
            d['is_static'] = True

    # Salva dataset limpo sem links externos
    with open(dataset_file, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    # 2. Constrói o HTML estático definitivo
    with open('templates/portfolio.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # Injeta o dataset sem nenhum link do Power BI
    html = html.replace('{{ dashboards_json|safe }}', json.dumps(dataset, ensure_ascii=False))

    # Garante que os botões de download usem arquivos locais
    html = html.replace('href="/portfolio/download-pptx"', 'href="Portfolio_Anderson_Mello_BI_Executive.pptx" download')
    html = html.replace('href="/portfolio/download-pdf"', 'href="Portfolio_Anderson_Mello_BI_Executive.pdf" download')

    # Remove qualquer link para intranet interna
    html = html.replace('<a href="/" class="btn btn-outline">\n        <i class="fa-solid fa-house"></i> Intranet\n      </a>', '')
    html = html.replace('<a href="/" class="btn btn-outline">\r\n        <i class="fa-solid fa-house"></i> Intranet\r\n      </a>', '')

    # Garante que o card-preview e o botão de ação chamem apenas o visualizador interno (openLightbox)
    # Substitui a linha 784 antiga que ainda passava d.url
    html = html.replace(
        "openLightbox('${imgUrl}', '${d.title.replace(/'/g, \"\\\\'\")}', '${d.url}')",
        "openLightbox('${imgUrl}', '${d.title.replace(/'/g, \"\\\\'\")}', '${d.department}')"
    )

    out_file = os.path.join(dist_dir, 'index.html')
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(html)

    # Atualiza também o template Flask
    with open('templates/portfolio.html', 'w', encoding='utf-8') as f:
        f.write(html.replace('href="Portfolio_Anderson_Mello_BI_Executive.pptx" download', 'href="/portfolio/download-pptx"')
                    .replace('href="Portfolio_Anderson_Mello_BI_Executive.pdf" download', 'href="/portfolio/download-pdf"'))

    print(f"Limpeza concluída! Nenhuma URL do Power BI permaneceu em {out_file}")

if __name__ == '__main__':
    sanitize_and_decouple_powerbi()
