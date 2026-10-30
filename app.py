import os
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify, abort, send_file
)
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash
from config import Config
from database import (
    init_db, get_user_by_id, get_user_by_username,
    list_all_users, create_user, update_user, update_password, delete_user,
    list_all_departments, get_department_by_id, get_department_by_code, create_department, update_department, delete_department,
    list_all_reports, get_report_by_id, create_report, update_report, delete_report,
    get_reports_for_user, get_user_accessible_departments, user_can_access_report,
    get_user_department_ids, log_access, get_stats,
    list_portal_tools, create_portal_tool, update_portal_tool, delete_portal_tool,
    get_portal_settings, set_portal_setting, get_dashboard_usabilidade_analytics
)

app = Flask(__name__)
app.config.from_object(Config)

if Config.IS_PRODUCTION:
    # Na Vercel o app fica atrás de proxy: IP real e HTTPS vêm nos cabeçalhos X-Forwarded-*
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

# Inicializa banco de dados caso não exista
with app.app_context():
    init_db()

# ----------------- DECORATORS & AUTH ----------------- #

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar a Intranet.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar esta área.', 'warning')
            return redirect(url_for('login', next=request.url))
        if session.get('role') != 'admin':
            flash('Acesso restrito. Você não possui privilégios de Administrador.', 'danger')
            return redirect(url_for('portal'))
        return f(*args, **kwargs)
    return decorated_function

def resolve_embed_url(url):
    if not url:
        return ''
    try:
        host = request.host.split(':')[0]
        for origin in ('localhost:', '127.0.0.1:', '10.11.1.162:', '10.11.1.100:', '192.168.15.37:', '10.81.234.4:'):
            if origin in url:
                return url.replace(origin, f'{host}:')
    except Exception:
        pass
    return url

@app.context_processor
def inject_globals():
    user_id = session.get('user_id')
    user_depts = []
    if user_id:
        try:
            user_depts = get_user_accessible_departments(user_id, session.get('role') == 'admin')
        except Exception:
            user_depts = []
    return {
        'current_user': {
            'id': session.get('user_id'),
            'username': session.get('username'),
            'name': session.get('name'),
            'role': session.get('role'),
            'is_admin': session.get('role') == 'admin'
        } if user_id else None,
        'user_accessible_depts': user_depts,
        'resolve_url': resolve_embed_url
    }

# ----------------- ROTAS DE AUTENTICAÇÃO ----------------- #

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('portal'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Informe seu usuário e senha.', 'danger')
            return render_template('login.html', settings=get_portal_settings())

        user = get_user_by_username(username)
        if not user or not check_password_hash(user['password_hash'], password):
            flash('Usuário ou senha incorretos.', 'danger')
            return render_template('login.html', settings=get_portal_settings())

        if not user['active']:
            flash('Esta conta de usuário está desativada. Contate o Administrador.', 'danger')
            return render_template('login.html', settings=get_portal_settings())

        # Cria sessão do usuário
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['name'] = user['name']
        session['role'] = user['role']
        session['email'] = user['email']

        log_access(user['id'], None, 'login', request.remote_addr)

        flash(f'Bem-vindo(a) de volta, {user["name"]}!', 'success')
        next_page = request.args.get('next')
        # '//host' e '/\host' são tratados pelo navegador como URL externa (open redirect)
        if next_page and next_page.startswith('/') and not next_page.startswith(('//', '/\\')):
            return redirect(next_page)
        return redirect(url_for('portal'))

    return render_template('login.html', settings=get_portal_settings())

@app.route('/logout')
def logout():
    if 'user_id' in session:
        log_access(session['user_id'], None, 'logout', request.remote_addr)
    session.clear()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = get_user_by_id(session['user_id'])
    if request.method == 'POST':
        current_pwd = request.form.get('current_password', '').strip()
        new_pwd = request.form.get('new_password', '').strip()
        confirm_pwd = request.form.get('confirm_password', '').strip()

        if current_pwd or new_pwd:
            if not check_password_hash(user['password_hash'], current_pwd):
                flash('Senha atual incorreta.', 'danger')
            elif len(new_pwd) < 3:
                flash('A nova senha deve ter no mínimo 3 caracteres.', 'warning')
            elif new_pwd != confirm_pwd:
                flash('A confirmação da nova senha não confere.', 'warning')
            else:
                update_password(user['id'], new_pwd)
                flash('Sua senha foi alterada com sucesso!', 'success')
                return redirect(url_for('profile'))
        else:
            flash('Dados do perfil salvos com sucesso!', 'success')
            return redirect(url_for('profile'))

    return render_template('profile.html', user=user)

# ----------------- PORTAL PRINCIPAL ----------------- #

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('portal'))
    return redirect(url_for('login'))

@app.route('/portal')
@login_required
def portal():
    user_id = session['user_id']
    is_admin = session.get('role') == 'admin'
    selected_dept = request.args.get('dept', 'todos')

    # Busca departamentos acessíveis pelo usuário
    accessible_departments = get_user_accessible_departments(user_id, is_admin)

    # Identificar relatório em destaque (Cockpit Geral de Indicadores Estratégicos MQ)
    all_user_reports = get_reports_for_user(user_id, is_admin, 'todos')
    featured_report = None
    for r in all_user_reports:
        if r['id'] == 5 or 'Cockpit Geral' in r['title']:
            featured_report = r
            break

    current_department = None
    if selected_dept and selected_dept != 'todos':
        current_department = get_department_by_code(selected_dept)
        # No Hub setorial, traz TODOS os relatórios daquele setor sem excluir featured
        reports = get_reports_for_user(user_id, is_admin, selected_dept)
    else:
        # Na Home geral, lista os relatórios disponíveis (exclui o destaque para não duplicar no grid geral)
        raw_reports = get_reports_for_user(user_id, is_admin, 'todos')
        reports = [r for r in raw_reports if not (featured_report and r['id'] == featured_report['id'])]

    tools = list_portal_tools(only_active=True)
    return render_template(
        'index.html',
        reports=reports,
        featured_report=featured_report,
        departments=accessible_departments,
        selected_dept=selected_dept,
        current_department=current_department,
        total_reports=len(reports),
        tools=tools
    )

@app.route('/report/<int:report_id>')
@login_required
def view_report(report_id):
    user_id = session['user_id']
    is_admin = session.get('role') == 'admin'

    if not user_can_access_report(user_id, report_id, is_admin):
        flash('Você não tem permissão para visualizar este relatório.', 'danger')
        return redirect(url_for('portal'))

    report = get_report_by_id(report_id)
    if not report:
        flash('Relatório não encontrado.', 'danger')
        return redirect(url_for('portal'))

    # Registra log de visualização
    log_access(user_id, report_id, 'view_report', request.remote_addr)

    # Se for o próprio Dashboard de Usabilidade, redireciona diretamente para renderização nativa
    if report['embed_url'].strip() == '/analytics' or report['embed_url'].strip().endswith('/analytics'):
        return redirect(url_for('analytics_dashboard'))

    # Se for relatório do DRE Gestores (:5100), injeta o usuário autenticado e token seguro
    embed_url = resolve_embed_url(report['embed_url'].strip())
    username = session.get('username', '')
    if ':5100' in embed_url and username:
        import hmac, hashlib, time
        secret = os.getenv("DRE_AUTH_SECRET", "mq-hair-dre-secure-token-2026")
        exp = int(time.time()) + 86400
        payload = f"{username}:{exp}"
        sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        token = f"{payload}:{sig}"
        sep = '&' if '?' in embed_url else '?'
        embed_url = f"{embed_url}{sep}user={username}&token={token}"
    # DRE Empresa (:5150) e Dashboard TV (:5050): repassa o usuario logado para a saudacao da MQIA
    elif (':5150' in embed_url or ':5050' in embed_url) and username and 'user=' not in embed_url:
        sep = '&' if '?' in embed_url else '?'
        embed_url = f"{embed_url}{sep}user={username}"

    return render_template('report_view.html', report=report, embed_url=embed_url)

# ----------------- COCKPIT DE ANALYTICS & USABILIDADE DOS DASHBOARDS ----------------- #

@app.route('/analytics')
@login_required
def analytics_dashboard():
    month = request.args.get('month', 'todos')
    department_id = request.args.get('dept', 'todos')
    user_id = request.args.get('user', 'todos')
    report_id = request.args.get('report', 'todos')

    data = get_dashboard_usabilidade_analytics(
        month=month,
        department_id=department_id,
        user_id=user_id,
        report_id=report_id
    )

    return render_template('analytics_dashboard.html', data=data)


@app.route('/api/analytics')
@login_required
def api_analytics():
    month = request.args.get('month', 'todos')
    department_id = request.args.get('dept', 'todos')
    user_id = request.args.get('user', 'todos')
    report_id = request.args.get('report', 'todos')

    data = get_dashboard_usabilidade_analytics(
        month=month,
        department_id=department_id,
        user_id=user_id,
        report_id=report_id
    )
    return jsonify(data)


@app.route('/api/analytics/log', methods=['POST'])
@app.route('/api/log_access', methods=['GET', 'POST'])
def api_log_access():
    user_id = None
    report_id = None
    action = 'view_report'

    if request.method == 'POST':
        data = request.get_json(silent=True) or request.form
        username = data.get('username')
        report_id = data.get('report_id')
        action = data.get('action', 'view_report')
    else:
        username = request.args.get('username')
        report_id = request.args.get('report_id')
        action = request.args.get('action', 'view_report')

    if username:
        user = get_user_by_username(username)
        if user:
            user_id = user['id']
    elif 'user_id' in session:
        user_id = session['user_id']

    if report_id:
        try:
            report_id = int(report_id)
        except Exception:
            report_id = None

    if user_id or report_id:
        log_access(user_id, report_id, action, request.remote_addr)
        return jsonify({'status': 'ok', 'logged': True})
    return jsonify({'status': 'ignored', 'reason': 'no user or report identified'}), 400


# ----------------- PAINEL ADMINISTRATIVO ----------------- #

@app.route('/admin')
@admin_required
def admin_dashboard():
    stats = get_stats()
    return render_template('admin/dashboard.html', stats=stats)

# Gestão de Usuários
@app.route('/admin/users', methods=['GET', 'POST'])
@admin_required
def admin_users():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'create':
            username = request.form.get('username', '').strip()
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            role = request.form.get('role', 'user')
            dept_id = request.form.get('department_id') or None
            extra_depts = request.form.getlist('extra_departments')

            if not username or not name or not password:
                flash('Preencha os campos obrigatórios (Usuário, Nome e Senha).', 'danger')
            else:
                user_id = create_user(username, name, email, password, role, dept_id, extra_depts)
                if user_id:
                    flash(f'Usuário "{name}" cadastrado com sucesso!', 'success')
                else:
                    flash(f'O usuário "{username}" já existe.', 'danger')
            return redirect(url_for('admin_users'))

        elif action == 'edit':
            user_id = int(request.form.get('user_id'))
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            role = request.form.get('role', 'user')
            dept_id = request.form.get('department_id') or None
            active = 1 if request.form.get('active') == '1' else 0
            extra_depts = request.form.getlist('extra_departments')
            new_pwd = request.form.get('new_password', '')

            update_user(user_id, name, email, role, dept_id, active, extra_depts, new_pwd)
            flash(f'Dados do usuário atualizados com sucesso!', 'success')
            return redirect(url_for('admin_users'))

        elif action == 'delete':
            user_id = int(request.form.get('user_id'))
            if user_id == session['user_id']:
                flash('Você não pode excluir sua própria conta de administrador.', 'danger')
            else:
                delete_user(user_id)
                flash('Usuário removido com sucesso.', 'info')
            return redirect(url_for('admin_users'))

    users = list_all_users()
    departments = list_all_departments()
    
    # Prepara mapa de departamentos extras por usuário
    user_depts_map = {}
    for u in users:
        user_depts_map[u['id']] = get_user_department_ids(u['id'])

    return render_template('admin/users.html', users=users, departments=departments, user_depts_map=user_depts_map)

# Gestão de Departamentos
@app.route('/admin/departments', methods=['GET', 'POST'])
@admin_required
def admin_departments():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'create':
            name = request.form.get('name', '').strip()
            code = request.form.get('code', '').strip().lower()
            description = request.form.get('description', '').strip()
            icon = request.form.get('icon', 'bi-folder').strip()
            color = request.form.get('color', '#CB9727').strip()

            if not name or not code:
                flash('Nome e Código são obrigatórios.', 'danger')
            else:
                dept_id = create_department(name, code, description, icon, color)
                if dept_id:
                    flash(f'Departamento "{name}" criado com sucesso!', 'success')
                else:
                    flash(f'Já existe um departamento com o código "{code}".', 'danger')
            return redirect(url_for('admin_departments'))

        elif action == 'edit':
            dept_id = int(request.form.get('dept_id'))
            name = request.form.get('name', '').strip()
            code = request.form.get('code', '').strip().lower()
            description = request.form.get('description', '').strip()
            icon = request.form.get('icon', 'bi-folder').strip()
            color = request.form.get('color', '#CB9727').strip()

            update_department(dept_id, name, code, description, icon, color)
            flash(f'Departamento "{name}" atualizado com sucesso!', 'success')
            return redirect(url_for('admin_departments'))

        elif action == 'delete':
            dept_id = int(request.form.get('dept_id'))
            delete_department(dept_id)
            flash('Departamento excluído com sucesso.', 'info')
            return redirect(url_for('admin_departments'))

    departments = list_all_departments()
    return render_template('admin/departments.html', departments=departments)

# Gestão de Relatórios
@app.route('/admin/reports', methods=['GET', 'POST'])
@admin_required
def admin_reports():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'create':
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            department_id = request.form.get('department_id', type=int)
            embed_url = request.form.get('embed_url', '').strip()
            icon = request.form.get('icon', 'bi-bar-chart-line').strip()
            is_public = 1 if request.form.get('is_public') == '1' else 0
            display_order = request.form.get('display_order', 0, type=int)
            active = 1 if request.form.get('active', '1') == '1' else 0

            if not title or not embed_url or not department_id:
                flash('Título, Departamento e URL do Power BI são obrigatórios.', 'danger')
            else:
                create_report(title, description, department_id, embed_url, icon, is_public, display_order, active)
                flash(f'Relatório "{title}" cadastrado com sucesso!', 'success')
            return redirect(url_for('admin_reports'))

        elif action == 'edit':
            report_id = request.form.get('report_id', type=int)
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            department_id = request.form.get('department_id', type=int)
            embed_url = request.form.get('embed_url', '').strip()
            icon = request.form.get('icon', 'bi-bar-chart-line').strip()
            is_public = 1 if request.form.get('is_public') == '1' else 0
            display_order = request.form.get('display_order', 0, type=int)
            active = 1 if request.form.get('active') == '1' else 0

            if not report_id or not title or not embed_url or not department_id:
                flash('Relatório, título, departamento e URL do Power BI são obrigatórios.', 'danger')
            else:
                update_report(report_id, title, description, department_id, embed_url, icon, is_public, display_order, active)
                flash(f'Relatório "{title}" atualizado com sucesso!', 'success')
            return redirect(url_for('admin_reports'))

        elif action == 'delete':
            report_id = request.form.get('report_id', type=int)
            if report_id:
                delete_report(report_id)
                flash('Relatório removido com sucesso.', 'info')
            else:
                flash('Relatório inválido.', 'danger')
            return redirect(url_for('admin_reports'))

    reports = list_all_reports()
    departments = list_all_departments()
    return render_template('admin/reports.html', reports=reports, departments=departments)




# ----------------- ADMIN: FERRAMENTAS RÁPIDAS & CONFIGURAÇÕES ----------------- #

@app.route('/admin/tools', methods=['GET', 'POST'])
@admin_required
def admin_tools():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            title = request.form.get('title', '').strip()
            url = request.form.get('url', '').strip()
            icon = request.form.get('icon', 'bi-link-45deg').strip()
            custom_svg = request.form.get('custom_svg', '').strip()
            is_active = 1 if request.form.get('is_active') == '1' else 0
            display_order = int(request.form.get('display_order', 0) or 0)
            if title and url:
                create_portal_tool(title, url, icon, custom_svg, is_active, display_order)
                flash(f'Ferramenta "{title}" adicionada com sucesso!', 'success')
            else:
                flash('Título e URL são obrigatórios.', 'danger')
            return redirect(url_for('admin_tools'))

        elif action == 'edit':
            tool_id = int(request.form.get('tool_id'))
            title = request.form.get('title', '').strip()
            url = request.form.get('url', '').strip()
            icon = request.form.get('icon', 'bi-link-45deg').strip()
            custom_svg = request.form.get('custom_svg', '').strip()
            is_active = 1 if request.form.get('is_active') == '1' else 0
            display_order = int(request.form.get('display_order', 0) or 0)
            update_portal_tool(tool_id, title, url, icon, custom_svg, is_active, display_order)
            flash(f'Ferramenta atualizada com sucesso!', 'success')
            return redirect(url_for('admin_tools'))

        elif action == 'delete':
            tool_id = int(request.form.get('tool_id'))
            delete_portal_tool(tool_id)
            flash('Ferramenta removida com sucesso.', 'info')
            return redirect(url_for('admin_tools'))

    tools = list_portal_tools(only_active=False)
    return render_template('admin/tools.html', tools=tools)


@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    if request.method == 'POST':
        bg_type = request.form.get('login_bg_type', 'video')
        yt_url = request.form.get('login_bg_youtube_url', '').strip()
        img_url = request.form.get('login_bg_image_url', '').strip()
        title = request.form.get('login_bg_title', '').strip()

        set_portal_setting('login_bg_type', bg_type, 'Tipo de fundo: video ou image')
        set_portal_setting('login_bg_youtube_url', yt_url, 'URL do vídeo YouTube')
        set_portal_setting('login_bg_image_url', img_url, 'URL da imagem de fundo')
        set_portal_setting('login_bg_title', title, 'Título institucional')
        flash('Configurações visuais salvas com sucesso!', 'success')
        return redirect(url_for('admin_settings'))

    settings = get_portal_settings()
    return render_template('admin/settings.html', settings=settings)


# ----------------- PORTFÓLIO EXECUTIVO (SITE & PDF) ----------------- #

@app.route('/portfolio')
def portfolio():
    """
    Página web pública do Portfólio Executivo de Dashboards,
    apresentando catálogo com mais de 60 soluções analíticas, estatísticas e filtros dinâmicos.
    """
    import json
    dataset_file = os.path.join(os.path.dirname(__file__), 'portfolio_final_dataset.json')
    if os.path.exists(dataset_file):
        with open(dataset_file, 'r', encoding='utf-8') as f:
            dashboards = json.load(f)
    else:
        dashboards = []
    
    return render_template('portfolio.html', dashboards_json=json.dumps(dashboards, ensure_ascii=False))


@app.route('/dre_assistencia/')
@app.route('/dre_assistencia/<path:filename>')
def serve_dre_assistencia_portfolio(filename='index.html'):
    from flask import send_from_directory
    dre_dir = os.path.join(os.path.dirname(__file__), 'portfolio_standalone', 'dre_assistencia')
    return send_from_directory(dre_dir, filename)


@app.route('/dre_empresa/')
@app.route('/dre_empresa/<path:filename>')
def serve_dre_empresa_portfolio(filename='index.html'):
    from flask import send_from_directory
    emp_dir = os.path.join(os.path.dirname(__file__), 'portfolio_standalone', 'dre_empresa')
    return send_from_directory(emp_dir, filename)


@app.route('/ecommerce/')
@app.route('/ecommerce/<path:filename>')
def serve_ecommerce_portfolio(filename='index.html'):
    from flask import send_from_directory
    ecom_dir = os.path.join(os.path.dirname(__file__), 'portfolio_standalone', 'ecommerce')
    return send_from_directory(ecom_dir, filename)


@app.route('/dashboard_tv/')
@app.route('/dashboard_tv/<path:filename>')
def serve_dashboard_tv_portfolio(filename='tv.html'):
    from flask import send_from_directory
    tv_dir = os.path.join(os.path.dirname(__file__), 'portfolio_standalone', 'dashboard_tv')
    return send_from_directory(tv_dir, filename)



@app.route('/portfolio/download-pdf')
def download_portfolio_pdf():
    """
    Download do PDF executivo diagramado e pronto para envio a recrutadores e vagas de emprego.
    """
    pdf_path = os.path.join(os.path.dirname(__file__), 'static', 'portfolio_anderson_mello.pdf')
    
    # Se o PDF ainda não existir, regera automaticamente
    if not os.path.exists(pdf_path):
        from generate_portfolio_pdf import generate_portfolio_pdf
        generate_portfolio_pdf()
        
    return send_file(
        pdf_path,
        as_attachment=True,
        download_name='Portfolio_Anderson_Mello_BI_Executive.pdf',
        mimetype='application/pdf'
    )


@app.route('/Portfolio_Antonio_Mello_BI_Executive.pptx')
@app.route('/portfolio/download-pptx')
def download_portfolio_pptx():
    """
    Download do PowerPoint (.pptx) editável do portfólio.
    """
    pptx_path = os.path.join(os.path.dirname(__file__), 'static', 'Portfolio_Antonio_Mello_BI_Executive.pptx')
    if not os.path.exists(pptx_path):
        from create_portfolio_pptx import create_portfolio_powerpoint
        create_portfolio_powerpoint(output_pptx=pptx_path)
        
    return send_file(
        pptx_path,
        as_attachment=True,
        download_name='Portfolio_Antonio_Mello_BI_Executive.pptx',
        mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation'
    )



@app.route('/curriculo')
@app.route('/curriculo.html')
def serve_curriculo():
    curriculo_path = os.path.join(os.path.dirname(__file__), 'portfolio_standalone', 'curriculo.html')
    return send_file(curriculo_path, mimetype='text/html')


@app.route('/curriculo/download-pdf')
@app.route('/Curriculo_Antonio_Carlos_de_Mello_BI.pdf')
def serve_curriculo_pdf():
    pdf_path = os.path.join(os.path.dirname(__file__), 'portfolio_standalone', 'Curriculo_Antonio_Carlos_de_Mello_BI.pdf')
    if not os.path.exists(pdf_path):
        pdf_path = os.path.join(os.path.dirname(__file__), 'Curriculo_Antonio_Carlos_de_Mello_BI.pdf')
    return send_file(
        pdf_path,
        as_attachment=True,
        download_name='Curriculo_Antonio_Carlos_de_Mello_BI.pdf',
        mimetype='application/pdf'
    )


@app.route('/Portfolio_Antonio_Mello_BI_Executive.pdf')
def serve_portfolio_pdf_direct():
    pdf_path = os.path.join(os.path.dirname(__file__), 'portfolio_standalone', 'Portfolio_Antonio_Mello_BI_Executive.pdf')
    if not os.path.exists(pdf_path):
        pdf_path = os.path.join(os.path.dirname(__file__), 'static', 'Portfolio_Antonio_Mello_BI_Executive.pdf')
    return send_file(
        pdf_path,
        as_attachment=True,
        download_name='Portfolio_Antonio_Mello_BI_Executive.pdf',
        mimetype='application/pdf'
    )


if __name__ == '__main__':
    print(f"Iniciando Portal Intranet MQ em http://localhost:{Config.PORT}")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG, use_reloader=False)
