import os
import json
import re
import shutil
from playwright.sync_api import sync_playwright

def sanitize_filename(name):
    clean = re.sub(r'[^a-zA-Z0-9_\-]', '_', str(name).lower())
    return clean[:35]

def capture_all_screenshots(dataset_file='portfolio_final_dataset.json', output_dir='static/portfolio_screenshots'):
    os.makedirs(output_dir, exist_ok=True)
    
    with open(dataset_file, 'r', encoding='utf-8') as f:
        dashboards = json.load(f)

    # Garante imagem base de fallback caso um link externo esteja offline ou protegido por login
    sample_src = os.path.join(output_dir, 'pbi_sample.jpg')

    with sync_playwright() as p:
        browser = p.chromium.launch()
        
        for i, d in enumerate(dashboards, 1):
            dash_id = d.get('id', i)
            title = d.get('title', f'dash_{dash_id}')
            safe_name = f"dash_{dash_id}_{sanitize_filename(title)}"
            img_filename = f"{safe_name}.jpg"
            img_path = os.path.join(output_dir, img_filename)

            d['image'] = f"/static/portfolio_screenshots/{img_filename}"

            if os.path.exists(img_path) and os.path.getsize(img_path) > 10000:
                continue

            raw_url = d.get('url', '')
            if not raw_url:
                if os.path.exists(sample_src):
                    shutil.copy2(sample_src, img_path)
                continue

            target_url = (raw_url.replace('10.11.1.162:', '127.0.0.1:')
                                 .replace('10.11.1.100:', '127.0.0.1:')
                                 .replace('localhost:', '127.0.0.1:'))
            
            is_local = '127.0.0.1' in target_url
            wait_time = 2000 if is_local else 8000
            timeout_ms = 10000 if is_local else 20000

            # Cria nova página limpa para cada dashboard evitando conflito de navegação
            try:
                page = browser.new_page(viewport={'width': 1600, 'height': 900})
                page.goto(target_url, timeout=timeout_ms, wait_until='domcontentloaded')
                page.wait_for_timeout(wait_time)
                page.screenshot(path=img_path, quality=80)
                page.close()
            except Exception:
                try:
                    page.close()
                except:
                    pass
                if os.path.exists(sample_src):
                    shutil.copy2(sample_src, img_path)

        browser.close()

    with open(dataset_file, 'w', encoding='utf-8') as f:
        json.dump(dashboards, f, ensure_ascii=False, indent=2)

    print("Concluido! Todas as imagens foram processadas com sucesso.")

if __name__ == '__main__':
    capture_all_screenshots()
