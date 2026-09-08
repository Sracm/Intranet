// =========================================================
// MQ INTRANET — PORTAL CLIENT LOGIC
// Arquivo: static/js/portal.js
// =========================================================

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('reportSearchInput');
    const reportCards = document.querySelectorAll('.report-card');
    const emptyState = document.getElementById('reportsEmptyState');
    const counterDisplay = document.getElementById('visibleReportsCounter');
    const totalCount = reportCards.length;

    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            let visibleCount = 0;

            reportCards.forEach(card => {
                const title = card.getAttribute('data-title') || '';
                const desc = card.getAttribute('data-desc') || '';
                const dept = card.getAttribute('data-dept') || '';

                const matches = title.includes(query) || desc.includes(query) || dept.includes(query);

                if (matches) {
                    card.style.display = 'flex';
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });

            // Atualiza contador se existir
            if (counterDisplay) {
                counterDisplay.textContent = visibleCount;
            }

            // Exibe empty state se nenhum cartão for encontrado
            if (emptyState) {
                emptyState.style.display = visibleCount === 0 ? 'block' : 'none';
            }
        });
    }
});
