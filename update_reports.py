import sqlite3

def update_logistics_reports():
    conn = sqlite3.connect('intranet.db')
    cursor = conn.cursor()

    log_dept = cursor.execute("SELECT id FROM departments WHERE code = 'logistica'").fetchone()
    if not log_dept:
        print("Departamento logística não encontrado!")
        conn.close()
        return

    dept_id = log_dept[0]

    # Remove relatórios antigos de logística
    cursor.execute("DELETE FROM reports WHERE department_id = ?", (dept_id,))

    # Power BI URLs
    pbi_ciclo = 'https://app.powerbi.com/view?r=eyJrIjoiOTQ3YzUyZWMtYzM2YS00NWE0LWE0MmYtY2U2YzcxMjgxZmI3IiwidCI6IjcwM2ZiM2ZjLTI3ZTAtNDEyYS1hZjAxLWZkNWMzY2Q5OWU1MyJ9'
    pbi_inventario = 'https://app.powerbi.com/view?r=eyJrIjoiNzA1YWI0YjctMDhiNC00MjQzLWJiMDYtYzdkZjA1NTg2YTE5IiwidCI6IjcwM2ZiM2ZjLTI3ZTAtNDEyYS1hZjAxLWZkNWMzY2Q5OWU1MyJ9'
    pbi_reabastecimento = 'https://app.powerbi.com/reportEmbed?reportId=5a2a1ded-b800-406f-83ab-23a791544279&autoAuth=true&ctid=703fb3fc-27e0-412a-af01-fd5c3cd99e53&actionBarEnabled=true'
    pbi_dre = 'http://localhost:5150/dre-empresa'

    log_reports = [
        ('DRE Logística',
         'Demonstrativo de Resultados - Logística',
         dept_id, pbi_dre, 'bi-cash-coin', 0, 1),

        ('Demandas de Reabastecimento do Estoque',
         'Acompanhamento de demandas e reabastecimento de estoque',
         dept_id, pbi_reabastecimento, 'bi-box-seam', 0, 2),

        ('Dashboard Logística — Ciclo do Pedido', 
         'DIR. DASH LOGISTICA CICLO DO PEDIDO: Acompanhamento de todas as etapas do pedido, lead time de separação, faturamento e expedição.', 
         dept_id, pbi_ciclo, 'bi-arrow-repeat', 0, 3),

        ('Dashboard Logística — Inventário', 
         'DIR.DASH LOGISTICA INVENTARIO: Acuracidade de armazém, inventário físico rotativo x saldo contábil, perdas e auditoria de posições.', 
         dept_id, pbi_inventario, 'bi-boxes', 0, 4)
    ]

    for title, desc, did, url, icon, is_pub, order in log_reports:
        cursor.execute('''
            INSERT INTO reports (title, description, department_id, embed_url, icon, is_public, display_order, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        ''', (title, desc, did, url, icon, is_pub, order))

    conn.commit()
    print("Os relatórios de Logística foram configurados com sucesso no banco!")
    conn.close()

if __name__ == '__main__':
    update_logistics_reports()
