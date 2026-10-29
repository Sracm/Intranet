import datetime
import sqlite3
import pymysql
import pymysql.cursors
from werkzeug.security import generate_password_hash
from config import Config

if getattr(Config, 'USE_MARIADB', False):
    IntegrityError = pymysql.IntegrityError
elif Config.USE_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    IntegrityError = psycopg2.IntegrityError
else:
    IntegrityError = sqlite3.IntegrityError

# ----------------- CONEXÃO (SQLite em dev / PostgreSQL em produção) ----------------- #

class _PgCursor:
    """Cursor psycopg2 com a mesma interface usada com sqlite3 (placeholders '?')."""

    def __init__(self, raw_cursor):
        self._cur = raw_cursor

    def execute(self, sql, params=()):
        # '%' literal precisa ser escapado antes de converter os placeholders
        self._cur.execute(sql.replace('%', '%%').replace('?', '%s'), tuple(params))
        return self

    def fetchone(self):
        return self._cur.fetchone()

    def fetchall(self):
        return self._cur.fetchall()


class _PgConnection:
    def __init__(self, raw_conn):
        self._conn = raw_conn

    def cursor(self):
        return _PgCursor(self._conn.cursor(cursor_factory=RealDictCursor))

    def execute(self, sql, params=()):
        return self.cursor().execute(sql, params)

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()


class _MariaDBCursor:
    def __init__(self, raw_cursor):
        self._cur = raw_cursor

    def execute(self, sql, params=()):
        self._cur.execute(sql.replace('%', '%%').replace('?', '%s'), tuple(params))
        return self

    def fetchone(self):
        return self._cur.fetchone()

    def fetchall(self):
        return self._cur.fetchall()
        
    @property
    def lastrowid(self):
        return self._cur.lastrowid

class _MariaDBConnection:
    def __init__(self, raw_conn):
        self._conn = raw_conn

    def cursor(self):
        return _MariaDBCursor(self._conn.cursor())

    def execute(self, sql, params=()):
        return self.cursor().execute(sql, params)

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()


def get_db():
    if getattr(Config, 'USE_MARIADB', False):
        try:
            conn = pymysql.connect(
                host=Config.MARIADB_HOST,
                user=Config.MARIADB_USER,
                password=Config.MARIADB_PASSWORD,
                database=Config.MARIADB_DB,
                port=Config.MARIADB_PORT,
                connect_timeout=2,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            return _MariaDBConnection(conn)
        except Exception as e:
            print(f"[AVISO] Falha ao conectar ao MariaDB ({e}). Utilizando SQLite local.", flush=True)
            Config.USE_MARIADB = False
    if Config.USE_POSTGRES:
        return _PgConnection(psycopg2.connect(Config.DATABASE_URL))
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def _insert_returning_id(cursor, sql, params):
    if getattr(Config, 'USE_MARIADB', False):
        cursor.execute(sql, params)
        return cursor.lastrowid
    if Config.USE_POSTGRES:
        return cursor.execute(sql + ' RETURNING id', params).fetchone()['id']
    cursor.execute(sql, params)
    return cursor.lastrowid

_SCHEMA_POSTGRES = '''
    CREATE TABLE IF NOT EXISTS departments (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        code TEXT UNIQUE NOT NULL,
        description TEXT,
        icon TEXT DEFAULT 'bi-folder',
        color TEXT DEFAULT '#CB9727',
        created_at TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        email TEXT,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        department_id INTEGER REFERENCES departments (id) ON DELETE SET NULL,
        active INTEGER DEFAULT 1,
        created_at TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS user_departments (
        user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
        department_id INTEGER NOT NULL REFERENCES departments (id) ON DELETE CASCADE,
        PRIMARY KEY (user_id, department_id)
    );

    CREATE TABLE IF NOT EXISTS reports (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        department_id INTEGER NOT NULL REFERENCES departments (id) ON DELETE CASCADE,
        embed_url TEXT NOT NULL,
        icon TEXT DEFAULT 'bi-bar-chart-line',
        is_public INTEGER DEFAULT 0,
        display_order INTEGER DEFAULT 0,
        active INTEGER DEFAULT 1,
        created_at TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS user_reports (
        user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
        report_id INTEGER NOT NULL REFERENCES reports (id) ON DELETE CASCADE,
        PRIMARY KEY (user_id, report_id)
    );

    CREATE TABLE IF NOT EXISTS access_logs (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users (id) ON DELETE SET NULL,
        report_id INTEGER REFERENCES reports (id) ON DELETE SET NULL,
        action TEXT NOT NULL,
        ip_address TEXT,
        created_at TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP
    );
'''

_SCHEMA_MARIADB = '''
    CREATE TABLE IF NOT EXISTS departments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        code VARCHAR(255) UNIQUE NOT NULL,
        description TEXT,
        icon VARCHAR(255) DEFAULT 'bi-folder',
        color VARCHAR(255) DEFAULT '#CB9727',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255),
        password_hash VARCHAR(255) NOT NULL,
        role VARCHAR(255) DEFAULT 'user',
        department_id INT,
        active INT DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (department_id) REFERENCES departments (id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS user_departments (
        user_id INT NOT NULL,
        department_id INT NOT NULL,
        PRIMARY KEY (user_id, department_id),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (department_id) REFERENCES departments (id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS reports (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        department_id INT NOT NULL,
        embed_url TEXT NOT NULL,
        icon VARCHAR(255) DEFAULT 'bi-bar-chart-line',
        is_public INT DEFAULT 0,
        display_order INT DEFAULT 0,
        active INT DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (department_id) REFERENCES departments (id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS user_reports (
        user_id INT NOT NULL,
        report_id INT NOT NULL,
        PRIMARY KEY (user_id, report_id),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (report_id) REFERENCES reports (id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS access_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        report_id INT,
        action VARCHAR(255) NOT NULL,
        ip_address VARCHAR(255),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL,
        FOREIGN KEY (report_id) REFERENCES reports (id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS portal_tools (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        url VARCHAR(255) NOT NULL,
        icon VARCHAR(255) DEFAULT 'bi-link-45deg',
        custom_svg TEXT,
        is_active INT DEFAULT 1,
        display_order INT DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS portal_settings (
        `key` VARCHAR(255) PRIMARY KEY,
        value TEXT,
        description TEXT,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
'''

def init_db():
    if getattr(Config, 'USE_MARIADB', False):
        try:
            conn = pymysql.connect(
                host=Config.MARIADB_HOST,
                user=Config.MARIADB_USER,
                password=Config.MARIADB_PASSWORD,
                database=Config.MARIADB_DB,
                port=Config.MARIADB_PORT,
                connect_timeout=2,
                autocommit=True
            )
            with conn.cursor() as cursor:
                # pymysql requires splitting multiple statements or executing one by one
                for statement in _SCHEMA_MARIADB.split(';'):
                    if statement.strip():
                        cursor.execute(statement)
            conn.close()
            return
        except Exception as e:
            print(f"[AVISO] Falha ao conectar ao MariaDB em init_db ({e}). Utilizando SQLite local.", flush=True)
            Config.USE_MARIADB = False

    if Config.USE_POSTGRES:
        conn = psycopg2.connect(Config.DATABASE_URL)
        with conn.cursor() as cursor:
            cursor.execute(_SCHEMA_POSTGRES)
        conn.commit()
        conn.close()
        return

    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        code TEXT UNIQUE NOT NULL,
        description TEXT,
        icon TEXT DEFAULT 'bi-folder',
        color TEXT DEFAULT '#CB9727',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        email TEXT,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'user', -- 'admin' ou 'user'
        department_id INTEGER,
        active INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (department_id) REFERENCES departments (id) ON DELETE SET NULL
    );

    CREATE TABLE IF NOT EXISTS user_departments (
        user_id INTEGER NOT NULL,
        department_id INTEGER NOT NULL,
        PRIMARY KEY (user_id, department_id),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (department_id) REFERENCES departments (id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        department_id INTEGER NOT NULL,
        embed_url TEXT NOT NULL,
        icon TEXT DEFAULT 'bi-bar-chart-line',
        is_public INTEGER DEFAULT 0, -- 1 se visível para todos os usuários logados
        display_order INTEGER DEFAULT 0,
        active INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (department_id) REFERENCES departments (id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS user_reports (
        user_id INTEGER NOT NULL,
        report_id INTEGER NOT NULL,
        PRIMARY KEY (user_id, report_id),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (report_id) REFERENCES reports (id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS access_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        report_id INTEGER,
        action TEXT NOT NULL,
        ip_address TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL,
        FOREIGN KEY (report_id) REFERENCES reports (id) ON DELETE SET NULL
    );
    ''')

    conn.commit()
    conn.close()

# ----------------- USUÁRIOS ----------------- #

def get_user_by_id(user_id):
    conn = get_db()
    user = conn.execute('''
        SELECT u.*, d.name as department_name 
        FROM users u 
        LEFT JOIN departments d ON u.department_id = d.id 
        WHERE u.id = ?
    ''', (user_id,)).fetchone()
    conn.close()
    return user

def get_user_by_username(username):
    conn = get_db()
    user = conn.execute('''
        SELECT u.*, d.name as department_name 
        FROM users u 
        LEFT JOIN departments d ON u.department_id = d.id 
        WHERE LOWER(u.username) = LOWER(?)
    ''', (username.strip(),)).fetchone()
    conn.close()
    return user

def create_user(username, name, email, password, role='user', department_id=None, extra_dept_ids=None):
    conn = get_db()
    cursor = conn.cursor()
    pwd_hash = generate_password_hash(password)
    try:
        user_id = _insert_returning_id(cursor, '''
            INSERT INTO users (username, name, email, password_hash, role, department_id, active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        ''', (username.strip().lower(), name.strip(), email.strip() if email else '', pwd_hash, role, department_id))

        # Atribuir departamento principal também em user_departments
        dept_ids_to_add = set()
        if department_id:
            dept_ids_to_add.add(int(department_id))
        if extra_dept_ids:
            for d in extra_dept_ids:
                dept_ids_to_add.add(int(d))

        for d_id in dept_ids_to_add:
            cursor.execute('INSERT INTO user_departments (user_id, department_id) VALUES (?, ?) ON CONFLICT DO NOTHING', (user_id, d_id))

        conn.commit()
        return user_id
    except IntegrityError:
        return None
    finally:
        conn.close()

def update_user(user_id, name, email, role, department_id, active, extra_dept_ids=None, new_password=None):
    conn = get_db()
    cursor = conn.cursor()
    
    if new_password and new_password.strip():
        pwd_hash = generate_password_hash(new_password.strip())
        cursor.execute('''
            UPDATE users 
            SET name = ?, email = ?, role = ?, department_id = ?, active = ?, password_hash = ?
            WHERE id = ?
        ''', (name.strip(), email.strip() if email else '', role, department_id, int(active), pwd_hash, user_id))
    else:
        cursor.execute('''
            UPDATE users 
            SET name = ?, email = ?, role = ?, department_id = ?, active = ?
            WHERE id = ?
        ''', (name.strip(), email.strip() if email else '', role, department_id, int(active), user_id))

    # Atualiza departamentos extras
    cursor.execute('DELETE FROM user_departments WHERE user_id = ?', (user_id,))
    dept_ids_to_add = set()
    if department_id:
        dept_ids_to_add.add(int(department_id))
    if extra_dept_ids:
        for d in extra_dept_ids:
            if d:
                dept_ids_to_add.add(int(d))

    for d_id in dept_ids_to_add:
        cursor.execute('INSERT INTO user_departments (user_id, department_id) VALUES (?, ?) ON CONFLICT DO NOTHING', (user_id, d_id))

    conn.commit()
    conn.close()

def update_password(user_id, new_password):
    conn = get_db()
    pwd_hash = generate_password_hash(new_password)
    conn.execute('UPDATE users SET password_hash = ? WHERE id = ?', (pwd_hash, user_id))
    conn.commit()
    conn.close()

def delete_user(user_id):
    conn = get_db()
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

def list_all_users():
    conn = get_db()
    concat_fn = 'STRING_AGG' if Config.USE_POSTGRES else 'GROUP_CONCAT'
    users = conn.execute(f'''
        SELECT u.*, d.name as department_name,
               (SELECT {concat_fn}(d2.name, ', ')
                FROM user_departments ud 
                JOIN departments d2 ON ud.department_id = d2.id 
                WHERE ud.user_id = u.id) as all_departments
        FROM users u
        LEFT JOIN departments d ON u.department_id = d.id
        ORDER BY u.role DESC, u.name ASC
    ''').fetchall()
    conn.close()
    return [dict(user) for user in users]

def get_user_department_ids(user_id):
    conn = get_db()
    rows = conn.execute('SELECT department_id FROM user_departments WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()
    return [r['department_id'] for r in rows]

# ----------------- DEPARTAMENTOS ----------------- #

def list_all_departments():
    conn = get_db()
    departments = conn.execute('''
        SELECT d.*, 
               (SELECT COUNT(*) FROM reports r WHERE r.department_id = d.id AND r.active = 1) as report_count,
               (SELECT COUNT(DISTINCT user_id) FROM user_departments ud WHERE ud.department_id = d.id) as user_count
        FROM departments d 
        ORDER BY d.name ASC
    ''').fetchall()
    conn.close()
    return [dict(department) for department in departments]

def get_department_by_id(dept_id):
    conn = get_db()
    dept = conn.execute('SELECT * FROM departments WHERE id = ?', (dept_id,)).fetchone()
    conn.close()
    return dept

def get_department_by_code(code):
    conn = get_db()
    dept = conn.execute('SELECT * FROM departments WHERE code = ?', (code.strip().lower(),)).fetchone()
    conn.close()
    return dict(dept) if dept else None

def create_department(name, code, description='', icon='bi-folder', color='#CB9727'):
    conn = get_db()
    cursor = conn.cursor()
    try:
        dept_id = _insert_returning_id(cursor, '''
            INSERT INTO departments (name, code, description, icon, color)
            VALUES (?, ?, ?, ?, ?)
        ''', (name.strip(), code.strip().lower(), description.strip(), icon, color))
        conn.commit()
        return dept_id
    except IntegrityError:
        return None
    finally:
        conn.close()

def update_department(dept_id, name, code, description='', icon='bi-folder', color='#CB9727'):
    conn = get_db()
    conn.execute('''
        UPDATE departments 
        SET name = ?, code = ?, description = ?, icon = ?, color = ?
        WHERE id = ?
    ''', (name.strip(), code.strip().lower(), description.strip(), icon, color, dept_id))
    conn.commit()
    conn.close()

def delete_department(dept_id):
    conn = get_db()
    conn.execute('DELETE FROM departments WHERE id = ?', (dept_id,))
    conn.commit()
    conn.close()

# ----------------- RELATÓRIOS ----------------- #

def list_all_reports():
    conn = get_db()
    reports = conn.execute('''
        SELECT r.*, d.name as department_name, d.color as department_color, d.code as department_code
        FROM reports r
        JOIN departments d ON r.department_id = d.id
        ORDER BY r.display_order ASC, r.title ASC
    ''').fetchall()
    conn.close()
    return [dict(report) for report in reports]

def get_report_by_id(report_id):
    conn = get_db()
    report = conn.execute('''
        SELECT r.*, d.name as department_name, d.color as department_color, d.code as department_code
        FROM reports r
        JOIN departments d ON r.department_id = d.id
        WHERE r.id = ?
    ''', (report_id,)).fetchone()
    conn.close()
    return report

def get_reports_for_user(user_id, is_admin=False, department_code=None):
    conn = get_db()
    
    if is_admin:
        query = '''
            SELECT r.*, d.name as department_name, d.color as department_color, d.code as department_code
            FROM reports r
            JOIN departments d ON r.department_id = d.id
            WHERE r.active = 1
        '''
        params = []
        if department_code and department_code != 'todos':
            query += ' AND d.code = ?'
            params.append(department_code)
        query += ' ORDER BY r.display_order ASC, r.title ASC'
        reports = conn.execute(query, params).fetchall()
    else:
        # Usuário comum: vê relatórios públicos OU relatórios dos seus departamentos OU relatórios permitidos diretamente
        query = '''
            SELECT DISTINCT r.*, d.name as department_name, d.color as department_color, d.code as department_code
            FROM reports r
            JOIN departments d ON r.department_id = d.id
            WHERE r.active = 1 AND (
                r.is_public = 1
                OR r.department_id IN (SELECT department_id FROM user_departments WHERE user_id = ?)
                OR r.id IN (SELECT report_id FROM user_reports WHERE user_id = ?)
            )
        '''
        params = [user_id, user_id]
        if department_code and department_code != 'todos':
            query += ' AND d.code = ?'
            params.append(department_code)
        query += ' ORDER BY r.display_order ASC, r.title ASC'
        reports = conn.execute(query, params).fetchall()
        
    # Ranking por popularidade: mais acessados primeiro (desempate pela ordem manual e título)
    counts = {
        row['report_id']: row['n']
        for row in conn.execute(
            "SELECT report_id, COUNT(*) AS n FROM access_logs "
            "WHERE action = 'view_report' AND report_id IS NOT NULL GROUP BY report_id"
        ).fetchall()
    }
    conn.close()

    ranked = []
    for report in reports:
        item = dict(report)
        item['views'] = counts.get(item['id'], 0)
        ranked.append(item)
    # display_order negativo = card fixado no topo (ordem crescente); demais por acessos
    ranked.sort(key=lambda r: (
        0 if (r.get('display_order') or 0) < 0 else 1,
        (r.get('display_order') or 0) if (r.get('display_order') or 0) < 0 else 0,
        -r['views'],
        r.get('display_order') or 0,
        (r.get('title') or '').lower(),
    ))

    # Top 3 (não fixados) com pelo menos 1 acesso recebem o selo "Mais acessado"
    unpinned_pos = 0
    for item in ranked:
        if (item.get('display_order') or 0) < 0:
            item['is_top'] = False
            continue
        item['is_top'] = unpinned_pos < 3 and item['views'] > 0
        unpinned_pos += 1
    return ranked

def get_user_accessible_departments(user_id, is_admin=False):
    conn = get_db()
    if is_admin:
        depts_rows = conn.execute('''
            SELECT DISTINCT d.* 
            FROM departments d
            JOIN reports r ON r.department_id = d.id AND r.active = 1
            ORDER BY d.name ASC
        ''').fetchall()
    else:
        depts_rows = conn.execute('''
            SELECT DISTINCT d.* 
            FROM departments d
            JOIN reports r ON r.department_id = d.id AND r.active = 1
            WHERE (
                r.is_public = 1
                OR d.id IN (SELECT department_id FROM user_departments WHERE user_id = ?)
                OR r.id IN (SELECT report_id FROM user_reports WHERE user_id = ?)
            )
            ORDER BY d.name ASC
        ''', (user_id, user_id)).fetchall()

    depts = []
    for d in depts_rows:
        dept_dict = dict(d)
        if is_admin:
            rep_rows = conn.execute('''
                SELECT id, title, embed_url, icon, is_public, display_order
                FROM reports
                WHERE department_id = ? AND active = 1
                ORDER BY 
                    CASE WHEN title LIKE '%DRE%' THEN 0 ELSE 1 END,
                    display_order ASC,
                    id ASC
            ''', (dept_dict['id'],)).fetchall()
        else:
            rep_rows = conn.execute('''
                SELECT id, title, embed_url, icon, is_public, display_order
                FROM reports
                WHERE department_id = ? AND active = 1
                  AND (
                      is_public = 1
                      OR ? IN (SELECT user_id FROM user_departments WHERE department_id = ?)
                      OR id IN (SELECT report_id FROM user_reports WHERE user_id = ?)
                  )
                ORDER BY 
                    CASE WHEN title LIKE '%DRE%' THEN 0 ELSE 1 END,
                    display_order ASC,
                    id ASC
            ''', (dept_dict['id'], user_id, dept_dict['id'], user_id)).fetchall()

        dept_dict['reports'] = [dict(r) for r in rep_rows]
        dept_dict['primary_report_id'] = dept_dict['reports'][0]['id'] if dept_dict['reports'] else None
        depts.append(dept_dict)

    conn.close()
    return depts

def user_can_access_report(user_id, report_id, is_admin=False):
    if is_admin:
        return True
    conn = get_db()
    row = conn.execute('''
        SELECT 1 FROM reports r
        WHERE r.id = ? AND r.active = 1 AND (
            r.is_public = 1
            OR r.department_id IN (SELECT department_id FROM user_departments WHERE user_id = ?)
            OR r.id IN (SELECT report_id FROM user_reports WHERE user_id = ?)
        )
    ''', (report_id, user_id, user_id)).fetchone()
    conn.close()
    return row is not None

def create_report(title, description, department_id, embed_url, icon='bi-bar-chart-line', is_public=0, display_order=0, active=1):
    conn = get_db()
    cursor = conn.cursor()
    report_id = _insert_returning_id(cursor, '''
        INSERT INTO reports (title, description, department_id, embed_url, icon, is_public, display_order, active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title.strip(), description.strip(), int(department_id), embed_url.strip(), icon, int(is_public), int(display_order), int(active)))
    conn.commit()
    conn.close()
    return report_id

def update_report(report_id, title, description, department_id, embed_url, icon='bi-bar-chart-line', is_public=0, display_order=0, active=1):
    conn = get_db()
    conn.execute('''
        UPDATE reports
        SET title = ?, description = ?, department_id = ?, embed_url = ?, icon = ?, is_public = ?, display_order = ?, active = ?
        WHERE id = ?
    ''', (title.strip(), description.strip(), int(department_id), embed_url.strip(), icon, int(is_public), int(display_order), int(active), report_id))
    conn.commit()
    conn.close()

def delete_report(report_id):
    conn = get_db()
    conn.execute('DELETE FROM reports WHERE id = ?', (report_id,))
    conn.commit()
    conn.close()

# ----------------- LOGS & ESTATÍSTICAS ----------------- #

def log_access(user_id, report_id, action, ip_address=''):
    conn = get_db()
    conn.execute('''
        INSERT INTO access_logs (user_id, report_id, action, ip_address)
        VALUES (?, ?, ?, ?)
    ''', (user_id, report_id, action, ip_address))
    conn.commit()
    conn.close()

def get_stats():
    conn = get_db()
    total_users = conn.execute('SELECT COUNT(*) as c FROM users WHERE active = 1').fetchone()['c']
    total_departments = conn.execute('SELECT COUNT(*) as c FROM departments').fetchone()['c']
    total_reports = conn.execute('SELECT COUNT(*) as c FROM reports WHERE active = 1').fetchone()['c']
    total_views = conn.execute("SELECT COUNT(*) as c FROM access_logs WHERE action = 'view_report'").fetchone()['c']
    
    recent_logs = conn.execute('''
        SELECT al.*, u.name as user_name, u.username, r.title as report_title
        FROM access_logs al
        LEFT JOIN users u ON al.user_id = u.id
        LEFT JOIN reports r ON al.report_id = r.id
        ORDER BY al.created_at DESC
        LIMIT 10
    ''').fetchall()
    
    most_viewed = conn.execute('''
        SELECT r.title, d.name as department_name, COUNT(al.id) as views
        FROM reports r
        JOIN departments d ON r.department_id = d.id
        LEFT JOIN access_logs al ON r.id = al.report_id AND al.action = 'view_report'
        GROUP BY r.id, d.name
        ORDER BY views DESC
        LIMIT 5
    ''').fetchall()

    conn.close()
    return {
        'total_users': total_users,
        'total_departments': total_departments,
        'total_reports': total_reports,
        'total_views': total_views,
        'recent_logs': recent_logs,
        'most_viewed': most_viewed
    }


# ----------------- FERRAMENTAS RÁPIDAS & CONFIGURAÇÕES PORTAL ----------------- #

def list_portal_tools(only_active=True):
    conn = get_db()
    if only_active:
        rows = conn.execute("SELECT * FROM portal_tools WHERE is_active = 1 ORDER BY display_order ASC, id ASC").fetchall()
    else:
        rows = conn.execute("SELECT * FROM portal_tools ORDER BY display_order ASC, id ASC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_portal_tool(title, url, icon='bi-link-45deg', custom_svg='', is_active=1, display_order=0):
    conn = get_db()
    c = conn.cursor()
    _insert_returning_id(c, "INSERT INTO portal_tools (title, url, icon, custom_svg, is_active, display_order) VALUES (?, ?, ?, ?, ?, ?)",
                         (title, url, icon, custom_svg, is_active, display_order))
    conn.commit()
    conn.close()

def update_portal_tool(tool_id, title, url, icon='bi-link-45deg', custom_svg='', is_active=1, display_order=0):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE portal_tools SET title = ?, url = ?, icon = ?, custom_svg = ?, is_active = ?, display_order = ? WHERE id = ?",
              (title, url, icon, custom_svg, is_active, display_order, tool_id))
    conn.commit()
    conn.close()

def delete_portal_tool(tool_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM portal_tools WHERE id = ?", (tool_id,))
    conn.commit()
    conn.close()

def get_portal_settings():
    conn = get_db()
    rows = conn.execute("SELECT * FROM portal_settings").fetchall()
    conn.close()
    return {r['key']: r['value'] for r in rows}

def set_portal_setting(key, value, description=''):
    conn = get_db()
    c = conn.cursor()
    if getattr(Config, 'USE_MARIADB', False):
        c.execute("INSERT INTO portal_settings (`key`, value, description, updated_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP) ON DUPLICATE KEY UPDATE value = VALUES(value), updated_at = CURRENT_TIMESTAMP",
                  (key, value, description))
    elif Config.USE_POSTGRES:
        c.execute("INSERT INTO portal_settings (key, value, description, updated_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP",
                  (key, value, description))
    else:
        c.execute("INSERT INTO portal_settings (key, value, description, updated_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP) ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP",
                  (key, value, description))
    conn.commit()
    conn.close()


# ----------------- USABILIDADE & ANALYTICS DE DASHBOARDS ----------------- #

def get_dashboard_usabilidade_analytics(month=None, department_id=None, user_id=None, report_id=None):
    conn = get_db()
    is_mariadb = getattr(Config, 'USE_MARIADB', False)
    
    where_clauses = ["al.action = 'view_report'"]
    params = []
    
    # Filtro por mês
    if month and month not in ('todos', 'all', ''):
        if is_mariadb:
            where_clauses.append("DATE_FORMAT(al.created_at, '%Y-%m') = ?")
        else:
            where_clauses.append("strftime('%Y-%m', al.created_at) = ?")
        params.append(month)
        
    if department_id and str(department_id) not in ('todos', 'all', '0', ''):
        where_clauses.append("r.department_id = ?")
        params.append(int(department_id))
        
    if user_id and str(user_id) not in ('todos', 'all', '0', ''):
        where_clauses.append("al.user_id = ?")
        params.append(int(user_id))
        
    if report_id and str(report_id) not in ('todos', 'all', '0', ''):
        where_clauses.append("al.report_id = ?")
        params.append(int(report_id))
        
    where_sql = " AND ".join(where_clauses)
    
    # 1. Total KPIs
    kpi_sql = f"""
        SELECT 
            COUNT(al.id) as total_views,
            COUNT(DISTINCT al.user_id) as total_users,
            COUNT(DISTINCT al.report_id) as total_reports
        FROM access_logs al
        JOIN reports r ON al.report_id = r.id
        WHERE {where_sql}
    """
    kpi_row = conn.execute(kpi_sql, params).fetchone()
    total_views = kpi_row['total_views'] if kpi_row and kpi_row['total_views'] else 0
    total_users = kpi_row['total_users'] if kpi_row and kpi_row['total_users'] else 0
    accessed_reports = kpi_row['total_reports'] if kpi_row and kpi_row['total_reports'] else 0
    
    total_registered_reports = conn.execute("SELECT COUNT(*) as c FROM reports WHERE active = 1").fetchone()['c'] or 1
    total_registered_users = conn.execute("SELECT COUNT(*) as c FROM users WHERE active = 1").fetchone()['c'] or 1
    adoption_rate = round((accessed_reports / total_registered_reports) * 100, 1) if total_registered_reports else 0
    avg_views_per_user = round(total_views / total_users, 1) if total_users else 0
    
    # Total de Logins no período
    login_where = ["al.action = 'login'"]
    login_params = []
    if month and month not in ('todos', 'all', ''):
        if is_mariadb:
            login_where.append("DATE_FORMAT(al.created_at, '%Y-%m') = ?")
        else:
            login_where.append("strftime('%Y-%m', al.created_at) = ?")
        login_params.append(month)
    if user_id and str(user_id) not in ('todos', 'all', '0', ''):
        login_where.append("al.user_id = ?")
        login_params.append(int(user_id))
    total_logins = conn.execute(f"SELECT COUNT(*) as c FROM access_logs al WHERE {' AND '.join(login_where)}", login_params).fetchone()['c'] or 0

    # 2. Ranking de Dashboards
    dash_sql = f"""
        SELECT r.id, r.title, d.name as dept_name, d.color as dept_color,
               COUNT(al.id) as total_views,
               COUNT(DISTINCT al.user_id) as unique_users,
               MAX(al.created_at) as last_access
        FROM access_logs al
        JOIN reports r ON al.report_id = r.id
        JOIN departments d ON r.department_id = d.id
        WHERE {where_sql}
        GROUP BY r.id, r.title, d.name, d.color
        ORDER BY total_views DESC, r.title ASC
    """
    dashboards = [dict(r) for r in conn.execute(dash_sql, params).fetchall()]
    
    # Acessos por mês para cada dashboard
    month_expr = "DATE_FORMAT(al.created_at, '%Y-%m')" if is_mariadb else "strftime('%Y-%m', al.created_at)"
    dash_monthly_sql = f"""
        SELECT al.report_id, 
               {month_expr} as ym,
               COUNT(al.id) as views
        FROM access_logs al
        JOIN reports r ON al.report_id = r.id
        WHERE {where_sql}
        GROUP BY al.report_id, ym
    """
    dash_monthly_rows = conn.execute(dash_monthly_sql, params).fetchall()
    dash_monthly_map = {}
    for row in dash_monthly_rows:
        rid = row['report_id']
        if rid not in dash_monthly_map:
            dash_monthly_map[rid] = {}
        dash_monthly_map[rid][row['ym']] = row['views']

    for i, d in enumerate(dashboards):
        d['rank'] = i + 1
        d['share_pct'] = round((d['total_views'] / total_views) * 100, 1) if total_views else 0
        d['monthly_views'] = dash_monthly_map.get(d['id'], {})
        if d['last_access']:
            if isinstance(d['last_access'], (datetime.datetime, datetime.date)):
                d['last_access_str'] = d['last_access'].strftime('%d/%m/%Y %H:%M')
                d['last_access'] = d['last_access'].isoformat()
            else:
                d['last_access_str'] = str(d['last_access'])[:16]
                d['last_access'] = str(d['last_access'])
        else:
            d['last_access_str'] = '-'
            d['last_access'] = None

    # 3. Dias da Semana (Segunda a Domingo)
    dow_names = {
        1: 'Domingo',
        2: 'Segunda-feira',
        3: 'Terça-feira',
        4: 'Quarta-feira',
        5: 'Quinta-feira',
        6: 'Sexta-feira',
        7: 'Sábado'
    }
    dow_expr = "DAYOFWEEK(al.created_at)" if is_mariadb else "(CAST(strftime('%w', al.created_at) AS INTEGER) + 1)"
    dow_sql = f"""
        SELECT {dow_expr} as dow, COUNT(al.id) as views
        FROM access_logs al
        JOIN reports r ON al.report_id = r.id
        WHERE {where_sql}
        GROUP BY dow
        ORDER BY dow
    """
    dow_counts = {r['dow']: r['views'] for r in conn.execute(dow_sql, params).fetchall()}
    
    dow_list = []
    peak_dow = None
    max_dow_views = -1
    for dow_num in [2, 3, 4, 5, 6, 7, 1]:  # Seg a Dom
        views = dow_counts.get(dow_num, 0)
        share = round((views / total_views) * 100, 1) if total_views else 0
        item = {
            'dow': dow_num,
            'name': dow_names[dow_num],
            'short_name': dow_names[dow_num][:3],
            'views': views,
            'share': share,
            'is_peak': False
        }
        if views > max_dow_views:
            max_dow_views = views
            peak_dow = item
        dow_list.append(item)
    if peak_dow and max_dow_views > 0:
        peak_dow['is_peak'] = True

    # 4. Evolução Mensal (Janeiro a Dezembro de 2026)
    monthly_sql = f"""
        SELECT {month_expr} as ym, COUNT(al.id) as views
        FROM access_logs al
        JOIN reports r ON al.report_id = r.id
        WHERE {where_sql}
        GROUP BY ym
        ORDER BY ym ASC
    """
    monthly_raw = conn.execute(monthly_sql, params).fetchall()
    monthly_views_dict = {r['ym']: r['views'] for r in monthly_raw}
    
    month_labels_pt = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    evolution_12m = []
    current_year = 2026
    for m in range(1, 13):
        ym_key = f"{current_year}-{m:02d}"
        views = monthly_views_dict.get(ym_key, 0)
        evolution_12m.append({
            'ym': ym_key,
            'month_num': m,
            'label': f"{month_labels_pt[m-1]}/26",
            'views': views
        })

    # 5. Distribuição por Horário e Turno
    hour_expr = "HOUR(al.created_at)" if is_mariadb else "CAST(strftime('%H', al.created_at) AS INTEGER)"
    hour_sql = f"""
        SELECT {hour_expr} as hr, COUNT(al.id) as views
        FROM access_logs al
        JOIN reports r ON al.report_id = r.id
        WHERE {where_sql}
        GROUP BY hr
        ORDER BY hr
    """
    hour_raw = conn.execute(hour_sql, params).fetchall()
    hour_dict = {r['hr']: r['views'] for r in hour_raw}
    hourly_distribution = []
    periods = {
        'Manhã (06h-12h)': 0,
        'Tarde (12h-18h)': 0,
        'Noite (18h-24h)': 0,
        'Madrugada (00h-06h)': 0
    }
    for h in range(24):
        v = hour_dict.get(h, 0)
        hourly_distribution.append({'hour': h, 'label': f"{h:02d}h", 'views': v})
        if 6 <= h < 12:
            periods['Manhã (06h-12h)'] += v
        elif 12 <= h < 18:
            periods['Tarde (12h-18h)'] += v
        elif 18 <= h < 24:
            periods['Noite (18h-24h)'] += v
        else:
            periods['Madrugada (00h-06h)'] += v

    # 6. Distribuição por Departamento
    dept_sql = f"""
        SELECT d.id, d.name, d.color, COUNT(al.id) as views
        FROM access_logs al
        JOIN reports r ON al.report_id = r.id
        JOIN departments d ON r.department_id = d.id
        WHERE {where_sql}
        GROUP BY d.id, d.name, d.color
        ORDER BY views DESC
    """
    dept_shares = [dict(r) for r in conn.execute(dept_sql, params).fetchall()]
    for ds in dept_shares:
        ds['share_pct'] = round((ds['views'] / total_views) * 100, 1) if total_views else 0

    # 7. Ranking de Usuários e Raio-X
    user_sql = f"""
        SELECT u.id, u.username, u.name, d.name as dept_name,
               COUNT(al.id) as total_views,
               COUNT(DISTINCT al.report_id) as distinct_reports,
               MAX(al.created_at) as last_access
        FROM access_logs al
        JOIN reports r ON al.report_id = r.id
        JOIN users u ON al.user_id = u.id
        LEFT JOIN departments d ON u.department_id = d.id
        WHERE {where_sql}
        GROUP BY u.id, u.username, u.name, d.name
        ORDER BY total_views DESC, u.name ASC
    """
    users = [dict(u) for u in conn.execute(user_sql, params).fetchall()]
    
    user_reports_sql = f"""
        SELECT al.user_id, r.id as report_id, r.title as report_title, d.name as dept_name,
               COUNT(al.id) as views,
               MAX(al.created_at) as last_access
        FROM access_logs al
        JOIN reports r ON al.report_id = r.id
        JOIN departments d ON r.department_id = d.id
        WHERE {where_sql}
        GROUP BY al.user_id, r.id, r.title, d.name
        ORDER BY views DESC
    """
    ur_rows = conn.execute(user_reports_sql, params).fetchall()
    user_reports_map = {}
    for row in ur_rows:
        uid = row['user_id']
        if uid not in user_reports_map:
            user_reports_map[uid] = []
        last_acc = row['last_access']
        last_str = last_acc.strftime('%d/%m/%Y %H:%M') if isinstance(last_acc, (datetime.datetime, datetime.date)) else (str(last_acc)[:16] if last_acc else '-')
        user_reports_map[uid].append({
            'report_id': row['report_id'],
            'title': row['report_title'],
            'dept_name': row['dept_name'],
            'views': row['views'],
            'last_access_str': last_str
        })
        
    for i, u in enumerate(users):
        u['rank'] = i + 1
        u['reports'] = user_reports_map.get(u['id'], [])
        u['share_pct'] = round((u['total_views'] / total_views) * 100, 1) if total_views else 0
        if u['last_access']:
            if isinstance(u['last_access'], (datetime.datetime, datetime.date)):
                u['last_access_str'] = u['last_access'].strftime('%d/%m/%Y %H:%M')
                u['last_access'] = u['last_access'].isoformat()
            else:
                u['last_access_str'] = str(u['last_access'])[:16]
                u['last_access'] = str(u['last_access'])
        else:
            u['last_access_str'] = '-'
            u['last_access'] = None

    # 8. Cruzamento Inverso: Para cada Dashboard, quais usuários acessaram
    report_users_sql = f"""
        SELECT al.report_id, u.id as user_id, u.username, u.name as user_name, d.name as user_dept,
               COUNT(al.id) as views,
               MAX(al.created_at) as last_access
        FROM access_logs al
        JOIN reports r ON al.report_id = r.id
        JOIN users u ON al.user_id = u.id
        LEFT JOIN departments d ON u.department_id = d.id
        WHERE {where_sql}
        GROUP BY al.report_id, u.id, u.username, u.name, d.name
        ORDER BY views DESC
    """
    ru_rows = conn.execute(report_users_sql, params).fetchall()
    report_users_map = {}
    for row in ru_rows:
        rid = row['report_id']
        if rid not in report_users_map:
            report_users_map[rid] = []
        last_acc = row['last_access']
        last_str = last_acc.strftime('%d/%m/%Y %H:%M') if isinstance(last_acc, (datetime.datetime, datetime.date)) else (str(last_acc)[:16] if last_acc else '-')
        report_users_map[rid].append({
            'user_id': row['user_id'],
            'username': row['username'],
            'name': row['user_name'],
            'user_dept': row['user_dept'] or 'Geral',
            'views': row['views'],
            'last_access_str': last_str
        })
        
    for d in dashboards:
        d['users_accessed'] = report_users_map.get(d['id'], [])

    # 9. Feed Recente de Auditoria (últimos 20 acessos)
    recent_sql = f"""
        SELECT al.id, al.action, al.ip_address, al.created_at,
               u.id as user_id, u.name as user_name, u.username,
               r.id as report_id, r.title as report_title, d.name as dept_name
        FROM access_logs al
        LEFT JOIN users u ON al.user_id = u.id
        LEFT JOIN reports r ON al.report_id = r.id
        LEFT JOIN departments d ON r.department_id = d.id
        ORDER BY al.created_at DESC
        LIMIT 20
    """
    recent_raw = conn.execute(recent_sql).fetchall()
    recent_feed = []
    for r in recent_raw:
        dt = r['created_at']
        dt_str = dt.strftime('%d/%m/%Y %H:%M:%S') if isinstance(dt, (datetime.datetime, datetime.date)) else (str(dt)[:19] if dt else '')
        recent_feed.append({
            'id': r['id'],
            'action': r['action'],
            'ip_address': r['ip_address'],
            'created_at_str': dt_str,
            'user_name': r['user_name'] or r['username'] or 'Sistema',
            'username': r['username'] or '',
            'report_title': r['report_title'] or ('Login' if r['action'] == 'login' else ('Logout' if r['action'] == 'logout' else r['action'])),
            'dept_name': r['dept_name'] or 'MQ'
        })

    # 10. Listas para filtros dinâmicos
    available_months_sql = f"""
        SELECT DISTINCT {month_expr} as ym
        FROM access_logs al
        WHERE al.action = 'view_report' AND al.created_at IS NOT NULL
        ORDER BY ym DESC
    """
    available_months = [r['ym'] for r in conn.execute(available_months_sql).fetchall() if r['ym']]
    
    all_departments = [dict(r) for r in conn.execute("SELECT id, name, code, color FROM departments ORDER BY name").fetchall()]
    all_users_list = [dict(r) for r in conn.execute("SELECT id, name, username FROM users WHERE active = 1 ORDER BY name").fetchall()]
    all_reports_list = [dict(r) for r in conn.execute("SELECT id, title FROM reports WHERE active = 1 ORDER BY title").fetchall()]

    conn.close()

    return {
        'kpis': {
            'total_views': total_views,
            'total_logins': total_logins,
            'total_users': total_users,
            'total_registered_users': total_registered_users,
            'accessed_reports': accessed_reports,
            'total_registered_reports': total_registered_reports,
            'adoption_rate': adoption_rate,
            'avg_views_per_user': avg_views_per_user,
            'peak_day': peak_dow['name'] if peak_dow else 'Quinta-feira',
            'peak_day_views': peak_dow['views'] if peak_dow else 0,
            'peak_day_share': peak_dow['share'] if peak_dow else 0,
            'top_dashboard': dashboards[0]['title'] if dashboards else 'N/A',
            'top_dashboard_views': dashboards[0]['total_views'] if dashboards else 0
        },
        'ranking_dashboards': dashboards,
        'ranking_users': users,
        'days_of_week': dow_list,
        'evolution_12m': evolution_12m,
        'hourly_distribution': hourly_distribution,
        'periods_distribution': [{'period': k, 'views': v} for k, v in periods.items()],
        'dept_shares': dept_shares,
        'recent_feed': recent_feed,
        'filters_meta': {
            'current_month': month or 'todos',
            'current_department': department_id or 'todos',
            'current_user': user_id or 'todos',
            'available_months': available_months,
            'departments': all_departments,
            'users': all_users_list,
            'reports': all_reports_list
        }
    }
