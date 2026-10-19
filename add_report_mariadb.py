from database import get_db, create_report, update_report

conn = get_db()
cur = conn.cursor()
cur.execute("SELECT id FROM reports WHERE title = 'Dashboard SAC & Assistencia Técnica 2' AND department_id = 14")
row = cur.fetchone()
conn.close()

if row:
    rep_id = row['id'] if isinstance(row, dict) else row[0]
    print('Atualizando relatório existente ID:', rep_id)
    update_report(
        report_id=rep_id,
        title='Dashboard SAC & Assistencia Técnica 2',
        description='Cockpit Executivo & Operacional da Diretoria de Assistência Técnica & SAC (Versão Web). Indicadores de WhatsApp/CRC, Fale Conosco, CSAT/NPS e Ordens de Serviço.',
        department_id=14,
        embed_url='http://localhost:5300/',
        icon='bi-headset',
        is_public=0,
        display_order=4,
        active=1
    )
else:
    rep_id = create_report(
        title='Dashboard SAC & Assistencia Técnica 2',
        description='Cockpit Executivo & Operacional da Diretoria de Assistência Técnica & SAC (Versão Web). Indicadores de WhatsApp/CRC, Fale Conosco, CSAT/NPS e Ordens de Serviço.',
        department_id=14,
        embed_url='http://localhost:5300/',
        icon='bi-headset',
        is_public=0,
        display_order=4,
        active=1
    )
    print('Novo relatório criado no MariaDB com ID:', rep_id)

# Consulta para confirmar
conn2 = get_db()
cur2 = conn2.cursor()
cur2.execute("SELECT id, title, department_id, embed_url, display_order FROM reports WHERE department_id = 14 ORDER BY display_order ASC")
rows = cur2.fetchall()
print("\n--- Relatórios em Assistência Técnica & SAC (MariaDB): ---")
for r in rows:
    print(r)
conn2.close()
