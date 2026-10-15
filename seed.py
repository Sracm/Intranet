from database import (
    init_db, create_department, create_user, create_report, get_db
)

def run_seed():
    print("Iniciando banco de dados...")
    init_db()
    
    conn = get_db()
    user_count = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()['c']
    if user_count > 0:
        print("Banco de dados já possui dados. Ignorando seed para preservar registros.")
        conn.close()
        return

    print("Criando Departamentos padrão...")
    depts = [
        {
            'name': 'Logística',
            'code': 'logistica',
            'description': 'Gestão de fretes, expedição, devoluções, estoque e prazos de entrega.',
            'icon': 'bi-truck',
            'color': '#CB9727'
        },
        {
            'name': 'Comercial & Vendas',
            'code': 'comercial',
            'description': 'Acompanhamento de metas, faturamento por canal, pedidos e representantes.',
            'icon': 'bi-graph-up-arrow',
            'color': '#28A745'
        },
        {
            'name': 'Financeiro',
            'code': 'financeiro',
            'description': 'Fluxo de caixa, conciliação bancária, inadimplência e DRE gerencial.',
            'icon': 'bi-cash-coin',
            'color': '#0D6EFD'
        },
        {
            'name': 'Fiscal',
            'code': 'fiscal',
            'description': 'Auditoria de notas, tarefas fiscais, impostos e obrigações acessórias.',
            'icon': 'bi-receipt',
            'color': '#17A2B8'
        },
        {
            'name': 'Marketing',
            'code': 'marketing',
            'description': 'Campanhas digitais, conversão de e-commerce, CAC, ROAS e redes sociais.',
            'icon': 'bi-megaphone',
            'color': '#E83E8C'
        },
        {
            'name': 'TI & BI',
            'code': 'ti_bi',
            'description': 'Monitoramento de sistemas, pipelines de dados, governança e integrações.',
            'icon': 'bi-cpu',
            'color': '#6F42C1'
        },
        {
            'name': 'Cockpit Geral de Indicadores Estratégicos',
            'code': 'diretoria',
            'description': 'Cockpit executivo, KPIs estratégicos consolidados e margem líquida.',
            'icon': 'bi-briefcase',
            'color': '#FD7E14'
        },
        {
            'name': 'Regional FSP',
            'code': 'regional_fsp',
            'description': 'Gestão financeira, DRE e indicadores operacionais da Regional FSP.',
            'icon': 'bi-geo-alt-fill',
            'color': '#CB9727'
        },
        {
            'name': 'RH',
            'code': 'rh',
            'description': 'Gestão de Recursos Humanos e Indicadores de Pessoas.',
            'icon': 'bi-people-fill',
            'color': '#17A2B8'
        }
    ]

    dept_ids = {}
    for d in depts:
        d_id = create_department(d['name'], d['code'], d['description'], d['icon'], d['color'])
        dept_ids[d['code']] = d_id
        print(f" -> Depto: {d['name']} (ID: {d_id})")

    print("\nCriando Usuários iniciais...")
    # 1. Admin geral
    admin_id = create_user(
        username='admin',
        name='Administrador Geral MQ',
        email='admin@mqhair.com.br',
        password='admin',
        role='admin',
        department_id=dept_ids['ti_bi'],
        extra_dept_ids=list(dept_ids.values())
    )
    print(f" -> Usuário Admin criado (admin / admin) - ID {admin_id}")

    # 2. Usuário de Logística
    log_user_id = create_user(
        username='logistica',
        name='Equipe de Logística',
        email='logistica@mqhair.com.br',
        password='123',
        role='user',
        department_id=dept_ids['logistica'],
        extra_dept_ids=[dept_ids['logistica']]
    )
    print(f" -> Usuário Logística criado (logistica / 123) - ID {log_user_id}")

    # 3. Usuário Comercial
    com_user_id = create_user(
        username='comercial',
        name='Equipe Comercial',
        email='comercial@mqhair.com.br',
        password='123',
        role='user',
        department_id=dept_ids['comercial'],
        extra_dept_ids=[dept_ids['comercial']]
    )
    print(f" -> Usuário Comercial criado (comercial / 123) - ID {com_user_id}")

    # 4. Gestor Regional FSP (Ricardo Pavão)
    fsp_user_id = create_user(
        username='ricardo.pavao',
        name='Ricardo Pavão',
        email='ricardo.pavao@mqhair.com.br',
        password='123',
        role='user',
        department_id=dept_ids['regional_fsp'],
        extra_dept_ids=[dept_ids['regional_fsp'], dept_ids['comercial']]
    )
    print(f" -> Usuário Ricardo Pavão criado (ricardo.pavao / 123) - ID {fsp_user_id}")

    # 5. Gestora RH (Maria Macedo)
    maria_user_id = create_user(
        username='maria.macedo',
        name='Maria Macedo',
        email='maria.macedo@mqhair.com.br',
        password='123',
        role='user',
        department_id=dept_ids['rh'],
        extra_dept_ids=[dept_ids['rh']]
    )
    print(f" -> Usuária Maria Macedo criada (maria.macedo / 123) - ID {maria_user_id}")

    print("\nCriando Relatórios Power BI de demonstração...")
    # Power BI embed seguro ou link de publicação
    # Colocamos links de demonstração interativos do Power BI da Microsoft que abrem com perfeição
    sample_pbi_1 = "https://app.powerbi.com/reportEmbed?reportId=5a2a1ded-b800-406f-83ab-23a791544279&autoAuth=true&ctid=703fb3fc-27e0-412a-af01-fd5c3cd99e53"
    sample_pbi_2 = "https://app.powerbi.com/view?r=eyJrIjoiZTNkMjkxMzQtYWEyNC00ZjhkLWJmOTItMWI0OGJlOWYxNDgxIiwidCI6IjU3ZWRjNTZkLTgwNzUtNDQzMS04MWNkLWQxNDQ0YWY2Y2U0NiIsImMiOjF9"
    sample_pbi_3 = "https://app.powerbi.com/view?r=eyJrIjoiMTc2MWYxOTgtNTY3Ni00MzBhLTk2YzMtMTFmMzhmNmQyNWQ4IiwidCI6IjVlMDQxODhmLWEyY2MtNDlmNi1iMTYxLTIzYzg0Yzg4YTVhMiIsImMiOjl9"
    sample_pbi_4 = "https://app.powerbi.com/view?r=eyJrIjoiOGZjMDNmY2MtNzA4Ny00MDdmLTgzYzAtY2JlM2I0MjM1NzI4IiwidCI6IjE1ODMwOGZmLWI4NGEtNDcxMC1iZTIzLTY0NGM0NDcxNWU2YiIsImMiOjh9"

    reports = [
        {
            'title': 'Dashboard Logística — Ciclo do Pedido',
            'description': 'DIR. DASH LOGISTICA CICLO DO PEDIDO: Acompanhamento de todas as etapas do pedido, lead time de separação, faturamento e expedição.',
            'dept': 'logistica',
            'url': sample_pbi_1,
            'icon': 'bi-arrow-repeat',
            'is_public': 0,
            'order': 1
        },
        {
            'title': 'Dashboard Logística — Demanda & Reabastecimento',
            'description': 'DIR. DASH LOGISTICA DEMANDA REABASTECIMENTO: Planejamento e previsão de demanda, giro de estoque, ponto de reposição e controle de suprimentos.',
            'dept': 'logistica',
            'url': sample_pbi_2,
            'icon': 'bi-graph-up-arrow',
            'is_public': 0,
            'order': 2
        },
        {
            'title': 'Dashboard Logística — Inventário',
            'description': 'DIR.DASH LOGISTICA INVENTARIO: Acuracidade de armazém, inventário físico rotativo x saldo contábil, perdas e auditoria de posições.',
            'dept': 'logistica',
            'url': sample_pbi_3,
            'icon': 'bi-boxes',
            'is_public': 0,
            'order': 3
        },
        {
            'title': 'Dashboard Logística — Total Express',
            'description': 'DIR.DASH LOGISTICA TOTALEXPRESS: Indicadores de performance de fretes e transportadora Total Express, SLA de entregas e ocorrências de rastreamento.',
            'dept': 'logistica',
            'url': sample_pbi_4,
            'icon': 'bi-truck',
            'is_public': 0,
            'order': 4
        },
        {
            'title': 'Painel de Performance Comercial & Vendas B2B',
            'description': 'Faturamento por região, margem por produto, ranking de clientes e curva ABC de vendas.',
            'dept': 'comercial',
            'url': sample_pbi_3,
            'icon': 'bi-bar-chart-fill',
            'is_public': 0,
            'order': 3
        },
        {
            'title': 'Análise de Recorrência & Recompra de Clientes',
            'description': 'Ciclo de vida do cliente MQ, intervalo entre compras e retenção por canal de distribuição.',
            'dept': 'comercial',
            'url': sample_pbi_4,
            'icon': 'bi-arrow-repeat',
            'is_public': 0,
            'order': 4
        },
        {
            'title': 'Cockpit Geral de Indicadores Estratégicos MQ',
            'description': 'Visão macro corporativa com faturamento acumulado, pedidos totais e metas globais da empresa.',
            'dept': 'diretoria',
            'url': sample_pbi_1,
            'icon': 'bi-speedometer2',
            'is_public': 1, # Visível a todos os usuários
            'order': 0
        },
        {
            'title': 'Acompanhamento de Obrigações Fiscais e SPED',
            'description': 'Controle de prazos de entregas fiscais, conferência de XMLs e apuração de tributos.',
            'dept': 'fiscal',
            'url': sample_pbi_2,
            'icon': 'bi-file-earmark-check',
            'is_public': 0,
            'order': 5
        },
        {
            'title': 'DRE Regional FSP — Gestão de Resultados',
            'description': 'Demonstrativo de Resultados da Regional FSP (Distribuição 1020000, Varejo RJ 1010200, Varejo ND 1010300 e Varejo SUL 1010400). Acompanhamento de faturamento líquido, margens e custos operacionais.',
            'dept': 'regional_fsp',
            'url': 'http://localhost:5100/regional.fsp',
            'icon': 'bi-file-earmark-bar-graph-fill',
            'is_public': 0,
            'order': 1
        },
        {
            'title': 'DRE RH — Recursos Humanos',
            'description': 'Demonstrativo de Resultados do Exercício — Centro de Custo RH (9010000). Acompanhamento de despesas e custos operacionais de Recursos Humanos.',
            'dept': 'rh',
            'url': 'http://localhost:5100/rh',
            'icon': 'bi-people-fill',
            'is_public': 0,
            'order': 1
        },
        {
            'title': 'Dashboard Nubmetrics',
            'description': 'Inteligência de mercado, análise de vendas e indicadores competitivos Nubmetrics da Regional FSP.',
            'dept': 'regional_fsp',
            'url': 'https://app.powerbi.com/view?r=eyJrIjoiNWYzZmE0NTgtZTRmZS00OWVmLWE2M2YtYWRiMzJhMGRkNzE5IiwidCI6IjcwM2ZiM2ZjLTI3ZTAtNDEyYS1hZjAxLWZkNWMzY2Q5OWU1MyJ9',
            'icon': 'bi-graph-up-arrow',
            'is_public': 0,
            'order': 2
        }
    ]

    for r in reports:
        dept_id = dept_ids.get(r['dept'])
        if dept_id:
            rep_id = create_report(
                title=r['title'],
                description=r['description'],
                department_id=dept_id,
                embed_url=r['url'],
                icon=r['icon'],
                is_public=r['is_public'],
                display_order=r['order']
            )
            print(f" -> Relatório criado: {r['title']} (ID {rep_id})")

    conn.close()
    print("\nInicialização e Carga do banco concluída com sucesso!")

if __name__ == '__main__':
    run_seed()
