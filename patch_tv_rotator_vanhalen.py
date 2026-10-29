"""
Script para adicionar o botao Van Halen e a protecao de rotacao no tv_rotator.js
"""
import os

rotator_path = r"C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\ANTIGRAVITY\PROJETOS\DASHBOARD_tv\static\js\tv_rotator.js"
content = open(rotator_path, "r", encoding="utf-8").read()

# 1. Substituir o HTML da pílula para incluir o botão de Van Halen
old_pill_html = """            <button type="button" class="rotator-toggle-btn" id="tv-rotator-toggle-btn" title="Pausar / Retomar Rotação">⏸️</button>
            <button type="button" class="rotator-test-btn" id="tv-rotator-test-btn" title="Testar Alerta de Oscilação (Simula Subida e Caixa Registradora)" onclick="window.simularOscilacaoGlobal('cima', 'distribuicao'); event.stopPropagation();">⚡ Alerta</button>"""

# Pode haver pequenas variações no emoji ou texto, vamos buscar o trecho com regex ou substituir flexível
if 'id="tv-rotator-test-btn"' in content:
    # Localizar bloco onde pill.innerHTML é definido
    start_str = "pill.innerHTML = `"
    end_str = "`;\n\n        pill.addEventListener('click', togglePause);"
    start_pos = content.find(start_str)
    end_pos = content.find(end_str, start_pos)
    
    if start_pos != -1 and end_pos != -1:
        current_inner = content[start_pos + len(start_str):end_pos]
        new_inner = """
            <span class="rotator-dot pulse" id="tv-rotator-dot"></span>
            <span class="rotator-label">Auto-TV:</span>
            <span class="rotator-time" id="tv-rotator-time">02:30</span>
            <span class="rotator-divider">|</span>
            <span class="rotator-data-label">Dados:</span>
            <span class="rotator-data-time" id="tv-data-refresh-time">10:00</span>
            <button type="button" class="rotator-toggle-btn" id="tv-rotator-toggle-btn" title="Pausar / Retomar Rotação">⏸️</button>
            <button type="button" class="rotator-vanhalen-btn" id="tv-rotator-vanhalen-btn" title="Tocar Van Halen - Jump (A tela só muda após o fim da música)" onclick="window.tocarVanHalenGlobal(); event.stopPropagation();">🎸 Van Halen</button>
            <button type="button" class="rotator-test-btn" id="tv-rotator-test-btn" title="Testar Alerta de Oscilação (Simula Subida e Caixa Registradora)" onclick="window.simularOscilacaoGlobal('cima', 'distribuicao'); event.stopPropagation();">⚡ Alerta</button>"""
        content = content[:start_pos + len(start_str)] + new_inner + content[end_pos:]
        print("HTML do pill atualizado com botão Van Halen!")

# 2. Atualizar a lógica do tick para checar se a música está tocando
old_tick = """    // Ciclo de segundo a segundo
    function tick() {
        // 1. Contador de Rotação (2.5 min)
        if (!isPaused) {
            timeLeft--;
            if (timeLeft <= 0) {
                timeLeft = 0;
                updateCountdownUI();
                goToNextTab();
                return;
            }
        }"""

new_tick = """    // Ciclo de segundo a segundo
    function tick() {
        // Bloqueio de rotação: se qualquer música ou áudio de celebração estiver tocando, a tela JAMAIS muda!
        if (window.isMusicaVanHalenTocando && window.isMusicaVanHalenTocando()) {
            updateCountdownUI();
            return;
        }

        // 1. Contador de Rotação (2.5 min)
        if (!isPaused) {
            timeLeft--;
            if (timeLeft <= 0) {
                if (window.isMusicaVanHalenTocando && window.isMusicaVanHalenTocando()) {
                    timeLeft = 1; // Mantém segurando enquanto toca
                    updateCountdownUI();
                    return;
                }
                timeLeft = 0;
                updateCountdownUI();
                goToNextTab();
                return;
            }
        }"""

if old_tick in content:
    content = content.replace(old_tick, new_tick)
    print("tick() atualizado com proteção de reprodução de áudio!")
else:
    # Tenta substituição sem acentos/com encoding
    import re
    tick_pattern = re.compile(r"function tick\(\)\s*\{[\s\S]*?if\s*\(!isPaused\)\s*\{[\s\S]*?goToNextTab\(\);\s*return;\s*\}\s*\}", re.MULTILINE)
    match = tick_pattern.search(content)
    if match:
        print("Match regex encontrado para tick()!")

# 3. Adicionar estilos CSS do botão Van Halen
style_marker = ".rotator-test-btn {"
new_style = """.rotator-vanhalen-btn {
                background: linear-gradient(135deg, rgba(239, 68, 68, 0.4), rgba(220, 38, 38, 0.2));
                border: 1px solid #ef4444;
                color: #fca5a5;
                border-radius: 4px;
                padding: 1px 8px;
                font-size: 0.70rem;
                font-weight: 800;
                cursor: pointer;
                transition: all 0.2s;
                font-family: Montserrat, sans-serif;
                display: inline-flex;
                align-items: center;
                gap: 3px;
            }
            .rotator-vanhalen-btn:hover {
                background: #ef4444;
                color: #ffffff;
                box-shadow: 0 0 12px rgba(239, 68, 68, 0.7);
            }
            .rotator-vanhalen-btn.playing {
                background: #ef4444 !important;
                color: #ffffff !important;
                border-color: #fca5a5 !important;
                box-shadow: 0 0 15px rgba(239, 68, 68, 0.9);
                animation: vanHalenPulsing 1s infinite alternate;
            }
            @keyframes vanHalenPulsing {
                from { transform: scale(1); filter: brightness(1); }
                to { transform: scale(1.06); filter: brightness(1.25); }
            }
            """ + style_marker

if style_marker in content and ".rotator-vanhalen-btn" not in content:
    content = content.replace(style_marker, new_style, 1)
    print("Estilos do botão Van Halen injetados com sucesso!")

# 4. Implementar window.tocarVanHalenGlobal e window.isMusicaVanHalenTocando
vanhalen_functions = """
    // ========================================================
    // Tocar Van Halen e Segurar a Tela até Acabar
    // ========================================================
    let _vanHalenAudioObj = null;

    window.isMusicaVanHalenTocando = function () {
        if (_vanHalenAudioObj && !_vanHalenAudioObj.paused && !_vanHalenAudioObj.ended && _vanHalenAudioObj.currentTime > 0) {
            return true;
        }
        const audioEl = document.getElementById('music-sound') || document.getElementById('victory-sound');
        if (audioEl && !audioEl.paused && !audioEl.ended && audioEl.currentTime > 0) {
            return true;
        }
        return false;
    };

    window.tocarVanHalenGlobal = function () {
        let audioEl = document.getElementById('music-sound') || document.getElementById('victory-sound');
        if (!audioEl) {
            audioEl = document.createElement('audio');
            audioEl.id = 'music-sound';
            audioEl.src = '/static/audio/van_halen_jump.mp3';
            audioEl.preload = 'auto';
            document.body.appendChild(audioEl);
        }
        _vanHalenAudioObj = audioEl;

        const btnVanHalen = document.getElementById('tv-rotator-vanhalen-btn');

        // Se já estiver tocando, pausa
        if (!audioEl.paused && audioEl.currentTime > 0) {
            audioEl.pause();
            audioEl.currentTime = 0;
            if (btnVanHalen) {
                btnVanHalen.classList.remove('playing');
                btnVanHalen.innerHTML = '🎸 Van Halen';
            }
            window.tvRotator.retomarAposAudio();
            mostrarToastTV('⏸️ Música interrompida. Rotação restaurada.', '#f59e0b');
            return;
        }

        // Toca a música e PAUSA a rotação da TV
        window.tvRotator.pausarParaAudio('Van Halen - Jump');
        if (btnVanHalen) {
            btnVanHalen.classList.add('playing');
            btnVanHalen.innerHTML = '🔊 Tocando Jump...';
        }

        mostrarToastTV('🎸 <strong>Van Halen - Jump</strong> tocando! A tela só mudará após o término da música.', '#ef4444');

        audioEl.currentTime = 0;
        const playPromise = audioEl.play();
        if (playPromise !== undefined) {
            playPromise.then(() => {
                console.log('[VAN HALEN] Reprodução iniciada com sucesso. Rotação travada até o término.');
            }).catch(err => {
                console.warn('[VAN HALEN] Reprodução requer interação ou falhou:', err);
                mostrarToastTV('⚠️ Clique no botão novamente para liberar o áudio no navegador!', '#f59e0b');
            });
        }

        // Evento QUANDO A MÚSICA ACABAR:
        audioEl.onended = function () {
            console.log('[VAN HALEN] Música terminada! Liberando rotação da TV...');
            if (btnVanHalen) {
                btnVanHalen.classList.remove('playing');
                btnVanHalen.innerHTML = '🎸 Van Halen';
            }
            mostrarToastTV('🏁 Fim da música! A tela continuará a rotação normalmente.', '#10b981');
            window.tvRotator.retomarAposAudio();
            // Troca de tela logo após acabar se o tempo de tela já tiver esgotado
            goToNextTab();
        };
    };
"""

if "window.tocarVanHalenGlobal" not in content:
    content = content.replace("window.tvRotator = {", vanhalen_functions + "\n    window.tvRotator = {")
    print("Funções globais de Van Halen adicionadas ao tv_rotator.js!")

open(rotator_path, "w", encoding="utf-8").write(content)
print("tv_rotator.js atualizado com sucesso!")
