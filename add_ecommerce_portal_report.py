import sqlite3
from database import get_db, create_report, update_report
from config import Config

REPORT_TITLE = 'Portal Corporativo • E-Commerce'
REPORT_DESC = 'Cockpit executivo e acompanhamento diário de vendas, projeções e metas por canal: Mercado Livre, VTEX, Shopee, Magalu e Parlux.'
DEPT_ID = 11  # E-commerce
EMBED_URL = 'http://localhost:5200/'
ICON = 'bi-cart-check'
IS_PUBLIC = 0
ACTIVE = 1
DISPLAY_ORDER = -1

print("--- 1. ATUALIZANDO MARIADB ---")
try:
    conn_maria = get_db()
    cur_maria = conn_maria.cursor()
    
    # Verifica se já existe
    cur_maria.execute("SELECT id FROM reports WHERE title = ? AND department_id = ?", (REPORT_TITLE, DEPT_ID))
    row_maria = cur_maria.fetchone()
    
    # Ajusta display_order dos outros relatórios no MariaDB para não colidir
    cur_maria.execute("UPDATE reports SET display_order = display_order + 1 WHERE department_id = ? AND display_order >= ? AND title != ?", (DEPT_ID, DISPLAY_ORDER, REPORT_TITLE))
    conn_maria.commit()

    if row_maria:
        rep_id_maria = row_maria['id'] if isinstance(row_maria, dict) else row_maria[0]
        print(f"Relatório já existe no MariaDB (ID: {rep_id_maria}). Atualizando...")
        update_report(
            report_id=rep_id_maria,
            title=REPORT_TITLE,
            description=REPORT_DESC,
            department_id=DEPT_ID,
            embed_url=EMBED_URL,
            icon=ICON,
            is_public=IS_PUBLIC,
            display_order=DISPLAY_ORDER,
            active=ACTIVE
        )
    else:
        rep_id_maria = create_report(
            title=REPORT_TITLE,
            description=REPORT_DESC,
            department_id=DEPT_ID,
            embed_url=EMBED_URL,
            icon=ICON,
            is_public=IS_PUBLIC,
            display_order=DISPLAY_ORDER,
            active=ACTIVE
        )
        print(f"Novo relatório criado no MariaDB (ID: {rep_id_maria})")
    
    # Listar relatórios do Dept 11 no MariaDB
    cur_maria.execute("SELECT id, title, department_id, embed_url, icon, display_order, active FROM reports WHERE department_id = ? ORDER BY display_order ASC", (DEPT_ID,))
    print("\nRelatórios Dept 11 no MariaDB:")
    for r in cur_maria.fetchall():
        print(r)
    conn_maria.close()
except Exception as e:
    print("Erro ao atualizar MariaDB:", e)

print("\n--- 2. ATUALIZANDO SQLITE (intranet.db) ---")
try:
    conn_sq = sqlite3.connect('intranet.db')
    cur_sq = conn_sq.cursor()
    
    # Verifica se já existe
    cur_sq.execute("SELECT id FROM reports WHERE title = ? AND department_id = ?", (REPORT_TITLE, DEPT_ID))
    row_sq = cur_sq.fetchone()
    
    # Ajusta display_order dos outros relatórios no SQLite
    cur_sq.execute("UPDATE reports SET display_order = display_order + 1 WHERE department_id = ? AND display_order >= ? AND title != ?", (DEPT_ID, DISPLAY_ORDER, REPORT_TITLE))
    
    if row_sq:
        rep_id_sq = row_sq[0]
        print(f"Relatório já existe no SQLite (ID: {rep_id_sq}). Atualizando...")
        cur_sq.execute("""
            UPDATE reports
            SET title = ?, description = ?, department_id = ?, embed_url = ?, icon = ?, is_public = ?, display_order = ?, active = ?
            WHERE id = ?
        """, (REPORT_TITLE, REPORT_DESC, DEPT_ID, EMBED_URL, ICON, IS_PUBLIC, DISPLAY_ORDER, ACTIVE, rep_id_sq))
    else:
        cur_sq.execute("""
            INSERT INTO reports (title, description, department_id, embed_url, icon, is_public, display_order, active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
        """, (REPORT_TITLE, REPORT_DESC, DEPT_ID, EMBED_URL, ICON, IS_PUBLIC, DISPLAY_ORDER, ACTIVE))
        rep_id_sq = cur_sq.lastrowid
        print(f"Novo relatório criado no SQLite (ID: {rep_id_sq})")
        
    conn_sq.commit()
    
    cur_sq.execute("SELECT id, title, department_id, embed_url, icon, display_order, active FROM reports WHERE department_id = ? ORDER BY display_order ASC", (DEPT_ID,))
    print("\nRelatórios Dept 11 no SQLite:")
    for r in cur_sq.fetchall():
        print(f"ID {r[0]}: {r[1]} | Ordem: {r[5]} | URL: {r[3]} | Ícone: {r[4]}")
    conn_sq.close()
except Exception as e:
    print("Erro ao atualizar SQLite:", e)
