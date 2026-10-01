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
        conn = pymysql.connect(
            host=Config.MARIADB_HOST,
            user=Config.MARIADB_USER,
            password=Config.MARIADB_PASSWORD,
            database=Config.MARIADB_DB,
            port=Config.MARIADB_PORT,
            cursorclass=pymysql.cursors.DictCursor
        )
        return _MariaDBConnection(conn)
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
        conn = pymysql.connect(
            host=Config.MARIADB_HOST,
            user=Config.MARIADB_USER,
            password=Config.MARIADB_PASSWORD,
            database=Config.MARIADB_DB,
            port=Config.MARIADB_PORT,
            autocommit=True
        )
        with conn.cursor() as cursor:
            # pymysql requires splitting multiple statements or executing one by one
            for statement in _SCHEMA_MARIADB.split(';'):
                if statement.strip():
                    cursor.execute(statement)
        conn.close()
        return

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
        
    conn.close()
    return reports

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
