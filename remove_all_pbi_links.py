import re

# 1. Limpa templates/portfolio.html
with open('templates/portfolio.html', 'r', encoding='utf-8') as f:
    text = f.read()

text_clean = re.sub(r'https?://[^\s"\'<>]*powerbi\.com[^\s"\'<>]*', '#', text)
with open('templates/portfolio.html', 'w', encoding='utf-8') as f:
    f.write(text_clean)

# 2. Limpa portfolio_standalone/index.html
with open('portfolio_standalone/index.html', 'r', encoding='utf-8') as f:
    text_stand = f.read()

text_stand_clean = re.sub(r'https?://[^\s"\'<>]*powerbi\.com[^\s"\'<>]*', '#', text_stand)
with open('portfolio_standalone/index.html', 'w', encoding='utf-8') as f:
    f.write(text_stand_clean)

print("Verificação templates/portfolio.html:", text_clean.count("powerbi.com"))
print("Verificação portfolio_standalone/index.html:", text_stand_clean.count("powerbi.com"))
