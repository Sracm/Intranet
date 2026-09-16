"""
Migra os dados do intranet.db (SQLite local) para o PostgreSQL (Neon).

Uso:
    python migrate_to_postgres.py            # aborta se o PostgreSQL já tiver usuários
    python migrate_to_postgres.py --reset    # APAGA as tabelas do PostgreSQL e migra de novo

Lê DATABASE_URL do ambiente ou do arquivo .env na raiz do projeto.
"""
import os
import sqlite3
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ordem respeita as chaves estrangeiras
TABLES = ['departments', 'users', 'user_departments', 'reports', 'user_reports', 'access_logs']
TABLES_WITH_SERIAL = ['departments', 'users', 'reports', 'access_logs']


def load_env_file():
    env_path = os.path.join(BASE_DIR, '.env')
    if not os.path.exists(env_path):
        return
    with open(env_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def read_sqlite(sqlite_path):
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    data = {t: [dict(r) for r in conn.execute(f'SELECT * FROM {t}').fetchall()] for t in TABLES}
    conn.close()
    return data


def drop_orphans(data):
    """O SQLite só aplica FKs com PRAGMA ligado; o PostgreSQL rejeita referências órfãs."""
    ids = {t: {r['id'] for r in data[t]} for t in TABLES_WITH_SERIAL}
    fixes = 0

    for u in data['users']:
        if u['department_id'] is not None and u['department_id'] not in ids['departments']:
            u['department_id'] = None
            fixes += 1

    before = len(data['reports'])
    data['reports'] = [r for r in data['reports'] if r['department_id'] in ids['departments']]
    fixes += before - len(data['reports'])
    ids['reports'] = {r['id'] for r in data['reports']}

    for table, ref_table, ref_col in [('user_departments', 'departments', 'department_id'),
                                      ('user_reports', 'reports', 'report_id')]:
        before = len(data[table])
        data[table] = [r for r in data[table]
                       if r['user_id'] in ids['users'] and r[ref_col] in ids[ref_table]]
        fixes += before - len(data[table])

    for log in data['access_logs']:
        if log['user_id'] is not None and log['user_id'] not in ids['users']:
            log['user_id'] = None
            fixes += 1
        if log['report_id'] is not None and log['report_id'] not in ids['reports']:
            log['report_id'] = None
            fixes += 1

    return fixes


def main():
    load_env_file()
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        sys.exit('ERRO: DATABASE_URL não definida (nem no ambiente, nem no .env).')

    sqlite_path = os.environ.get('SQLITE_PATH', os.path.join(BASE_DIR, 'intranet.db'))
    if not os.path.exists(sqlite_path):
        sys.exit(f'ERRO: banco SQLite não encontrado em {sqlite_path}')

    import psycopg2
    import database  # com DATABASE_URL definida, init_db() cria o schema PostgreSQL

    print(f'Lendo SQLite: {sqlite_path}')
    data = read_sqlite(sqlite_path)
    fixes = drop_orphans(data)
    if fixes:
        print(f'Aviso: {fixes} referência(s) órfã(s) corrigida(s)/descartada(s) antes da migração.')

    conn = psycopg2.connect(database_url)
    cur = conn.cursor()

    if '--reset' in sys.argv:
        print('--reset: removendo tabelas existentes no PostgreSQL...')
        cur.execute('DROP TABLE IF EXISTS ' + ', '.join(reversed(TABLES)) + ' CASCADE')
        conn.commit()

    database.init_db()

    cur.execute('SELECT COUNT(*) FROM users')
    if cur.fetchone()[0] > 0:
        conn.close()
        sys.exit('ERRO: o PostgreSQL já possui usuários. Use --reset para sobrescrever (apaga os dados de lá).')

    try:
        for table in TABLES:
            rows = data[table]
            if not rows:
                print(f' -> {table}: 0 registros')
                continue
            cols = list(rows[0].keys())
            sql = f'INSERT INTO {table} ({", ".join(cols)}) VALUES ({", ".join(["%s"] * len(cols))})'
            cur.executemany(sql, [tuple(r[c] for c in cols) for r in rows])
            print(f' -> {table}: {len(rows)} registros')

        # Os ids foram inseridos explicitamente: ajusta as sequences para o próximo INSERT
        for table in TABLES_WITH_SERIAL:
            cur.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                        f"COALESCE((SELECT MAX(id) FROM {table}), 0) + 1, false)")

        conn.commit()
    except Exception:
        conn.rollback()
        conn.close()
        raise

    print('\nConferência de contagens (SQLite -> PostgreSQL):')
    ok = True
    for table in TABLES:
        cur.execute(f'SELECT COUNT(*) FROM {table}')
        pg_count = cur.fetchone()[0]
        status = 'OK' if pg_count == len(data[table]) else 'DIVERGENTE'
        ok = ok and status == 'OK'
        print(f' {status:>10}  {table}: {len(data[table])} -> {pg_count}')

    conn.close()
    print('\nMigração concluída com sucesso!' if ok else '\nMigração concluída com divergências — verifique acima.')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
