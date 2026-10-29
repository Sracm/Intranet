import os
import re

templates_dir = r"C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\ANTIGRAVITY\PROJETOS\DASHBOARD_tv\templates"
count = 0
for f in os.listdir(templates_dir):
    if f.endswith('.html'):
        p = os.path.join(templates_dir, f)
        txt = open(p, 'r', encoding='utf-8', errors='ignore').read()
        if 'tv_rotator.js' in txt:
            new_txt = re.sub(r'tv_rotator\.js(\?[^"\'\s>]*)?', 'tv_rotator.js?v=20261027_vh', txt)
            if new_txt != txt:
                open(p, 'w', encoding='utf-8').write(new_txt)
                print(f"Bumped tv_rotator version in: {f}")
                count += 1

print(f"Total de templates atualizados: {count}")
