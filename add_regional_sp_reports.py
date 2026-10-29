import sys
import os
import sqlite3

BASE_DIR = r'c:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\ANTIGRAVITY\PROJETOS\INTRANET'
sys.path.append(BASE_DIR)
os.chdir(BASE_DIR)

from database import get_db

REPORTS = [
    {
        'title': 'DRE Regional SP – Gestão de Resultados',
        'desc': 'Demonstrativo de Resultados do Exercício (DRE) consolidado da Regional SP.',
        'url': 'http://10.11.1.162:5100/regional.sp',
        'icon': 'bi-file-earmark-bar-graph-fill',
        'order': 1
    },
    {
        'title': 'DASH. EVOLUÇÃO REDE E PROD. VISÃO  GER. REGIONAL SP',
        'desc': 'Evolução de vendas da rede e de produtos com visão gerencial da Regional SP.',
        'url': 'https://app.powerbi.com/reportEmbed?reportId=4931fe22-c166-4658-a0b0-778be3644d6d&autoAuth=true&ctid=703fb3fc-27e0-412a-af01-fd5c3cd99e53&actionBarEnabled=true',
        'icon': 'bi-diagram-3-fill',
        'order': 2
    },
    {
        'title': 'DIR CML DASH. PROFUNDIDADE - MIX- CARTEIRA REGIONAL SP',
        'desc': 'Análise profunda de mix de produtos, positivação e carteira de clientes da Regional SP.',
        'url': 'https://app.powerbi.com/reportEmbed?reportId=363159d6-da35-4143-8da1-218e3c4bdfab&autoAuth=true&ctid=703fb3fc-27e0-412a-af01-fd5c3cd99e53&actionBarEnabled=true',
        'icon': 'bi-pie-chart-fill',
        'order': 3
    },
    {
        'title': 'DIR. CML  VAREJO ESPECIALIZADO GESTOR SP.',
        'desc': 'Gestão e indicadores de vendas no canal Varejo Especializado da Regional SP.',
        'url': 'https://app.powerbi.com/reportEmbed?reportId=1d1c0a10-296e-4af8-998d-b3d4a4e57347&autoAuth=true&ctid=703fb3fc-27e0-412a-af01-fd5c3cd99e53&actionBarEnabled=true',
        'icon': 'bi-shop',
        'order': 4
    },
    {
        'title': 'DIR. CML. ACOMP. PERF. PRODUTO E CANAL REG.SP',
        'desc': 'Acompanhamento detalhado de performance por linha de produto e canal comercial.',
        'url': 'https://app.powerbi.com/reportEmbed?reportId=60954639-0a84-4e5f-85c2-f99b9c6857b3&autoAuth=true&ctid=703fb3fc-27e0-412a-af01-fd5c3cd99e53&actionBarEnabled=true',
        'icon': 'bi-bar-chart-line-fill',
        'order': 5
    },
    {
        'title': 'SELLOUT  PROMOTOR',
        'desc': 'Performance e acompanhamento do volume de sell-out registrado pelos promotores de vendas.',
        'url': 'https://app.powerbi.com/reportEmbed?reportId=0f33e57c-8f3d-4703-89e9-44d1c92e37ea&autoAuth=true&ctid=703fb3fc-27e0-412a-af01-fd5c3cd99e53&actionBarEnabled=true',
        'icon': 'bi-person-check-fill',
        'order': 6
    },
    {
        'title': 'SHOPPING PREÇO',
        'desc': 'Inteligência competitiva, monitoramento e comparativo de preços de mercado (Shopping Preço).',
        'url': 'https://app.powerbi.com/reportEmbed?reportId=a90031fa-3505-4b0d-8816-801d7d465385&autoAuth=true&ctid=703fb3fc-27e0-412a-af01-fd5c3cd99e53&actionBarEnabled=true',
        'icon': 'bi-cart-check-fill',
        'order': 7
    },
    {
        'title': 'Dashboard Guelta (Ação Promocional AP)',
        'desc': 'Inteligência executiva da campanha promocional Guelta (AP), vendas por loja, revendedora e produtos.',
        'url': 'http://10.11.1.100:5250/',
        'icon': 'bi-award-fill',
        'order': 8
    }
]

print("=== 1. ATUALIZANDO BANCO ATIVO (MARIADB) ===")
conn_active = get_db()
cur_active = conn_active.cursor()

cur_active.execute("SELECT id, code, name FROM departments WHERE code = ?", ('regional_sp',))
dept_active = cur_active.fetchone()
dept_active_id = dept_active['id'] if isinstance(dept_active, dict) else dept_active[0]
print(f"Departamento Regional SP ID no MariaDB: {dept_active_id}")

for rep in REPORTS:
    # Procura pelo título exato ou variações aproximadas
    title_key = rep['title'].replace('  ', ' ').strip()
    cur_active.execute("SELECT id, title FROM reports WHERE department_id = ? AND (title = ? OR title LIKE ?)",
                      (dept_active_id, rep['title'], f"{title_key[:15]}%"))
    existing = cur_active.fetchone()
    
    if existing:
        rep_id = existing['id'] if isinstance(existing, dict) else existing[0]
        cur_active.execute("""
            UPDATE reports 
            SET title = ?, description = ?, embed_url = ?, icon = ?, display_order = ?, active = 1 
            WHERE id = ?
        """, (rep['title'], rep['desc'], rep['url'], rep['icon'], rep['order'], rep_id))
        print(f" [OK UPDATE MariaDB] ID {rep_id}: {rep['title']}")
    else:
        cur_active.execute("""
            INSERT INTO reports (title, description, department_id, embed_url, icon, is_public, display_order, active)
            VALUES (?, ?, ?, ?, ?, 0, ?, 1)
        """, (rep['title'], rep['desc'], dept_active_id, rep['url'], rep['icon'], rep['order']))
        print(f" [OK INSERT MariaDB] {rep['title']}")

conn_active.commit()
conn_active.close()

print("\n=== 2. ATUALIZANDO SQLITE LOCAL (intranet.db) ===")
conn_sqlite = sqlite3.connect(os.path.join(BASE_DIR, 'intranet.db'))
conn_sqlite.row_factory = sqlite3.Row
cur_sqlite = conn_sqlite.cursor()

cur_sqlite.execute("SELECT id FROM departments WHERE code = 'regional_sp'")
dept_sqlite = cur_sqlite.fetchone()
dept_sqlite_id = dept_sqlite['id']
print(f"Departamento Regional SP ID no SQLite: {dept_sqlite_id}")

for rep in REPORTS:
    title_key = rep['title'].replace('  ', ' ').strip()
    cur_sqlite.execute("SELECT id FROM reports WHERE department_id = ? AND (title = ? OR title LIKE ?)",
                       (dept_sqlite_id, rep['title'], f"{title_key[:15]}%"))
    existing = cur_sqlite.fetchone()
    
    if existing:
        rep_id = existing['id']
        cur_sqlite.execute("""
            UPDATE reports 
            SET title = ?, description = ?, embed_url = ?, icon = ?, display_order = ?, active = 1 
            WHERE id = ?
        """, (rep['title'], rep['desc'], rep['url'], rep['icon'], rep['order'], rep_id))
        print(f" [OK UPDATE SQLite] ID {rep_id}: {rep['title']}")
    else:
        cur_sqlite.execute("""
            INSERT INTO reports (title, description, department_id, embed_url, icon, is_public, display_order, active)
            VALUES (?, ?, ?, ?, ?, 0, ?, 1)
        """, (rep['title'], rep['desc'], dept_sqlite_id, rep['url'], rep['icon'], rep['order']))
        print(f" [OK INSERT SQLite] {rep['title']}")

conn_sqlite.commit()
conn_sqlite.close()

print("\nTODOS OS 8 DASHBOARDS DA REGIONAL SP FORAM ATUALIZADOS COM SUCESSO!")
