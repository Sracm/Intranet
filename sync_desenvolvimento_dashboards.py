import sqlite3
import pymysql
from config import Config

REPORTS_DATA = [
    {
        'title': 'DRE Desenvolvimento de Produtos',
        'desc': 'Demonstrativo de Resultados do Exercício (DRE) da linha de desenvolvimento de produtos e projetos.',
        'url': 'http://10.11.1.162:5100/produto',
        'icon': 'bi-file-earmark-bar-graph-fill',
        'order': 1,
        'alt_titles': ['DRE Desenvolvimento de Produtos']
    },
    {
        'title': 'DASH. DESENV. PRODUTOS INDICADORES DE IMPORTACAO',
        'desc': 'Indicadores de importação, lead time, custos e desembaraço de produtos.',
        'url': 'https://app.powerbi.com/view?r=eyJrIjoiM2QyOGQyMWQtM2EyYy00MzQ1LTg4MTEtNzI3NjVkYWFkY2I5IiwidCI6IjcwM2ZiM2ZjLTI3ZTAtNDEyYS1hZjAxLWZkNWMzY2Q5OWU1MyJ9',
        'icon': 'bi-globe2',
        'order': 2,
        'alt_titles': ['DASH. DESENV. PRODUTOS INDICADORES DE IMPORTACAO', 'DASH. DESENV. PRODUTOS INDICADORES DE IMPORTAÇÃO', 'INDICADORES DE IMPORTACAO']
    },
    {
        'title': 'Dashboard Nubmetrics',
        'desc': 'Inteligência de mercado, vendas e posicionamento competitivo via Nubmetrics.',
        'url': 'https://app.powerbi.com/view?r=eyJrIjoiMzgxOTBiZGQtYzM1Ni00ZjJkLThhN2EtZGNlMTVlODk5NjNjIiwidCI6IjcwM2ZiM2ZjLTI3ZTAtNDEyYS1hZjAxLWZkNWMzY2Q5OWU1MyJ9',
        'icon': 'bi-bar-chart-line-fill',
        'order': 3,
        'alt_titles': ['Dashboard Nubmetrics', 'DASH. DIR. DESNV. PRODUTOS - NUBMETRICS']
    },
    {
        'title': 'DASH. DIR. DESNV. PRODUTOS - NUBMETRICS 10',
        'desc': 'Dashboard executivo da Diretoria de Desenvolvimento de Produtos - Nubmetrics (versão 10).',
        'url': 'https://app.powerbi.com/view?r=eyJrIjoiNmRjODc4ZDctNDczNS00OGM0LWE3NWEtZTg2ZTViMWUzZGYwIiwidCI6IjcwM2ZiM2ZjLTI3ZTAtNDEyYS1hZjAxLWZkNWMzY2Q5OWU1MyJ9',
        'icon': 'bi-graph-up-arrow',
        'order': 4,
        'alt_titles': ['DASH. DIR. DESNV. PRODUTOS - NUBMETRICS 10']
    },
    {
        'title': 'DIR. ASSISTEC. DASHBOARD FORECAST SPARE_PARTS vs05',
        'desc': 'Forecast e projeção de demanda de peças de reposição (Spare Parts) da Assistência Técnica.',
        'url': 'https://app.powerbi.com/view?r=eyJrIjoiNGI3YTM1MjctMzIyOC00OTU5LWFhOWItNmY3OGYxNmYxMDdjIiwidCI6IjcwM2ZiM2ZjLTI3ZTAtNDEyYS1hZjAxLWZkNWMzY2Q5OWU1MyJ9',
        'icon': 'bi-tools',
        'order': 5,
        'alt_titles': ['DIR. ASSISTEC. DASHBOARD FORECAST SPARE_PARTS vs05']
    },
    {
        'title': 'DIR. ASSISTEC. DASHBOARD RA',
        'desc': 'Gestão de chamados, reputação e índices de atendimento no Reclame Aqui da Assistência Técnica.',
        'url': 'https://app.powerbi.com/view?r=eyJrIjoiMjkyNTg3NjAtYjUwMi00YTk0LWIyZmMtNmEyMjI2MGRhYWExIiwidCI6IjcwM2ZiM2ZjLTI3ZTAtNDEyYS1hZjAxLWZkNWMzY2Q5OWU1MyJ9',
        'icon': 'bi-shield-check',
        'order': 6,
        'alt_titles': ['DIR. ASSISTEC. DASHBOARD RA']
    },
    {
        'title': 'DIR.CML ESTOQUE ATUAL CUSTO FINANCEIRO',
        'desc': 'Estoque atual e custo financeiro consolidado - Diretoria Comercial e Desenvolvimento.',
        'url': 'https://app.powerbi.com/view?r=eyJrIjoiNmRjMjFjYzctMjAzZS00NmU3LWI3ODAtODQxYmJhODI1MTk2IiwidCI6IjcwM2ZiM2ZjLTI3ZTAtNDEyYS1hZjAxLWZkNWMzY2Q5OWU1MyJ9',
        'icon': 'bi-boxes',
        'order': 7,
        'alt_titles': ['DIR.CML ESTOQUE ATUAL CUSTO FINANCEIRO', 'DIR.CML ESTOQUE ATUAL CUSTO FINANCEIRO v6']
    },
    {
        'title': 'DIR.DASH. ANALISE MARGEM CUSTO GER vs5',
        'desc': 'Análise gerencial de margens, composição de custos e rentabilidade de produtos.',
        'url': 'https://app.powerbi.com/view?r=eyJrIjoiZDhhODA0ODAtMDI5Ny00NDA1LWExMmMtNDAzOTQxMzBjMWRlIiwidCI6IjcwM2ZiM2ZjLTI3ZTAtNDEyYS1hZjAxLWZkNWMzY2Q5OWU1MyJ9',
        'icon': 'bi-percent',
        'order': 8,
        'alt_titles': ['DIR.DASH. ANALISE MARGEM CUSTO GER vs5']
    },
    {
        'title': 'RETORNO DE PEÇAS.',
        'desc': 'Controle, índices de retorno e conformidade de peças em garantia.',
        'url': 'https://app.powerbi.com/view?r=eyJrIjoiMWY0NGM2NzEtZWNjOS00YmEwLTliZDUtMjNmZjZiYThiYzVlIiwidCI6IjcwM2ZiM2ZjLTI3ZTAtNDEyYS1hZjAxLWZkNWMzY2Q5OWU1MyJ9',
        'icon': 'bi-arrow-return-left',
        'order': 9,
        'alt_titles': ['RETORNO DE PEÇAS.', 'RETORNO DE PEÇAS', 'RETORNO DE PEÇAS.v10']
    },
    {
        'title': 'SHOPPING PREÇO',
        'desc': 'Comparativo dinâmico de preços de produtos no mercado (Shopping de Preço).',
        'url': 'https://app.powerbi.com/view?r=eyJrIjoiNzEyM2M3OWUtNDUyOS00MGY4LThmNjItMjc0MDA0MDU5NTRjIiwidCI6IjcwM2ZiM2ZjLTI3ZTAtNDEyYS1hZjAxLWZkNWMzY2Q5OWU1MyJ9',
        'icon': 'bi-cart-check-fill',
        'order': 10,
        'alt_titles': ['SHOPPING PREÇO', 'SHOPPING PREÇO2']
    },
    {
        'title': 'TESTE PREDITIVOS.',
        'desc': 'Painel de modelos preditivos e testes estatísticos para desenvolvimento de produtos.',
        'url': 'https://app.powerbi.com/view?r=eyJrIjoiYTgyNDhiMTAtODdiNC00YzcxLWE5MTAtNGYyOTVkMjhkMzdhIiwidCI6IjcwM2ZiM2ZjLTI3ZTAtNDEyYS1hZjAxLWZkNWMzY2Q5OWU1MyJ9',
        'icon': 'bi-cpu-fill',
        'order': 11,
        'alt_titles': ['TESTE PREDITIVOS.', 'TESTE PREDITIVOS']
    }
]

def sync_sqlite():
    print("\n================== SINCRONIZANDO SQLITE (intranet.db) ==================")
    conn = sqlite3.connect('intranet.db')
    cur = conn.cursor()
    
    # Busca depto desenvolvimento
    dept = cur.execute("SELECT id FROM departments WHERE code = 'desenvolvimento'").fetchone()
    if not dept:
        print("[ERRO] Departamento desenvolvimento não encontrado no SQLite!")
        conn.close()
        return
    dept_id = dept[0]
    
    # Atualiza nome do departamento para 'Desenvolvimento de Produtos & Projetos'
    cur.execute("UPDATE departments SET name = 'Desenvolvimento de Produtos & Projetos' WHERE id = ?", (dept_id,))
    print("-> Nome do departamento atualizado para 'Desenvolvimento de Produtos & Projetos'")
    
    # Garante permissões em user_departments para admin e antonio.mello se existirem
    for username in ['admin', 'antonio.mello', 'thiago.figueiredo']:
        u = cur.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if u:
            u_id = u[0]
            cur.execute("INSERT OR IGNORE INTO user_departments (user_id, department_id) VALUES (?, ?)", (u_id, dept_id))
            print(f"-> Permissão de acesso garantida para '{username}' (ID {u_id})")
            
    # Processa os relatórios
    for rep in REPORTS_DATA:
        title = rep['title']
        desc = rep['desc']
        url = rep['url']
        icon = rep['icon']
        order = rep['order']
        
        # Procura se já existe por algum dos alt_titles
        placeholders = ','.join(['?'] * len(rep['alt_titles']))
        params = list(rep['alt_titles']) + [dept_id]
        existing = cur.execute(f"SELECT id, title FROM reports WHERE title IN ({placeholders}) AND department_id = ?", params).fetchone()
        
        if existing:
            rep_id = existing[0]
            cur.execute("""
                UPDATE reports 
                SET title = ?, description = ?, embed_url = ?, icon = ?, display_order = ?, active = 1
                WHERE id = ?
            """, (title, desc, url, icon, order, rep_id))
            print(f"-> [UPDATE] {title} (ID {rep_id})")
        else:
            cur.execute("""
                INSERT INTO reports (title, description, department_id, embed_url, icon, is_public, display_order, active)
                VALUES (?, ?, ?, ?, ?, 0, ?, 1)
            """, (title, desc, dept_id, url, icon, order))
            print(f"-> [INSERT] {title}")
            
    conn.commit()
    print("--- Relatórios em Desenvolvimento no SQLite ---")
    for r in cur.execute("SELECT id, title, display_order, embed_url FROM reports WHERE department_id = ? ORDER BY display_order", (dept_id,)):
        print(r)
    conn.close()

def sync_mariadb():
    print("\n================== SINCRONIZANDO MARIADB ==================")
    try:
        conn = pymysql.connect(
            host=Config.MARIADB_HOST,
            user=Config.MARIADB_USER,
            password=Config.MARIADB_PASSWORD,
            database=Config.MARIADB_DB,
            port=Config.MARIADB_PORT,
            connect_timeout=3,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as e:
        print(f"[AVISO] Não foi possível conectar ao MariaDB: {e}")
        return

    cur = conn.cursor()
    
    # Busca depto desenvolvimento
    cur.execute("SELECT id FROM departments WHERE code = 'desenvolvimento'")
    dept = cur.fetchone()
    if not dept:
        print("[ERRO] Departamento desenvolvimento não encontrado no MariaDB!")
        conn.close()
        return
    dept_id = dept['id']
    
    # Atualiza nome do departamento para 'Desenvolvimento de Produtos & Projetos'
    cur.execute("UPDATE departments SET name = 'Desenvolvimento de Produtos & Projetos' WHERE id = %s", (dept_id,))
    print("-> Nome do departamento atualizado para 'Desenvolvimento de Produtos & Projetos'")
    
    # Garante permissões em user_departments para admin e antonio.mello se existirem
    for username in ['admin', 'antonio.mello', 'thiago.figueiredo']:
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        u = cur.fetchone()
        if u:
            u_id = u['id']
            cur.execute("INSERT IGNORE INTO user_departments (user_id, department_id) VALUES (%s, %s)", (u_id, dept_id))
            print(f"-> Permissão de acesso garantida para '{username}' (ID {u_id})")
            
    # Processa os relatórios
    for rep in REPORTS_DATA:
        title = rep['title']
        desc = rep['desc']
        url = rep['url']
        icon = rep['icon']
        order = rep['order']
        
        # Procura se já existe por algum dos alt_titles
        format_strings = ','.join(['%s'] * len(rep['alt_titles']))
        params = list(rep['alt_titles']) + [dept_id]
        cur.execute(f"SELECT id, title FROM reports WHERE title IN ({format_strings}) AND department_id = %s", params)
        existing = cur.fetchone()
        
        if existing:
            rep_id = existing['id']
            cur.execute("""
                UPDATE reports 
                SET title = %s, description = %s, embed_url = %s, icon = %s, display_order = %s, active = 1
                WHERE id = %s
            """, (title, desc, url, icon, order, rep_id))
            print(f"-> [UPDATE] {title} (ID {rep_id})")
        else:
            cur.execute("""
                INSERT INTO reports (title, description, department_id, embed_url, icon, is_public, display_order, active)
                VALUES (%s, %s, %s, %s, %s, 0, %s, 1)
            """, (title, desc, dept_id, url, icon, order))
            print(f"-> [INSERT] {title}")
            
    conn.commit()
    print("--- Relatórios em Desenvolvimento no MariaDB ---")
    cur.execute("SELECT id, title, display_order, embed_url FROM reports WHERE department_id = %s ORDER BY display_order", (dept_id,))
    for r in cur.fetchall():
        print(f"[{r['id']}] (Ordem: {r['display_order']}) {r['title']} -> {r['embed_url']}")
    conn.close()

if __name__ == '__main__':
    sync_sqlite()
    sync_mariadb()
