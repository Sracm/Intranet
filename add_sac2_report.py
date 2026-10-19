import sqlite3

conn = sqlite3.connect('intranet.db')
cur = conn.cursor()

# Verifica se o relatório já existe
cur.execute("SELECT id FROM reports WHERE title = 'Dashboard SAC & Assistencia Técnica 2'")
row = cur.fetchone()

if row:
    print(f"Relatório já existe com ID {row[0]}, atualizando URL e configurações...")
    cur.execute("""
        UPDATE reports 
        SET embed_url = 'http://localhost:5300/', 
            icon = 'bi-headset', 
            active = 1,
            department_id = 14
        WHERE id = ?
    """, (row[0],))
else:
    # Ajusta a ordem para ficar logo após o relatório 40 (display_order = 4)
    cur.execute("UPDATE reports SET display_order = display_order + 1 WHERE department_id = 14 AND display_order >= 4")
    cur.execute("""
        INSERT INTO reports (
            title, description, department_id, embed_url, icon, is_public, display_order, active, created_at
        ) VALUES (
            'Dashboard SAC & Assistencia Técnica 2',
            'Cockpit Executivo & Operacional da Diretoria de Assistência Técnica & SAC (Versão Web). Indicadores de WhatsApp/CRC, Fale Conosco, CSAT/NPS e Ordens de Serviço.',
            14,
            'http://localhost:5300/',
            'bi-headset',
            0,
            4,
            1,
            datetime('now', 'localtime')
        )
    """)
    print("Relatório 'Dashboard SAC & Assistencia Técnica 2' cadastrado com sucesso! ID:", cur.lastrowid)

conn.commit()

# Exibe todos os relatórios do departamento 14 para validação
cur.execute("SELECT id, title, department_id, embed_url, display_order FROM reports WHERE department_id = 14 ORDER BY display_order")
print("\n--- Relatórios atuais em Assistência Técnica & SAC (Dept 14): ---")
for r in cur.fetchall():
    print(f"ID {r[0]}: {r[1]} | Ordem: {r[4]} | URL: {r[3]}")

conn.close()
