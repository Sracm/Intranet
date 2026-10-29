import os
import json
import shutil

def update_portfolio_with_all_tv_views():
    dataset_file = 'portfolio_final_dataset.json'
    with open(dataset_file, 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    # Lista das telas completas do Dashboard TV
    tv_dashboards = [
        {
            "id": 26,
            "title": "Dashboard TV - Performance de Vendas (Painel Geral)",
            "department": "Comercial & Vendas",
            "description": "Cockpit executivo Full HD em tempo real transmitido nas TVs corporativas: acompanhamento de metas mensais, velocímetros de atingimento por canal e alerta sonoro de meta batida.",
            "url": "#",
            "tech": "Fullstack Python / Flask / SQL Real-Time",
            "stack": ["Python 3", "Flask", "SQL Oracle Sankhya", "HTML5 Canvas", "WebSocket/Polling", "Audio FX"],
            "impact": "Engajamento imediato da equipe comercial e acompanhamento instantâneo da Diretoria sem custo de licença.",
            "image": "static/portfolio_screenshots/tv_geral.jpg",
            "is_static": True
        },
        {
            "id": 261,
            "title": "Dashboard TV - Países & COMEX (Visão Global)",
            "department": "Comercial & Vendas",
            "description": "Monitoramento de exportação e comércio exterior em 41 países. Análise de produto carro-chefe global, share de mercado 2025 x 2026 e evolução percentual por país.",
            "url": "#",
            "tech": "Fullstack Python / Flask / SQL Real-Time",
            "stack": ["Python 3", "Flask", "SQL (COMEX)", "CSS3 Glassmorphism", "Ranking Dinâmico"],
            "impact": "Inteligência competitiva internacional e priorização de mercados globais em tempo real.",
            "image": "static/portfolio_screenshots/tv_paises.jpg",
            "is_static": True
        },
        {
            "id": 262,
            "title": "Dashboard TV - Categorias de Produtos",
            "department": "Comercial & Vendas",
            "description": "Análise de share e evolução de mix por linha: Pranchas, Secadores, Escovas Secadoras, Máquinas, Modeladores e Tesouras, com ranking dos top SKUs em evolução.",
            "url": "#",
            "tech": "Fullstack Python / Flask / SQL Real-Time",
            "stack": ["Python 3", "Flask", "Oracle Sankhya", "Mix Modeling", "JavaScript Grid"],
            "impact": "Visibilidade profunda de curva de produtos e direcionamento de campanhas promocionais.",
            "image": "static/portfolio_screenshots/tv_categorias.jpg",
            "is_static": True
        },
        {
            "id": 263,
            "title": "Dashboard TV - Marcas Corporativas",
            "department": "Comercial & Vendas",
            "description": "Distribuição de market share e crescimento das marcas do ecossistema: MQ Pro, Parlux, Force Barb, MQ Escovas, MQ Beauty e MQ Tesoura.",
            "url": "#",
            "tech": "Fullstack Python / Flask / SQL Real-Time",
            "stack": ["Python 3", "Flask", "SQL Analytics", "Brand Performance", "Data Storytelling"],
            "impact": "Acompanhamento da estratégia multi-marcas e rentabilidade por linha de negócio.",
            "image": "static/portfolio_screenshots/tv_marcas.jpg",
            "is_static": True
        },
        {
            "id": 264,
            "title": "Dashboard TV - Acumulado do Ano (YTD)",
            "department": "Comercial & Vendas",
            "description": "Histórico mensal de janeiro a dezembro com barras comparativas mês a mês, linha de corte de metas e velocímetros de fechamento consolidado.",
            "url": "#",
            "tech": "Fullstack Python / Flask / SQL Real-Time",
            "stack": ["Python 3", "Flask", "Time Series Analysis", "Chart.js / SVG", "SQL Aggregation"],
            "impact": "Previsibilidade de faturamento anual e diagnóstico de sazonalidade comercial.",
            "image": "static/portfolio_screenshots/tv_acumulado.jpg",
            "is_static": True
        },
        {
            "id": 265,
            "title": "Dashboard TV - Performance Todos os Canais",
            "department": "Comercial & Vendas",
            "description": "Cockpit simultâneo de todos os canais de receita: Varejo SP, Varejo Regional, Distribuição, Comex, E-commerce MQ e E-commerce Parlux com comparativo por trimestre (T1 a T4).",
            "url": "#",
            "tech": "Fullstack Python / Flask / SQL Real-Time",
            "stack": ["Python 3", "Flask", "Multi-Channel Analytics", "SQL Real-time"],
            "impact": "Visão 360º de todas as frentes de receita corporativa da companhia.",
            "image": "static/portfolio_screenshots/tv_todos_canais.jpg",
            "is_static": True
        }
    ]

    # Substitui o card antigo #26 pela coleção completa de telas da TV
    new_dataset = []
    for d in dataset:
        if d.get('id') == 26 or 'Dashboard TV' in d.get('title', ''):
            continue
        # Corrige caminho da imagem caso ainda tenha barra absoluta
        if 'image' in d:
            d['image'] = d['image'].lstrip('/')
        # Garante URL desacoplada
        d['url'] = '#'
        new_dataset.append(d)

    # Insere as 6 telas ricas da TV na categoria Comercial & Vendas
    new_dataset.extend(tv_dashboards)

    # Ordena por departamento e título
    new_dataset.sort(key=lambda x: (x.get('department', ''), x.get('title', '')))

    # Salva dataset final
    with open(dataset_file, 'w', encoding='utf-8') as f:
        json.dump(new_dataset, f, ensure_ascii=False, indent=2)

    print(f"Dataset atualizado com sucesso! Total de dashboards: {len(new_dataset)}")

    # Regera o index.html da pasta portfolio_standalone
    with open('templates/portfolio.html', 'r', encoding='utf-8') as f:
        tpl = f.read()

    payload = json.dumps(new_dataset, ensure_ascii=False)
    import re
    new_html = re.sub(r'const DASHBOARDS = .*?;', f'const DASHBOARDS = {payload};', tpl, flags=re.DOTALL)
    
    # Assegura caminhos relativos
    new_html = new_html.replace('"/static/portfolio_screenshots/', '"static/portfolio_screenshots/')
    new_html = new_html.replace("'/static/portfolio_screenshots/", "'static/portfolio_screenshots/")

    with open('portfolio_standalone/index.html', 'w', encoding='utf-8') as f:
        f.write(new_html)

    # Atualiza também templates/portfolio.html
    with open('templates/portfolio.html', 'w', encoding='utf-8') as f:
        f.write(new_html)

    print("portfolio_standalone/index.html e templates/portfolio.html regerados com todas as telas do Dashboard TV!")

if __name__ == '__main__':
    update_portfolio_with_all_tv_views()
