"""
Script para atualizar os arquivos de interface de Trimestre
"""
import os

HTML_CONTENT = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel TV - Performance Trimestral e Semestral</title>
    
    <!-- Google Fonts: Montserrat (MQ Design System) -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800&display=swap" rel="stylesheet">
    
    <!-- Custom CSS -->
    <link rel="stylesheet" href="/static/css/style.css?v=58">
    <link rel="stylesheet" href="/static/css/canais.css?v=20261027_1">
    <link rel="stylesheet" href="/static/css/trimestre.css?v=20261027_3">
    
    <!-- ECharts Local -->
    <script src="/static/js/echarts.min.js"></script>
</head>
<body>
    <div class="dashboard-container">
        <!-- Header -->
        <header class="header">
            <div class="header-top">
                <div class="nav-tabs-container">
                    <button onclick="navigateTab('/tv')" class="tab-btn">Mensal(%)</button>
                    <button onclick="navigateTab('/acumulado')" class="tab-btn">Acumulado(%)</button>
                    <button onclick="navigateTab('/trimestre')" class="tab-btn active">Trimestre</button>
                    <button onclick="navigateTab('/todos_canais')" class="tab-btn">Todos os Canais</button>
                    <button onclick="navigateTab('/categorias')" class="tab-btn">Categorias</button>
                    <button onclick="navigateTab('/marcas')" class="tab-btn">Marcas</button>
                    <button onclick="navigateTab('/canal/distribuicao')" class="tab-btn">Distribuição</button>
                    <button onclick="navigateTab('/canal/ecommerce_mq')" class="tab-btn">E-commerce MQ</button>
                    <button onclick="navigateTab('/canal/varejo_sp')" class="tab-btn">Varejo SP</button>
                    <button onclick="navigateTab('/canal/comex')" class="tab-btn">Comex</button>
                    <button onclick="navigateTab('/canal/regional_no_nd')" class="tab-btn">Regional NO/ND</button>
                    <button onclick="navigateTab('/canal/regional_rj_mg_es')" class="tab-btn">Reg. RJ/MG/ES</button>
                    <button onclick="navigateTab('/canal/regional_sul')" class="tab-btn">Regional Sul</button>
                    <button onclick="navigateTab('/mapa_regionais')" class="tab-btn" style="color:#ffd700;">🗺️ Mapa Brasil</button>
                    <button onclick="navigateTab('/empresa')" class="tab-btn">Empresa</button>
                    <button onclick="navigateTab('/diario_canal')" class="tab-btn">Diário Canal</button>
                    <button onclick="navigateTab('/diario_marcas')" class="tab-btn">Diário Marcas</button>
                    <button onclick="navigateTab('/paises')" class="tab-btn">Países</button>
                    <button onclick="navigateTab('/teste_estoque')" class="tab-btn"><span class="tab-icon">🚨</span> Estoque e Previsão</button>
                </div>
            </div>

            <div class="header-bottom">
                <div class="filters-row">
                    <select id="filter-year" onchange="trocarAno()">
                        <option value="2024">2024</option>
                        <option value="2025">2025</option>
                        <option value="2026" selected>2026</option>
                    </select>
                    <!-- Sub-navegação idêntica a de Todos os Canais -->
                    <div class="sub-nav-canais" id="trimestres-pills-container" style="margin: 0; padding: 0;">
                        <button class="sub-tab-btn" id="btn-tri-1T" onclick="setTrimestreView('1T')">1º TRI (JAN-MAR)</button>
                        <button class="sub-tab-btn" id="btn-tri-2T" onclick="setTrimestreView('2T')">2º TRI (ABR-JUN)</button>
                        <button class="sub-tab-btn active" id="btn-tri-3T" onclick="setTrimestreView('3T')">3º TRI (JUL-SET)</button>
                        <button class="sub-tab-btn" id="btn-tri-4T" onclick="setTrimestreView('4T')">4º TRI (OUT-DEZ)</button>
                    </div>
                    <button id="btn-refresh" onclick="manualRefresh()" class="btn-refresh" title="Atualizar dados agora">🔄 Atualizar</button>
                </div>
                <div class="header-meta-info">
                    <div class="clock" id="clock">00:00:00</div>
                    <div class="date" id="date">01/01/2026</div>
                    <div class="last-update" id="last-update">Última atualização: --:--:--</div>
                    <div class="next-update" id="next-update">Próxima atualização em: 10:00</div>
                </div>
            </div>
        </header>

        <!-- Main Grid for 5 Financial Cards -->
        <main class="canais-main-container">
            <div id="trimestre-cards-container" class="grid-financeiro-5"></div>
        </main>
    </div>

    <!-- Áudio de Meta -->
    <audio id="music-sound" src="/static/audio/van_halen_jump.mp3" preload="none"></audio>

    <!-- Custom JS -->
    <script src="/static/js/trimestre.js?v=20261027_3"></script>
    <!-- Auto-Rotacao TV (Carrossel Contínuo 2.5 min) -->
    <script src="/static/js/tv_rotator.js?v=7"></script>
</body>
</html>
"""

CSS_CONTENT = """/* trimestre.css - Layout idêntico aos Canais com suporte a 5 cards financeiros */

.grid-financeiro-5 {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    grid-template-rows: 1fr 1fr;
    gap: 8px;
    flex: 1;
    min-height: 0;
    height: 100%;
    overflow: hidden;
}

/* 1ª Linha: 2 Cards (3 colunas cada) */
.grid-financeiro-5 .canal-card:nth-child(1),
.grid-financeiro-5 .canal-card:nth-child(2) {
    grid-column: span 3;
}

/* 2ª Linha: 3 Cards (2 colunas cada) */
.grid-financeiro-5 .canal-card:nth-child(3),
.grid-financeiro-5 .canal-card:nth-child(4),
.grid-financeiro-5 .canal-card:nth-child(5) {
    grid-column: span 2;
}

/* Ajuste nos títulos e charts para manter proporção */
.grid-financeiro-5 .canal-card {
    background: linear-gradient(180deg, #131722 0%, #0d1017 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    overflow: hidden;
    height: 100%;
    min-height: 0;
    position: relative;
    transition: border-color 0.25s, box-shadow 0.25s;
}

.grid-financeiro-5 .canal-title {
    background: rgba(255, 255, 255, 0.03);
    padding: 6px 10px;
    text-align: center;
    font-size: 0.88rem;
    font-weight: 800;
    color: var(--mq-gold, #cb9727);
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    letter-spacing: 0.5px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    flex-shrink: 0;
    text-transform: uppercase;
}

.grid-financeiro-5 .canal-chart {
    flex: 1;
    width: 100%;
    height: 100%;
    min-height: 120px;
    position: relative;
}

.grid-financeiro-5 .canal-card.meta-batida {
    animation: blink-green-blue 2.5s infinite ease-in-out !important;
    border-width: 2px !important;
}

.grid-financeiro-5 .canal-card.meta-batida .badge-objetivo-alcancado {
    display: inline-flex;
}
"""

JS_CONTENT = """// ============================================================
// trimestre.js - Painel Financeiro Trimestral (Layout Canais TV)
// Despesas Fixas, Variáveis, Totais, Faturamento e Lucro Líquido
// ============================================================

let chartInstances = {};
let nextUpdateSeconds = 600;
let currentTrimestre = '3T'; // Default: 3º TRIM

const TRI_LABELS = {
    '1T': '1º TRI (JAN-MAR)',
    '2T': '2º TRI (ABR-JUN)',
    '3T': '3º TRI (JUL-SET)',
    '4T': '4º TRI (OUT-DEZ)'
};

function navigateTab(path) {
    pararTodosAudios();
    if (path === '/tv' || path === '/') {
        window.location.href = '/tv';
        return;
    }
    const ano = document.getElementById('filter-year')?.value || new Date().getFullYear();
    window.location.href = `${path}?ano=${ano}`;
}

window.addEventListener('beforeunload', () => pararTodosAudios());
window.addEventListener('pagehide', () => pararTodosAudios());

function updateClock() {
    const now = new Date();
    const clockEl = document.getElementById('clock');
    const dateEl = document.getElementById('date');
    if (clockEl) clockEl.innerText = now.toLocaleTimeString('pt-BR');
    if (dateEl) dateEl.innerText = now.toLocaleDateString('pt-BR');

    nextUpdateSeconds--;
    if (nextUpdateSeconds <= 0) {
        nextUpdateSeconds = 600;
        fetchData(true);
    }

    const nextUpdateEl = document.getElementById('next-update');
    if (nextUpdateEl) {
        const min = Math.floor(nextUpdateSeconds / 60);
        const sec = nextUpdateSeconds % 60;
        nextUpdateEl.innerText = `Próxima atualização em: ${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
    }
}

/**
 * Cria o Gauge Radial idêntico aos Canais de Vendas
 */
function getCanalGaugeOption(percent, displayStr, diffVal, isLarge) {
    const diff = (diffVal !== undefined && diffVal !== null) ? Number(diffVal) : (percent - 100);
    const sign = diff >= 0 ? '+' : '';
    const diffText = sign + diff.toFixed(1) + '%';
    const diffColor = diff >= 0 ? '#00d26a' : '#ff2424';

    const radius = isLarge ? '120%' : '125%';
    const center = isLarge ? ['50%', '70%'] : ['50%', '65%'];
    const lineWidth = isLarge ? 24 : 18;
    const pointerWidth = isLarge ? 8 : 7;
    const titleSize = isLarge ? 26 : 22;
    const detailSize = isLarge ? 16 : 14;

    const mainDisplay = displayStr || (percent.toFixed(1) + '%');

    return {
        series: [
            {
                type: 'gauge',
                startAngle: 180,
                endAngle: 0,
                min: 0,
                max: 120,
                splitNumber: 12,
                radius: radius,
                center: center,
                axisLine: {
                    lineStyle: {
                        width: lineWidth,
                        color: [
                            [80 / 120, '#ff2424'],
                            [100 / 120, '#ffd600'],
                            [1, '#00d26a']
                        ]
                    }
                },
                pointer: {
                    icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
                    length: '62%',
                    width: pointerWidth,
                    offsetCenter: [0, '-4%'],
                    itemStyle: {
                        color: '#f5c518',
                        shadowColor: 'rgba(0,0,0,0.6)',
                        shadowBlur: 4
                    }
                },
                axisTick: {
                    length: isLarge ? 8 : 5,
                    lineStyle: { color: 'auto', width: 1.2 }
                },
                splitLine: {
                    length: isLarge ? 14 : 10,
                    lineStyle: { color: 'auto', width: 2 }
                },
                axisLabel: {
                    show: false
                },
                title: {
                    offsetCenter: [0, '15%'],
                    fontSize: titleSize,
                    color: '#ffffff',
                    fontWeight: '800',
                    fontFamily: 'Montserrat'
                },
                detail: {
                    fontSize: detailSize,
                    offsetCenter: [0, '38%'],
                    valueAnimation: false,
                    formatter: function () {
                        return diffText;
                    },
                    color: diffColor,
                    fontWeight: '700',
                    fontFamily: 'Montserrat'
                },
                data: [{
                    value: Math.min(Math.max(percent, 0), 120),
                    name: mainDisplay
                }]
            }
        ]
    };
}

/**
 * Renderiza os badges de trimestres (T1, T2, T3, T4) na base do card
 */
function renderQuarterBadges(reguaObj, activeTri) {
    const quarters = ['1T', '2T', '3T', '4T'];
    return quarters.map(tKey => {
        const item = reguaObj ? reguaObj[tKey] : null;
        let pct = item ? Number(item.percent) : null;
        let valStr = '—';
        let cls = 'val-neutral';

        if (pct !== null && !isNaN(pct)) {
            valStr = item.display || (pct.toFixed(1) + '%');
            if (pct >= 100) cls = 'val-success';
            else if (pct >= 80) cls = 'val-warning';
            else cls = 'val-danger';
        }

        const isSelected = (activeTri === tKey);
        const selClass = isSelected ? 'selected' : '';

        return `
            <div class="tri-badge-btn ${selClass}" onclick="setTrimestreView('${tKey}')" title="Clique para exibir o ${TRI_LABELS[tKey]} (${valStr})">
                <span>${tKey}</span>
                <span class="tri-badge-val ${cls}">${valStr}</span>
            </div>
        `;
    }).join('');
}

function renderCards(cardsList, selectedTri) {
    const container = document.getElementById('trimestre-cards-container');
    if (!container) return;

    Object.values(chartInstances).forEach(c => c && c.dispose());
    chartInstances = {};
    container.innerHTML = '';

    cardsList.forEach((item, idx) => {
        const isBatida = (Number(item.percent) >= 100);
        const card = document.createElement('div');
        card.className = 'canal-card';
        if (isBatida) {
            card.classList.add('meta-batida');
        }
        card.id = `card-trimestre-${idx}`;

        const isLarge = (idx === 0 || idx === 1); // 1ª linha mais larga

        card.innerHTML = `
            <div class="canal-title">${item.title}</div>
            <div class="badge-objetivo-alcancado">OBJETIVO ALCANÇADO!!!</div>
            <div class="canal-chart" id="chart-tri-${idx}"></div>
            <div class="canal-tri-footer">
                <div class="canal-tri-badges">
                    ${renderQuarterBadges(item.regua, selectedTri)}
                </div>
            </div>
        `;

        container.appendChild(card);

        const chartEl = document.getElementById(`chart-tri-${idx}`);
        if (chartEl) {
            const chart = echarts.init(chartEl);
            chart.setOption(getCanalGaugeOption(item.percent, item.display, item.diff, isLarge));
            chartInstances[idx] = chart;
        }
    });
}

function setTrimestreView(triKey) {
    currentTrimestre = triKey;
    document.querySelectorAll('#trimestres-pills-container .sub-tab-btn').forEach(b => {
        b.classList.toggle('active', b.id === `btn-tri-${triKey}`);
    });
    fetchData();
}

function trocarAno() {
    fetchData();
}

async function fetchData(forceRefresh = false) {
    const ano = document.getElementById('filter-year')?.value || '2026';

    try {
        let url = `/api/trimestre_tv?ano=${ano}&trimestre=${currentTrimestre}`;
        if (forceRefresh) {
            url += `&refresh=1&_t=${Date.now()}`;
        }
        const response = await fetch(url);
        const json = await response.json();

        if (json.success && json.data) {
            if (json.trimestres_disponiveis && json.trimestres_disponiveis.length > 0) {
                const pillsCont = document.getElementById('trimestres-pills-container');
                if (pillsCont) {
                    pillsCont.innerHTML = json.trimestres_disponiveis.map(t => {
                        const labelFull = TRI_LABELS[t.chave] || t.chave;
                        return `
                            <button class="sub-tab-btn ${t.ativo ? 'active' : ''}" id="btn-tri-${t.chave}" onclick="setTrimestreView('${t.chave}')">
                                ${labelFull}
                            </button>
                        `;
                    }).join('');
                }
            }

            renderCards(json.data, json.trimestre_selecionado || currentTrimestre);

            const lastUpdateEl = document.getElementById('last-update');
            if (lastUpdateEl) {
                lastUpdateEl.innerText = `Última atualização: ${new Date().toLocaleTimeString('pt-BR')}`;
            }
        }
    } catch (e) {
        console.error("Erro ao carregar dados do trimestre:", e);
    }
}

function manualRefresh() {
    nextUpdateSeconds = 600;
    fetchData(true);
}

function pararTodosAudios() {
    const audioMusica = document.getElementById('music-sound');
    if (audioMusica) {
        audioMusica.pause();
        audioMusica.currentTime = 0;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const anoParam = params.get('ano');
    const triParam = params.get('trimestre') || params.get('tri');

    if (anoParam && document.getElementById('filter-year')) {
        document.getElementById('filter-year').value = anoParam;
    }
    if (triParam) {
        currentTrimestre = triParam.toUpperCase();
    }

    fetchData();

    setInterval(updateClock, 1000);
    updateClock();

    window.addEventListener('resize', () => {
        Object.values(chartInstances).forEach(c => c && c.resize());
    });
});
"""

# Grava os arquivos
base_dir = r"C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\ANTIGRAVITY\PROJETOS\DASHBOARD_tv"
open(os.path.join(base_dir, "templates", "trimestre.html"), "w", encoding="utf-8").write(HTML_CONTENT)
open(os.path.join(base_dir, "static", "css", "trimestre.css"), "w", encoding="utf-8").write(CSS_CONTENT)
open(os.path.join(base_dir, "static", "js", "trimestre.js"), "w", encoding="utf-8").write(JS_CONTENT)
print("Arquivos de Trimestre atualizados com sucesso no layout exato dos Canais!")
