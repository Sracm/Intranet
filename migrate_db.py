import sqlite3
import pymysql

# SQLite connection
sqlite_db = r"c:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\ANTIGRAVITY\PROJETOS\INTRANET\intranet.db"
sqlite_conn = sqlite3.connect(sqlite_db)
sqlite_conn.row_factory = sqlite3.Row
sqlite_cursor = sqlite_conn.cursor()

# MariaDB connection
mariadb_conn = pymysql.connect(
    host='192.168.1.22',
    user='antonio',
    password='yzmpq100',
    port=3306,
    autocommit=True
)
mariadb_cursor = mariadb_conn.cursor()

# Create database
mariadb_cursor.execute("CREATE DATABASE IF NOT EXISTS intranet CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
mariadb_cursor.execute("USE intranet;")

# Create tables
mariadb_cursor.execute("SET FOREIGN_KEY_CHECKS=0;")

tables_schema = [
    """
    CREATE TABLE IF NOT EXISTS departments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        code VARCHAR(255) UNIQUE NOT NULL,
        description TEXT,
        icon VARCHAR(255) DEFAULT 'bi-folder',
        color VARCHAR(255) DEFAULT '#CB9727',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
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
    """,
    """
    CREATE TABLE IF NOT EXISTS user_departments (
        user_id INT NOT NULL,
        department_id INT NOT NULL,
        PRIMARY KEY (user_id, department_id),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (department_id) REFERENCES departments (id) ON DELETE CASCADE
    );
    """,
    """
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
    """,
    """
    CREATE TABLE IF NOT EXISTS user_reports (
        user_id INT NOT NULL,
        report_id INT NOT NULL,
        PRIMARY KEY (user_id, report_id),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
        FOREIGN KEY (report_id) REFERENCES reports (id) ON DELETE CASCADE
    );
    """,
    """
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
    """,
    """
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
    """,
    """
    CREATE TABLE IF NOT EXISTS portal_settings (
        `key` VARCHAR(255) PRIMARY KEY,
        value TEXT,
        description TEXT,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """
]

for stmt in tables_schema:
    mariadb_cursor.execute(stmt)

mariadb_cursor.execute("SET FOREIGN_KEY_CHECKS=1;")

def migrate_table(table_name):
    # check if sqlite table exists
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    if not sqlite_cursor.fetchone():
        print(f"Table {table_name} does not exist in SQLite, skipping.")
        return

    print(f"Migrating table {table_name}...")
    mariadb_cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
    mariadb_cursor.execute(f"DELETE FROM {table_name};")
    
    
    sqlite_cursor.execute(f"SELECT * FROM {table_name}")
    rows = sqlite_cursor.fetchall()
    
    if not rows:
        print(f"No data in {table_name}.")
        return

    col_names = rows[0].keys()
    
    # Handle the 'key' column name quoting in MariaDB
    escaped_col_names = [f"`{col}`" if col == 'key' else col for col in col_names]
    
    placeholders = ", ".join(["%s"] * len(col_names))
    cols = ", ".join(escaped_col_names)
    
    insert_sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
    
    data = []
    for row in rows:
        data.append(tuple(row[col] for col in col_names))
        
    mariadb_cursor.executemany(insert_sql, data)
    print(f"Inserted {len(rows)} rows into {table_name}.")
    mariadb_cursor.execute("SET FOREIGN_KEY_CHECKS=1;")

tables = ["departments", "users", "user_departments", "reports", "user_reports", "access_logs", "portal_tools", "portal_settings"]
for t in tables:
    migrate_table(t)

print("Migration completed.")
sqlite_conn.close()
mariadb_conn.close()
