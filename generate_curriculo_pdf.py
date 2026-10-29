import os
from playwright.sync_api import sync_playwright

def generate_pdf():
    html_path = os.path.abspath('curriculo_antonio_mello.html')
    pdf_path = os.path.abspath('Curriculo_Antonio_Carlos_de_Mello_BI.pdf')
    pdf_standalone = os.path.abspath('portfolio_standalone/Curriculo_Antonio_Carlos_de_Mello_BI.pdf')

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f'file:///{html_path.replace(os.sep, "/")}', wait_until='networkidle')
        
        # Oculta a barra de botões do topo para a impressão
        page.evaluate("""() => {
            const bar = document.querySelector('.print-bar');
            if (bar) bar.style.display = 'none';
            document.body.style.background = '#FFFFFF';
            document.body.style.padding = '0';
        }""")

        page.pdf(
            path=pdf_path,
            format='A4',
            print_background=True,
            margin={'top': '5mm', 'bottom': '5mm', 'left': '8mm', 'right': '8mm'}
        )
        
        # Também salva na pasta do portfolio_standalone para download online
        import shutil
        shutil.copy2(pdf_path, pdf_standalone)
        browser.close()

    print(f"Sucesso! PDF gerado em: {pdf_path}")
    print(f"Tamanho: {os.path.getsize(pdf_path)} bytes")

if __name__ == '__main__':
    generate_pdf()
