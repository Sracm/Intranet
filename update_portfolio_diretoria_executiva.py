import re
import json

portfolio_path = r"C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\ANTIGRAVITY\PROJETOS\INTRANET\portfolio_standalone\index.html"
txt = open(portfolio_path, "r", encoding="utf-8").read()

# 1. Atualizar DASHBOARDS
match = re.search(r'const DASHBOARDS = (\[.*?\]);', txt)
if match:
    dashs = json.loads(match.group(1))
    
    # Renomeia 'Diretoria' para 'Diretoria Executiva'
    # E adiciona projetos estratégicos que a diretoria acompanha
    for d in dashs:
        if d.get('department') == 'Diretoria':
            d['department'] = 'Diretoria Executiva'
        
        # Limpar caracteres corrompidos em títulos
        if 'DRE Gestores' in d.get('title', ''):
            d['title'] = 'DRE Gestores - Geral (Diretoria)'

    # Identificar e ordenar: Projetos da Diretoria Executiva em 1º lugar na listagem
    diretoria_executiva = [d for d in dashs if d.get('department') == 'Diretoria Executiva']
    outros = [d for d in dashs if d.get('department') != 'Diretoria Executiva']
    dashs_reordenados = diretoria_executiva + outros

    new_json_str = json.dumps(dashs_reordenados, ensure_ascii=False)
    txt = txt[:match.start(1)] + new_json_str + txt[match.end(1):]

# 2. Adicionar estilos CSS do botão em destaque para Diretoria Executiva
old_css = ".filter-tab.active {"
new_css = """.filter-tab-featured {
      border-color: rgba(203, 151, 39, 0.5) !important;
      color: var(--mq-gold) !important;
      background: rgba(203, 151, 39, 0.12) !important;
      font-weight: 700 !important;
    }
    .filter-tab-featured:hover {
      background: rgba(203, 151, 39, 0.25) !important;
      box-shadow: 0 0 12px rgba(203, 151, 39, 0.4) !important;
    }
    .filter-tab.active {"""

if old_css in txt and ".filter-tab-featured" not in txt:
    txt = txt.replace(old_css, new_css, 1)

# 3. Atualizar a função buildFilterTabs
old_tabs_func = """    function buildFilterTabs() {
      const depts = {};
      DASHBOARDS.forEach(d => {
        depts[d.department] = (depts[d.department] || 0) + 1;
      });

      const container = document.getElementById('filterTabs');
      let html = `<button class="filter-tab active" onclick="setDepartmentFilter('ALL')">Todos (${DASHBOARDS.length})</button>`;

      Object.keys(depts).sort().forEach(dept => {
        html += `<button class="filter-tab" onclick="setDepartmentFilter('${dept}')">${dept} (${depts[dept]})</button>`;
      });

      container.innerHTML = html;
    }"""

new_tabs_func = """    function buildFilterTabs() {
      const depts = {};
      DASHBOARDS.forEach(d => {
        depts[d.department] = (depts[d.department] || 0) + 1;
      });

      const container = document.getElementById('filterTabs');
      let html = `<button class="filter-tab active" onclick="setDepartmentFilter('ALL')">Todos (${DASHBOARDS.length})</button>`;

      // Prioridade: 'Diretoria Executiva' logo em 1º lugar ao lado de 'Todos'
      const deptoPrincipal = 'Diretoria Executiva';
      if (depts[deptoPrincipal]) {
        html += `<button class="filter-tab filter-tab-featured" onclick="setDepartmentFilter('${deptoPrincipal}')">⭐ ${deptoPrincipal} (${depts[deptoPrincipal]})</button>`;
      }

      // Demais departamentos em ordem alfabética
      Object.keys(depts).sort().forEach(dept => {
        if (dept !== deptoPrincipal) {
          html += `<button class="filter-tab" onclick="setDepartmentFilter('${dept}')">${dept} (${depts[dept]})</button>`;
        }
      });

      container.innerHTML = html;
    }"""

if old_tabs_func in txt:
    txt = txt.replace(old_tabs_func, new_tabs_func)
    print("buildFilterTabs atualizada com sucesso!")

# 4. Ajustar setDepartmentFilter para suportar o ícone de estrela
old_set_dept = """    function setDepartmentFilter(dept) {
      currentDept = dept;
      const tabs = document.querySelectorAll('.filter-tab');
      tabs.forEach(tab => {
        if ((dept === 'ALL' && tab.textContent.startsWith('Todos')) || tab.textContent.startsWith(dept)) {
          tab.classList.add('active');
        } else {
          tab.classList.remove('active');
        }
      });
      renderDashboards();
    }"""

new_set_dept = """    function setDepartmentFilter(dept) {
      currentDept = dept;
      const tabs = document.querySelectorAll('.filter-tab');
      tabs.forEach(tab => {
        const text = tab.textContent;
        if ((dept === 'ALL' && text.includes('Todos')) || text.includes(dept)) {
          tab.classList.add('active');
        } else {
          tab.classList.remove('active');
        }
      });
      renderDashboards();
    }"""

if old_set_dept in txt:
    txt = txt.replace(old_set_dept, new_set_dept)
    print("setDepartmentFilter atualizada com sucesso!")

open(portfolio_path, "w", encoding="utf-8").write(txt)
print("index.html do portfólio salvo com sucesso com 'Diretoria Executiva'!")
