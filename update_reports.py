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
    pbi_1 = 'https://app.powerbi.com/view?r=eyJrIjoiMDExNTM1YTQtNDFmMS00MDQxLWI5MWItYmI5N2RjMTk0Mzk3IiwidCI6IjViMGFjOGQ1LTg0MjYtNDVlMC1iYmQzLTc0MmZmMDRkZTZlZCJ9'
    pbi_2 = 'https://app.powerbi.com/view?r=eyJrIjoiZTNkMjkxMzQtYWEyNC00ZjhkLWJmOTItMWI0OGJlOWYxNDgxIiwidCI6IjU3ZWRjNTZkLTgwNzUtNDQzMS04MWNkLWQxNDQ0YWY2Y2U0NiIsImMiOjF9'
    pbi_3 = 'https://app.powerbi.com/view?r=eyJrIjoiMTc2MWYxOTgtNTY3Ni00MzBhLTk2YzMtMTFmMzhmNmQyNWQ4IiwidCI6IjVlMDQxODhmLWEyY2MtNDlmNi1iMTYxLTIzYzg0Yzg4YTVhMiIsImMiOjl9'
    pbi_4 = 'https://app.powerbi.com/view?r=eyJrIjoiOGZjMDNmY2MtNzA4Ny00MDdmLTgzYzAtY2JlM2I0MjM1NzI4IiwidCI6IjE1ODMwOGZmLWI4NGEtNDcxMC1iZTIzLTY0NGM0NDcxNWU2YiIsImMiOjh9'

    log_reports = [
        ('Dashboard Logística — Ciclo do Pedido', 
         'DIR. DASH LOGISTICA CICLO DO PEDIDO: Acompanhamento de todas as etapas do pedido, lead time de separação, faturamento e expedição.', 
         dept_id, pbi_1, 'bi-arrow-repeat', 0, 1),

        ('Dashboard Logística — Demanda & Reabastecimento', 
         'DIR. DASH LOGISTICA DEMANDA REABASTECIMENTO: Planejamento e previsão de demanda, giro de estoque, ponto de reposição e controle de suprimentos.', 
         dept_id, pbi_2, 'bi-graph-up-arrow', 0, 2),

        ('Dashboard Logística — Inventário', 
         'DIR.DASH LOGISTICA INVENTARIO: Acuracidade de armazém, inventário físico rotativo x saldo contábil, perdas e auditoria de posições.', 
         dept_id, pbi_3, 'bi-boxes', 0, 3),

        ('Dashboard Logística — Total Express', 
         'DIR.DASH LOGISTICA TOTALEXPRESS: Indicadores de performance de fretes e transportadora Total Express, SLA de entregas e ocorrências de rastreamento.', 
         dept_id, pbi_4, 'bi-truck', 0, 4)
    ]

    for title, desc, did, url, icon, is_pub, order in log_reports:
        cursor.execute('''
            INSERT INTO reports (title, description, department_id, embed_url, icon, is_public, display_order, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        ''', (title, desc, did, url, icon, is_pub, order))

    conn.commit()
    print("Os 4 relatórios de Logística foram configurados com sucesso no banco!")
    conn.close()

if __name__ == '__main__':
    update_logistics_reports()
