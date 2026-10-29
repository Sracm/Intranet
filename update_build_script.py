with open('build_github_dashboards_standalone.py', 'r', encoding='utf-8') as f:
    c = f.read()

target = '''    # Captura respostas reais da API local :5200 para os meses principais de 2026
    resumo_map = {}
    for m in [8, 9, 10]:
        data = fetch_json(f"http://localhost:5200/api/resumo?anos=2026&meses={m}&dia_ini=1&dia_fim=31&marca=Todas&force=false")
        if data and data.get("status") == "success":
            resumo_map[f"2026_{m}_Todas"] = data
            print(f"   -> Capturado E-commerce 2026/{m}")'''

replacement = '''    # Captura respostas reais da API local :5200 para os meses principais de 2026
    resumo_map = {}
    from datetime import datetime
    hoje = datetime.now()
    for m in [8, 9, 10]:
        dfim = hoje.day if m == hoje.month else (30 if m in (4, 6, 9, 11) else 31)
        data = fetch_json(f"http://localhost:5200/api/resumo?anos=2026&meses={m}&dia_ini=1&dia_fim={dfim}&marca=Todas&force=true")
        if data and data.get("status") == "success":
            resumo_map[f"2026_{m}_Todas"] = data
            print(f"   -> Capturado E-commerce 2026/{m} (dia 1 até {dfim})")'''

c = c.replace(target, replacement)
with open('build_github_dashboards_standalone.py', 'w', encoding='utf-8') as f:
    f.write(c)

print("Updated build_github_dashboards_standalone.py successfully!")

