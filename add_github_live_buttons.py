portfolio_path = r"C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\ANTIGRAVITY\PROJETOS\INTRANET\portfolio_standalone\index.html"
txt = open(portfolio_path, "r", encoding="utf-8").read()

old_action = """              <div class="card-action">
                <button onclick="openLightbox('${imgUrl}', '${d.title.replace(/'/g, "\\\\'")}', '${d.department}')" class="btn-card btn-card-primary" style="border: none; cursor: pointer; width: 100%;">
                  <i class="fa-solid fa-magnifying-glass-plus"></i> Ver Tela do Dashboard
                </button>
              </div>"""

new_action = """              <div class="card-action" style="display: flex; gap: 8px; width: 100%;">
                <button onclick="openLightbox('${imgUrl}', '${d.title.replace(/'/g, "\\\\'")}', '${d.department}')" class="btn-card" style="flex: 1; border: 1px solid rgba(255,255,255,0.15); background: rgba(255,255,255,0.06); color: #FFF; cursor: pointer; border-radius: 6px; padding: 8px 6px; font-weight: 700; font-size: 0.74rem; display: flex; align-items: center; justify-content: center; gap: 4px;">
                  <i class="fa-solid fa-magnifying-glass-plus"></i> Ver Tela
                </button>
                ${d.github_repo ? `
                  <a href="${d.github_repo}" target="_blank" rel="noopener" class="btn-card btn-card-primary" style="flex: 1; text-decoration: none; border-radius: 6px; padding: 8px 6px; font-weight: 700; font-size: 0.74rem; display: flex; align-items: center; justify-content: center; gap: 4px;">
                    <i class="fa-brands fa-github"></i> GitHub Live
                  </a>
                ` : ''}
              </div>"""

if old_action in txt:
    txt = txt.replace(old_action, new_action)
    open(portfolio_path, "w", encoding="utf-8").write(txt)
    print("Atualizado botoes de acao dos cards com Ver Tela + GitHub Live!")
else:
    print("old_action nao encontrado exatamente. Verificando...")
