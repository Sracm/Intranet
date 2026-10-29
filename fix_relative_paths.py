import os

# Corrige caminho absoluto /static/ para caminho relativo static/
file_path = 'portfolio_standalone/index.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Substitui tanto no JSON quanto nos fallbacks e botões
fixed_content = content.replace('"/static/portfolio_screenshots/', '"static/portfolio_screenshots/')
fixed_content = fixed_content.replace("'/static/portfolio_screenshots/", "'static/portfolio_screenshots/")

# Corrige também no template local
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(fixed_content)

with open('templates/portfolio.html', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("Caminhos de imagem corrigidos para caminhos relativos no GitHub Pages!")
print("Ocorrências de '/static/':", fixed_content.count("'/static/"))
print("Ocorrências de '\"/static/':", fixed_content.count('"/static/'))
