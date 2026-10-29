import os
from playwright.sync_api import sync_playwright

output_dirs = [
    'static/portfolio_screenshots',
    'portfolio_standalone/static/portfolio_screenshots'
]
for d in output_dirs:
    os.makedirs(d, exist_ok=True)

tv_views = [
    ('tv_geral', 'http://127.0.0.1:5050/tv'),
    ('tv_paises', 'http://127.0.0.1:5050/paises?mes=8&ano=2026'),
    ('tv_categorias', 'http://127.0.0.1:5050/categorias?mes=8&ano=2026'),
    ('tv_marcas', 'http://127.0.0.1:5050/marcas'),
    ('tv_acumulado', 'http://127.0.0.1:5050/acumulado'),
    ('tv_trimestre', 'http://127.0.0.1:5050/trimestre'),
    ('tv_canais', 'http://127.0.0.1:5050/canais'),
    ('tv_todos_canais', 'http://127.0.0.1:5050/todos_canais')
]

with sync_playwright() as p:
    browser = p.chromium.launch()
    # Resolução 1920x1080 Full HD (formato TV)
    page = browser.new_page(viewport={'width': 1920, 'height': 1080})
    
    for name, url in tv_views:
        print(f"Capturando tela TV: {name} -> {url}...")
        try:
            page.goto(url, timeout=15000, wait_until='networkidle')
            page.wait_for_timeout(2500)
            
            for out_dir in output_dirs:
                save_path = os.path.join(out_dir, f"{name}.jpg")
                page.screenshot(path=save_path, quality=85)
                print(f"  Salvo em {save_path} ({os.path.getsize(save_path)} bytes)")
        except Exception as e:
            print(f"  Erro ao capturar {name}: {e}")
            
    # Também substitui a imagem dash_26_dashboard_tv.jpg pela tela real geral
    for out_dir in output_dirs:
        dash_26 = os.path.join(out_dir, 'dash_26_dashboard_tv.jpg')
        tv_geral = os.path.join(out_dir, 'tv_geral.jpg')
        if os.path.exists(tv_geral):
            import shutil
            shutil.copy2(tv_geral, dash_26)
            print(f"dash_26_dashboard_tv.jpg atualizado com tv_geral.jpg em {out_dir}")

    browser.close()

print("Todas as telas do Dashboard TV foram capturadas!")
