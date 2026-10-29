import sqlite3

TITLE = 'Demandas de Reabastecimento do Estoque (Teste Copilot)'
URL = ('https://app.powerbi.com/reportEmbed?reportId=5a2a1ded-b800-406f-83ab-23a791544279'
       '&autoAuth=true&ctid=703fb3fc-27e0-412a-af01-fd5c3cd99e53')

conn = sqlite3.connect('intranet.db')
cur = conn.cursor()

cur.execute("SELECT id FROM departments WHERE code = 'logistica'")
dept_id = cur.fetchone()[0]

cur.execute("SELECT id FROM reports WHERE title = ?", (TITLE,))
row = cur.fetchone()

if row:
    print(f"Card de teste já existe com ID {row[0]}, atualizando URL...")
    cur.execute(
        "UPDATE reports SET embed_url = ?, icon = 'bi-boxes', active = 1, department_id = ? WHERE id = ?",
        (URL, dept_id, row[0]),
    )
else:
    cur.execute("SELECT COALESCE(MAX(display_order), 0) + 1 FROM reports WHERE department_id = ?", (dept_id,))
    order = cur.fetchone()[0]
    cur.execute("""
        INSERT INTO reports (
            title, description, department_id, embed_url, icon, is_public, display_order, active, created_at
        ) VALUES (?, ?, ?, ?, 'bi-boxes', 0, ?, 1, datetime('now', 'localtime'))
    """, (
        TITLE,
        'Card de teste: mesmo relatório de reabastecimento, com Copilot habilitado no embed.',
        dept_id,
        URL,
        order,
    ))
    print("Card de teste cadastrado! ID:", cur.lastrowid)

conn.commit()

cur.execute("SELECT id, title, display_order, embed_url FROM reports WHERE department_id = ? ORDER BY display_order", (dept_id,))
print("\n--- Relatórios atuais em Logística: ---")
for r in cur.fetchall():
    print(f"ID {r[0]}: {r[1]} | Ordem: {r[2]} | URL: {r[3]}")

conn.close()
