/**
 * MQ HAIR — Cockpit de Usabilidade & Analytics de Dashboards
 * Chart.js 4 + Real-time Dynamic Filtering + Modals + Export
 */

(function () {
  'use strict';

  // Guarda instâncias ativas dos gráficos
  let chartMonthly = null;
  let chartDOW = null;
  let chartHourly = null;
  let chartDept = null;

  // Estado global dos dados atuais
  let currentAnalyticsData = window.INITIAL_ANALYTICS_DATA || null;

  // Paleta de Cores MQ
  const MQ_COLORS = {
    gold: '#CB9727',
    goldLight: '#E0B246',
    goldDark: '#A5781B',
    goldGlow: 'rgba(203, 151, 39, 0.25)',
    goldFade: 'rgba(203, 151, 39, 0.08)',
    grayDark: '#1E293B',
    grayBar: '#334155',
    textMuted: '#94A3B8',
    gridLines: 'rgba(255, 255, 255, 0.05)',
    palette: [
      '#CB9727', '#E0B246', '#2563EB', '#38BDF8', 
      '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', 
      '#EC4899', '#6366F1', '#14B8A6', '#F97316'
    ]
  };

  document.addEventListener('DOMContentLoaded', () => {
    initCharts(currentAnalyticsData);
    bindFilterEvents();
    bindModalEvents();
    bindSearchEvents();
    bindExportEvents();
  });

  // ══════════════════════════════════════════════════════════════
  // INICIALIZAÇÃO DOS GRÁFICOS CHART.JS
  // ══════════════════════════════════════════════════════════════
  function initCharts(data) {
    if (!data) return;

    // 1. Gráfico de Evolução Mensal (Janeiro a Dezembro de 2026)
    const ctxMonthly = document.getElementById('chartMonthlyEvolution');
    if (ctxMonthly) {
      if (chartMonthly) chartMonthly.destroy();

      const labels = data.evolution_12m.map(m => m.label);
      const values = data.evolution_12m.map(m => m.views);

      chartMonthly = new Chart(ctxMonthly, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: 'Visualizações de Dashboards',
            data: values,
            borderColor: MQ_COLORS.gold,
            backgroundColor: (context) => {
              const chart = context.chart;
              const { ctx, chartArea } = chart;
              if (!chartArea) return null;
              const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
              gradient.addColorStop(0, 'rgba(203, 151, 39, 0.45)');
              gradient.addColorStop(1, 'rgba(203, 151, 39, 0.0)');
              return gradient;
            },
            fill: true,
            tension: 0.35,
            borderWidth: 3,
            pointBackgroundColor: MQ_COLORS.goldLight,
            pointBorderColor: '#0B0C10',
            pointBorderWidth: 2,
            pointRadius: 4,
            pointHoverRadius: 7,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: '#161722',
              titleColor: '#fff',
              bodyColor: MQ_COLORS.goldLight,
              borderColor: 'rgba(203, 151, 39, 0.4)',
              borderWidth: 1,
              padding: 10,
              displayColors: false,
              callbacks: {
                label: (ctx) => `${ctx.parsed.y} acessos`
              }
            }
          },
          scales: {
            x: {
              grid: { color: MQ_COLORS.gridLines },
              ticks: { color: MQ_COLORS.textMuted, font: { family: 'Montserrat', size: 11 } }
            },
            y: {
              beginAtZero: true,
              grid: { color: MQ_COLORS.gridLines },
              ticks: {
                color: MQ_COLORS.textMuted,
                font: { family: 'Montserrat', size: 11 },
                precision: 0
              }
            }
          }
        }
      });
    }

    // 2. Gráfico de Dias da Semana (Segunda a Domingo com Pico em Dourado)
    const ctxDOW = document.getElementById('chartDaysOfWeek');
    if (ctxDOW) {
      if (chartDOW) chartDOW.destroy();

      const labels = data.days_of_week.map(d => d.short_name);
      const values = data.days_of_week.map(d => d.views);
      const bgColors = data.days_of_week.map(d => d.is_peak ? MQ_COLORS.gold : MQ_COLORS.grayBar);
      const borderColors = data.days_of_week.map(d => d.is_peak ? MQ_COLORS.goldLight : 'transparent');

      chartDOW = new Chart(ctxDOW, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Acessos por Dia',
            data: values,
            backgroundColor: bgColors,
            borderColor: borderColors,
            borderWidth: 1.5,
            borderRadius: 6,
            maxBarThickness: 36
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: '#161722',
              titleColor: '#fff',
              bodyColor: MQ_COLORS.goldLight,
              borderColor: 'rgba(203, 151, 39, 0.4)',
              borderWidth: 1,
              callbacks: {
                title: (items) => data.days_of_week[items[0].dataIndex].name,
                label: (ctx) => `${ctx.parsed.y} acessos (${data.days_of_week[ctx.dataIndex].share}%)`
              }
            }
          },
          scales: {
            x: {
              grid: { display: false },
              ticks: { color: MQ_COLORS.textMuted, font: { family: 'Montserrat', size: 11, weight: '600' } }
            },
            y: {
              beginAtZero: true,
              grid: { color: MQ_COLORS.gridLines },
              ticks: { color: MQ_COLORS.textMuted, font: { family: 'Montserrat', size: 11 }, precision: 0 }
            }
          }
        }
      });
    }

    // 3. Gráfico de Distribuição por Horário (00h a 23h)
    const ctxHourly = document.getElementById('chartHourlyDistribution');
    if (ctxHourly) {
      if (chartHourly) chartHourly.destroy();

      const labels = data.hourly_distribution.map(h => h.label);
      const values = data.hourly_distribution.map(h => h.views);

      chartHourly = new Chart(ctxHourly, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Acessos por Hora',
            data: values,
            backgroundColor: (ctx) => {
              const val = ctx.parsed?.y || 0;
              return val >= 30 ? MQ_COLORS.gold : (val >= 15 ? 'rgba(203, 151, 39, 0.65)' : 'rgba(51, 65, 85, 0.7)');
            },
            borderRadius: 4,
            maxBarThickness: 22
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              backgroundColor: '#161722',
              titleColor: '#fff',
              bodyColor: MQ_COLORS.goldLight,
              borderColor: 'rgba(203, 151, 39, 0.4)',
              borderWidth: 1,
              callbacks: {
                title: (items) => `Horário: ${items[0].label}`,
                label: (ctx) => `${ctx.parsed.y} visualizações registradas`
              }
            }
          },
          scales: {
            x: {
              grid: { display: false },
              ticks: { color: MQ_COLORS.textMuted, font: { family: 'Montserrat', size: 10 }, maxRotation: 0 }
            },
            y: {
              beginAtZero: true,
              grid: { color: MQ_COLORS.gridLines },
              ticks: { color: MQ_COLORS.textMuted, font: { family: 'Montserrat', size: 10 }, precision: 0 }
            }
          }
        }
      });
    }

    // 4. Gráfico de Participação por Departamento (Donut)
    const ctxDept = document.getElementById('chartDeptShare');
    if (ctxDept) {
      if (chartDept) chartDept.destroy();

      const topDepts = data.dept_shares.slice(0, 7);
      const labels = topDepts.map(d => d.name);
      const values = topDepts.map(d => d.views);
      const colors = topDepts.map((d, i) => d.color || MQ_COLORS.palette[i % MQ_COLORS.palette.length]);

      chartDept = new Chart(ctxDept, {
        type: 'doughnut',
        data: {
          labels: labels,
          datasets: [{
            data: values,
            backgroundColor: colors,
            borderColor: '#161722',
            borderWidth: 2,
            hoverOffset: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '68%',
          plugins: {
            legend: {
              position: 'right',
              labels: {
                color: MQ_COLORS.textMuted,
                font: { family: 'Montserrat', size: 11 },
                boxWidth: 12,
                padding: 12
              }
            },
            tooltip: {
              backgroundColor: '#161722',
              titleColor: '#fff',
              bodyColor: MQ_COLORS.goldLight,
              borderColor: 'rgba(203, 151, 39, 0.4)',
              borderWidth: 1,
              callbacks: {
                label: (ctx) => {
                  const item = topDepts[ctx.dataIndex];
                  return ` ${item.views} acessos (${item.share_pct}%)`;
                }
              }
            }
          }
        }
      });
    }
  }

  // ══════════════════════════════════════════════════════════════
  // FILTRAGEM DINÂMICA VIA AJAX
  // ══════════════════════════════════════════════════════════════
  function bindFilterEvents() {
    const monthSelect = document.getElementById('filterMonth');
    const deptSelect = document.getElementById('filterDepartment');
    const userSelect = document.getElementById('filterUser');
    const resetBtn = document.getElementById('btnResetFilters');

    function applyFilters() {
      const month = monthSelect ? monthSelect.value : 'todos';
      const dept = deptSelect ? deptSelect.value : 'todos';
      const user = userSelect ? userSelect.value : 'todos';

      const url = `/api/analytics?month=${encodeURIComponent(month)}&dept=${encodeURIComponent(dept)}&user=${encodeURIComponent(user)}`;

      // Feedback visual de carregamento
      document.body.style.cursor = 'wait';

      fetch(url)
        .then(res => res.json())
        .then(data => {
          document.body.style.cursor = 'default';
          currentAnalyticsData = data;
          updateDashboardUI(data);
          initCharts(data);
        })
        .catch(err => {
          document.body.style.cursor = 'default';
          console.error('Erro ao atualizar analytics:', err);
        });
    }

    if (monthSelect) monthSelect.addEventListener('change', applyFilters);
    if (deptSelect) deptSelect.addEventListener('change', applyFilters);
    if (userSelect) userSelect.addEventListener('change', applyFilters);

    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        if (monthSelect) monthSelect.value = 'todos';
        if (deptSelect) deptSelect.value = 'todos';
        if (userSelect) userSelect.value = 'todos';
        const searchInput = document.getElementById('tableSearchInput');
        if (searchInput) searchInput.value = '';
        applyFilters();
      });
    }
  }

  // Atualiza toda a interface HTML com os novos dados
  function updateDashboardUI(data) {
    // 1. Atualizar KPIs
    setText('kpiTotalViews', data.kpis.total_views);
    setText('kpiAdoptionRate', data.kpis.adoption_rate + '%');
    setText('kpiAdoptionSub', `${data.kpis.accessed_reports} de ${data.kpis.total_registered_reports} relatórios ativos`);
    setText('kpiTotalUsers', data.kpis.total_users);
    setText('kpiUsersSub', `${data.kpis.total_users} usuários engajados`);
    setText('kpiAvgViews', data.kpis.avg_views_per_user);
    setText('kpiPeakDay', data.kpis.peak_day);
    setText('kpiPeakDayViews', `${data.kpis.peak_day_views} acessos (${data.kpis.peak_day_share}%)`);
    setText('kpiTopDash', data.kpis.top_dashboard);
    setText('kpiTopDashViews', `${data.kpis.top_dashboard_views} acessos`);

    // 2. Atualizar Turnos
    data.periods_distribution.forEach(p => {
      if (p.period.includes('Manhã')) setText('turnoManha', p.views);
      if (p.period.includes('Tarde')) setText('turnoTarde', p.views);
      if (p.period.includes('Noite')) setText('turnoNoite', p.views);
      if (p.period.includes('Madrugada')) setText('turnoMadrugada', p.views);
    });

    // 3. Atualizar Tabela de Ranking de Dashboards
    renderDashboardsTable(data.ranking_dashboards);

    // 4. Atualizar Tabela de Usuários (Raio-X)
    renderUsersTable(data.ranking_users);
  }

  function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
  }

  // Renderiza tabela de dashboards
  function renderDashboardsTable(dashboards) {
    const tbody = document.getElementById('dashboardsTableBody');
    if (!tbody) return;

    if (!dashboards || dashboards.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 2rem; color: var(--text-dim);">Nenhum dashboard encontrado com os filtros selecionados.</td></tr>`;
      return;
    }

    tbody.innerHTML = dashboards.map(d => {
      let rankBadgeClass = 'rank-badge';
      if (d.rank === 1) rankBadgeClass += ' rank-badge-1';
      else if (d.rank === 2) rankBadgeClass += ' rank-badge-2';
      else if (d.rank === 3) rankBadgeClass += ' rank-badge-3';

      const deptColor = d.dept_color || '#CB9727';

      return `
        <tr class="dashboard-row" data-title="${escapeHtml(d.title.toLowerCase())}" data-dept="${escapeHtml(d.dept_name.toLowerCase())}">
          <td style="text-align: center;">
            <span class="${rankBadgeClass}">${d.rank}</span>
          </td>
          <td>
            <div style="font-weight: 700; color: #fff; font-size: 0.86rem; margin-bottom: 2px;">
              ${escapeHtml(d.title)}
            </div>
            <span class="dept-pill">
              <span class="dept-pill-dot" style="background: ${deptColor};"></span>
              ${escapeHtml(d.dept_name)}
            </span>
          </td>
          <td>
            <div class="share-bar-container">
              <div class="share-bar-track">
                <div class="share-bar-fill" style="width: ${d.share_pct}%;"></div>
              </div>
              <span class="share-bar-text">${d.share_pct}%</span>
            </div>
          </td>
          <td style="font-weight: 800; color: var(--mq-gold); font-size: 0.94rem;">
            ${d.total_views}
          </td>
          <td>
            <span class="user-reports-tag">
              <i class="bi bi-people-fill"></i> ${d.unique_users} usuários
            </span>
          </td>
          <td style="color: var(--text-muted); font-size: 0.76rem;">
            ${d.last_access_str || '-'}
          </td>
          <td style="text-align: right; white-space: nowrap;">
            <button class="table-btn btn-view-report-users" data-report-id="${d.id}" title="Ver quem acessou este dashboard">
              <i class="bi bi-person-lines-fill"></i> Quem Acessou
            </button>
            <a href="/report/${d.id}" class="table-btn" style="background: rgba(203,151,39,0.12); color: var(--mq-gold); border-color: rgba(203,151,39,0.3);" title="Abrir Dashboard">
              <i class="bi bi-box-arrow-up-right"></i> Abrir
            </a>
          </td>
        </tr>
      `;
    }).join('');
  }

  // Renderiza tabela de usuários
  function renderUsersTable(users) {
    const tbody = document.getElementById('usersTableBody');
    if (!tbody) return;

    if (!users || users.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 2rem; color: var(--text-dim);">Nenhum usuário encontrado com os filtros selecionados.</td></tr>`;
      return;
    }

    tbody.innerHTML = users.map(u => {
      const initials = (u.name || u.username || 'MQ').split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase();

      return `
        <tr class="user-row" data-name="${escapeHtml((u.name || '').toLowerCase())}" data-username="${escapeHtml((u.username || '').toLowerCase())}">
          <td style="text-align: center;">
            <span class="rank-badge">${u.rank}</span>
          </td>
          <td>
            <div class="user-name-cell">
              <span class="user-avatar-circle">${initials}</span>
              <div>
                <div style="font-weight: 700; color: #fff;">${escapeHtml(u.name || u.username)}</div>
                <div style="font-size: 0.72rem; color: var(--text-dim);">@${escapeHtml(u.username)}</div>
              </div>
            </div>
          </td>
          <td>
            <span class="dept-pill">${escapeHtml(u.dept_name || 'Geral')}</span>
          </td>
          <td style="font-weight: 800; color: var(--mq-gold); font-size: 0.94rem;">
            ${u.total_views}
          </td>
          <td>
            <span class="user-reports-tag" style="background: rgba(40, 167, 69, 0.12); color: #4ade80;">
              <i class="bi bi-file-earmark-bar-graph"></i> ${u.distinct_reports} dashboards
            </span>
          </td>
          <td style="color: var(--text-muted); font-size: 0.76rem;">
            ${u.last_access_str || '-'}
          </td>
          <td style="text-align: right;">
            <button class="table-btn btn-view-user-reports" data-user-id="${u.id}" title="Ver todos os dashboards que este usuário acessou">
              <i class="bi bi-bar-chart-steps"></i> Raio-X de Relatórios
            </button>
          </td>
        </tr>
      `;
    }).join('');
  }

  // ══════════════════════════════════════════════════════════════
  // MODAIS INTERATIVOS (QUEM ACESSOU & RAIO-X USUÁRIO)
  // ══════════════════════════════════════════════════════════════
  function bindModalEvents() {
    const modalBackdrop = document.getElementById('analyticsModalBackdrop');
    const modalTitle = document.getElementById('analyticsModalTitle');
    const modalBody = document.getElementById('analyticsModalBody');
    const modalClose = document.getElementById('analyticsModalClose');

    function closeModal() {
      if (modalBackdrop) modalBackdrop.classList.remove('active');
    }

    if (modalClose) modalClose.addEventListener('click', closeModal);
    if (modalBackdrop) {
      modalBackdrop.addEventListener('click', (e) => {
        if (e.target === modalBackdrop) closeModal();
      });
    }

    // Delegação de evento: Clique em "Quem Acessou"
    document.addEventListener('click', (e) => {
      const btnReport = e.target.closest('.btn-view-report-users');
      if (btnReport) {
        const reportId = parseInt(btnReport.getAttribute('data-report-id'));
        openReportUsersModal(reportId);
        return;
      }

      const btnUser = e.target.closest('.btn-view-user-reports');
      if (btnUser) {
        const userId = parseInt(btnUser.getAttribute('data-user-id'));
        openUserReportsModal(userId);
        return;
      }
    });

    // Abre Modal: Lista de quem acessou o Dashboard
    function openReportUsersModal(reportId) {
      if (!currentAnalyticsData) return;
      const report = currentAnalyticsData.ranking_dashboards.find(d => d.id === reportId);
      if (!report) return;

      modalTitle.innerHTML = `<i class="bi bi-trophy-fill" style="color: var(--mq-gold);"></i> ${escapeHtml(report.title)}`;
      
      const users = report.users_accessed || [];
      if (users.length === 0) {
        modalBody.innerHTML = `<div style="text-align:center; padding: 2rem; color: var(--text-dim);">Nenhum usuário registrado para este dashboard no filtro atual.</div>`;
      } else {
        modalBody.innerHTML = `
          <div style="margin-bottom: 1rem; color: var(--text-muted); font-size: 0.82rem;">
            Total de <strong>${report.total_views} acessos</strong> distribuídos entre <strong>${users.length} usuários</strong>:
          </div>
          <table class="analytics-table" style="font-size: 0.8rem;">
            <thead>
              <tr>
                <th>Usuário</th>
                <th>Departamento</th>
                <th style="text-align: right;">Acessos</th>
                <th style="text-align: right;">Último Acesso</th>
              </tr>
            </thead>
            <tbody>
              ${users.map(u => `
                <tr>
                  <td style="font-weight: 700; color: #fff;">${escapeHtml(u.name || u.username)}</td>
                  <td><span class="dept-pill">${escapeHtml(u.user_dept)}</span></td>
                  <td style="text-align: right; font-weight: 800; color: var(--mq-gold);">${u.views}</td>
                  <td style="text-align: right; color: var(--text-muted); font-size: 0.75rem;">${u.last_access_str}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        `;
      }

      modalBackdrop.classList.add('active');
    }

    // Abre Modal: Lista de dashboards acessados pelo Usuário (Raio-X)
    function openUserReportsModal(userId) {
      if (!currentAnalyticsData) return;
      const user = currentAnalyticsData.ranking_users.find(u => u.id === userId);
      if (!user) return;

      modalTitle.innerHTML = `<i class="bi bi-person-badge-fill" style="color: var(--mq-gold);"></i> ${escapeHtml(user.name || user.username)} — Raio-X de Relatórios`;
      
      const reports = user.reports || [];
      if (reports.length === 0) {
        modalBody.innerHTML = `<div style="text-align:center; padding: 2rem; color: var(--text-dim);">Este usuário não possui acessos registrados no período filtrado.</div>`;
      } else {
        modalBody.innerHTML = `
          <div style="margin-bottom: 1rem; color: var(--text-muted); font-size: 0.82rem;">
            O usuário acessou <strong>${reports.length} dashboards diferentes</strong>, totalizando <strong>${user.total_views} visualizações</strong>:
          </div>
          <table class="analytics-table" style="font-size: 0.8rem;">
            <thead>
              <tr>
                <th>Dashboard</th>
                <th>Setor</th>
                <th style="text-align: right;">Acessos</th>
                <th style="text-align: right;">Último Acesso</th>
                <th style="text-align: right;">Ação</th>
              </tr>
            </thead>
            <tbody>
              ${reports.map(r => `
                <tr>
                  <td style="font-weight: 700; color: #fff;">${escapeHtml(r.title)}</td>
                  <td><span class="dept-pill">${escapeHtml(r.dept_name)}</span></td>
                  <td style="text-align: right; font-weight: 800; color: var(--mq-gold);">${r.views}</td>
                  <td style="text-align: right; color: var(--text-muted); font-size: 0.75rem;">${r.last_access_str}</td>
                  <td style="text-align: right;">
                    <a href="/report/${r.report_id}" class="table-btn" style="padding: 3px 8px;">
                      <i class="bi bi-box-arrow-up-right"></i>
                    </a>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        `;
      }

      modalBackdrop.classList.add('active');
    }
  }

  // ══════════════════════════════════════════════════════════════
  // BUSCA INSTANTÂNEA NAS TABELAS
  // ══════════════════════════════════════════════════════════════
  function bindSearchEvents() {
    const searchInput = document.getElementById('tableSearchInput');
    if (!searchInput) return;

    searchInput.addEventListener('input', (e) => {
      const q = e.target.value.toLowerCase().trim();

      // Filtra linhas da tabela de dashboards
      document.querySelectorAll('.dashboard-row').forEach(row => {
        const title = row.getAttribute('data-title') || '';
        const dept = row.getAttribute('data-dept') || '';
        if (!q || title.includes(q) || dept.includes(q)) {
          row.style.display = '';
        } else {
          row.style.display = 'none';
        }
      });

      // Filtra linhas da tabela de usuários
      document.querySelectorAll('.user-row').forEach(row => {
        const name = row.getAttribute('data-name') || '';
        const username = row.getAttribute('data-username') || '';
        if (!q || name.includes(q) || username.includes(q)) {
          row.style.display = '';
        } else {
          row.style.display = 'none';
        }
      });
    });
  }

  // ══════════════════════════════════════════════════════════════
  // EXPORTAÇÃO CSV / EXCEL
  // ══════════════════════════════════════════════════════════════
  function bindExportEvents() {
    const btnExport = document.getElementById('btnExportAnalytics');
    if (!btnExport) return;

    btnExport.addEventListener('click', () => {
      if (!currentAnalyticsData) return;

      let csv = 'RANK;DASHBOARD;DEPARTAMENTO;TOTAL_VIEWS;SHARE_PCT;USUARIOS_DISTINTOS;ULTIMO_ACESSO\n';
      currentAnalyticsData.ranking_dashboards.forEach(d => {
        csv += `${d.rank};"${d.title.replace(/"/g, '""')}";"${d.dept_name}";${d.total_views};${d.share_pct}%;${d.unique_users};"${d.last_access_str}"\n`;
      });

      csv += '\n\nRANK_USUARIO;NOME;USUARIO;DEPARTAMENTO;TOTAL_VIEWS;DASHBOARDS_DISTINTOS;ULTIMO_ACESSO\n';
      currentAnalyticsData.ranking_users.forEach(u => {
        csv += `${u.rank};"${(u.name || '').replace(/"/g, '""')}";"${u.username}";"${u.dept_name || 'Geral'}";${u.total_views};${u.distinct_reports};"${u.last_access_str}"\n`;
      });

      const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', `MQ_Usabilidade_Dashboards_${new Date().toISOString().slice(0, 10)}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    });
  }

  function escapeHtml(text) {
    if (!text) return '';
    return text.replace(/[&<>"']/g, function(m) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m];
    });
  }

})();
