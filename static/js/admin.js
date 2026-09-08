// =========================================================
// MQ INTRANET — ADMIN MANAGEMENT LOGIC
// Arquivo: static/js/admin.js
// =========================================================

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = '';
    }
}

// Fechar modal clicando fora do conteúdo
window.addEventListener('click', (e) => {
    if (e.target.classList.contains('mq-modal-backdrop')) {
        e.target.classList.remove('show');
        document.body.style.overflow = '';
    }
});

// Funções para Usuários
function editUser(user, extraDeptIds) {
    document.getElementById('edit_user_id').value = user.id;
    document.getElementById('edit_username').value = user.username;
    document.getElementById('edit_name').value = user.name;
    document.getElementById('edit_email').value = user.email || '';
    document.getElementById('edit_role').value = user.role;
    document.getElementById('edit_department_id').value = user.department_id || '';
    document.getElementById('edit_active').value = user.active ? '1' : '0';
    document.getElementById('edit_new_password').value = '';

    // Checkboxes de departamentos
    const checkboxes = document.querySelectorAll('#editUserModal .dept-extra-checkbox');
    checkboxes.forEach(cb => {
        const val = parseInt(cb.value);
        cb.checked = extraDeptIds && extraDeptIds.includes(val);
    });

    openModal('editUserModal');
}

// Funções para Departamentos
function editDepartment(dept) {
    document.getElementById('edit_dept_id').value = dept.id;
    document.getElementById('edit_dept_name').value = dept.name;
    document.getElementById('edit_dept_code').value = dept.code;
    document.getElementById('edit_dept_description').value = dept.description || '';
    document.getElementById('edit_dept_icon').value = dept.icon || 'bi-folder';
    document.getElementById('edit_dept_color').value = dept.color || '#CB9727';

    openModal('editDeptModal');
}

// Funções para Relatórios
function editReport(report) {
    document.getElementById('edit_report_id').value = report.id;
    document.getElementById('edit_report_title').value = report.title;
    document.getElementById('edit_report_description').value = report.description || '';
    document.getElementById('edit_report_department_id').value = report.department_id;
    document.getElementById('edit_report_embed_url').value = report.embed_url;
    document.getElementById('edit_report_icon').value = report.icon || 'bi-bar-chart-line';
    document.getElementById('edit_report_is_public').value = report.is_public ? '1' : '0';
    document.getElementById('edit_report_display_order').value = report.display_order || 0;
    document.getElementById('edit_report_active').value = report.active ? '1' : '0';

    openModal('editReportModal');
}
