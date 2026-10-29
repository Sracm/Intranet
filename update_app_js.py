import os

app_js_path = r"c:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\ANTIGRAVITY\PROJETOS\Dir.Ecommerce\static\js\app.js"
with open(app_js_path, "r", encoding="utf-8") as f:
    c = f.read()

c_norm = c.replace("\r\n", "\n")

old_fn = """function renderizarConversao() {
    if (!currentConversaoData) return;

    // 1. Atualiza Mini KPIs com Formatação Rica
    const badgeTot = document.getElementById('badge-total-conversao');
    if (badgeTot) badgeTot.textContent = `Média: ${fmtPct(currentConversaoData.totais.taxa_conversao_media)}`;

    const kpiSess = document.getElementById('kpi-ga-sessoes');
    if (kpiSess) kpiSess.innerHTML = `<span class="val-cyan">${fmtInt(currentConversaoData.totais.total_sessoes)}</span>`;

    const kpiPed = document.getElementById('kpi-ga-pedidos');
    if (kpiPed) kpiPed.innerHTML = `<span class="val-purple">${fmtInt(currentConversaoData.totais.total_pedidos)}</span>`;

    const kpiTaxa = document.getElementById('kpi-ga-taxa');
    if (kpiTaxa) kpiTaxa.innerHTML = `<span class="val-green-glow">${fmtPct(currentConversaoData.totais.taxa_conversao_media)}</span>`;

    renderizarTabelaConversao();
    if (window.lucide) lucide.createIcons();
}"""

new_fn = """function renderizarConversao() {
    if (!currentConversaoData) return;

    const mesesSel = currentParams && currentParams.meses ? currentParams.meses : [10];
    const ehMesUnico = mesesSel.length === 1;
    const nomeMesSel = ehMesUnico ? NOMES_MESES_ABREV[mesesSel[0] - 1] : `${mesesSel.length} Meses`;

    // 1. Atualiza Mini KPIs com Formatação Rica e adapta rótulo ao período selecionado
    const badgeTot = document.getElementById('badge-total-conversao');
    if (badgeTot) {
        badgeTot.textContent = ehMesUnico 
            ? `${nomeMesSel}: ${fmtPct(currentConversaoData.totais.taxa_conversao_media)}`
            : `Média: ${fmtPct(currentConversaoData.totais.taxa_conversao_media)}`;
    }

    const kpiSess = document.getElementById('kpi-ga-sessoes');
    if (kpiSess) kpiSess.innerHTML = `<span class="val-cyan">${fmtInt(currentConversaoData.totais.total_sessoes)}</span>`;

    const kpiPed = document.getElementById('kpi-ga-pedidos');
    if (kpiPed) kpiPed.innerHTML = `<span class="val-purple">${fmtInt(currentConversaoData.totais.total_pedidos)}</span>`;

    const kpiTaxa = document.getElementById('kpi-ga-taxa');
    if (kpiTaxa) kpiTaxa.innerHTML = `<span class="val-green-glow">${fmtPct(currentConversaoData.totais.taxa_conversao_media)}</span>`;

    // Atualiza labels dos 3 mini cards
    const lblSess = document.querySelector('.analytics-card-conversao .kpi-accent-blue .mini-kpi-label');
    if (lblSess) lblSess.textContent = ehMesUnico ? `Sessões (${nomeMesSel})` : 'Total Sessões';

    const lblPed = document.querySelector('.analytics-card-conversao .kpi-accent-purple .mini-kpi-label');
    if (lblPed) lblPed.textContent = ehMesUnico ? `Pedidos (${nomeMesSel})` : 'Total Pedidos';

    const lblTaxa = document.querySelector('.analytics-card-conversao .kpi-accent-green .mini-kpi-label');
    if (lblTaxa) lblTaxa.textContent = ehMesUnico ? `Taxa (${nomeMesSel})` : 'Taxa Média';

    renderizarTabelaConversao();
    if (window.lucide) lucide.createIcons();
}"""

old_table_sort = "const { col, dir } = currentConversaoSort;"
new_table_sort = """const mesesSel = currentParams && currentParams.meses ? currentParams.meses : [10];
    const { col, dir } = currentConversaoSort;"""

old_row = """        tr.innerHTML = `
            <td class="col-mes-name">
                <span class="mes-pill">${item.mes_abrev}</span>
            </td>
            <td class="text-right num-sessoes">${fmtInt(item.sessoes)}</td>
            <td class="text-right num-pedidos">${fmtInt(item.pedidos)}</td>
            <td class="text-right">
                <span class="${badgeClass}">
                    <span class="status-indicator-dot"></span>
                    <span>${item.taxa_conversao.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}%</span>
                </span>
            </td>
        `;"""

new_row = """        const isSelected = mesesSel.includes(item.mes);
        if (isSelected) {
            tr.style.background = 'rgba(203, 151, 39, 0.15)';
            tr.style.boxShadow = 'inset 3px 0 0 #CB9727';
        }
        tr.innerHTML = `
            <td class="col-mes-name">
                <span class="mes-pill ${isSelected ? 'mes-pill-active' : ''}" style="${isSelected ? 'background: #CB9727; color: #000; font-weight: 800;' : ''}">${item.mes_abrev}</span>
            </td>
            <td class="text-right num-sessoes" style="${isSelected ? 'color: #FFFFFF; font-weight: 700;' : ''}">${fmtInt(item.sessoes)}</td>
            <td class="text-right num-pedidos" style="${isSelected ? 'color: #FFFFFF; font-weight: 700;' : ''}">${fmtInt(item.pedidos)}</td>
            <td class="text-right">
                <span class="${badgeClass}">
                    <span class="status-indicator-dot"></span>
                    <span>${item.taxa_conversao.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}%</span>
                </span>
            </td>
        `;"""

if old_fn in c_norm and old_row in c_norm:
    c_norm = c_norm.replace(old_fn, new_fn).replace(old_table_sort, new_table_sort, 1).replace(old_row, new_row)
    with open(app_js_path, "w", encoding="utf-8") as f:
        f.write(c_norm.replace("\n", "\r\n"))
    print("SUCCESS: Updated app.js")
else:
    print("Target not found")

