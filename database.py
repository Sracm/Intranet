import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

def get_db():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
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
        cursor.execute('''
            INSERT INTO users (username, name, email, password_hash, role, department_id, active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        ''', (username.strip().lower(), name.strip(), email.strip() if email else '', pwd_hash, role, department_id))
        user_id = cursor.lastrowid

        # Atribuir departamento principal também em user_departments
        dept_ids_to_add = set()
        if department_id:
            dept_ids_to_add.add(int(department_id))
        if extra_dept_ids:
            for d in extra_dept_ids:
                dept_ids_to_add.add(int(d))

        for d_id in dept_ids_to_add:
            cursor.execute('INSERT OR IGNORE INTO user_departments (user_id, department_id) VALUES (?, ?)', (user_id, d_id))

        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
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
        cursor.execute('INSERT OR IGNORE INTO user_departments (user_id, department_id) VALUES (?, ?)', (user_id, d_id))

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
    users = conn.execute('''
        SELECT u.*, d.name as department_name,
               (SELECT GROUP_CONCAT(d2.name, ', ') 
                FROM user_departments ud 
                JOIN departments d2 ON ud.department_id = d2.id 
                WHERE ud.user_id = u.id) as all_departments
        FROM users u
        LEFT JOIN departments d ON u.department_id = d.id
        ORDER BY u.role DESC, u.name ASC
    ''').fetchall()
    conn.close()
    return users

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
    return departments

def get_department_by_id(dept_id):
    conn = get_db()
    dept = conn.execute('SELECT * FROM departments WHERE id = ?', (dept_id,)).fetchone()
    conn.close()
    return dept

def create_department(name, code, description='', icon='bi-folder', color='#CB9727'):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO departments (name, code, description, icon, color)
            VALUES (?, ?, ?, ?, ?)
        ''', (name.strip(), code.strip().lower(), description.strip(), icon, color))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
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
    return reports

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
        depts = conn.execute('''
            SELECT DISTINCT d.* 
            FROM departments d
            JOIN reports r ON r.department_id = d.id AND r.active = 1
            ORDER BY d.name ASC
        ''').fetchall()
    else:
        depts = conn.execute('''
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
    cursor.execute('''
        INSERT INTO reports (title, description, department_id, embed_url, icon, is_public, display_order, active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title.strip(), description.strip(), int(department_id), embed_url.strip(), icon, int(is_public), int(display_order), int(active)))
    report_id = cursor.lastrowid
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
        GROUP BY r.id
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
