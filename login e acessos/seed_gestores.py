"""
Script de Carga e Sincronização dos Gestores e Centros de Custo
Executa na Intranet (lendo config.py / .env do MariaDB oficial).
"""
import os, sys, json
from werkzeug.security import generate_password_hash

# Garante que importa database e config da Intranet
intranet_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, intranet_root)

from config import Config
from database import get_db

JSON_PATH = os.path.join(os.path.dirname(__file__), "gestores_centros_custo.json")

def sincronizar_gestores(senha_padrao="MQ@gestor2026"):
    print(f"[*] Conectando ao banco da Intranet (MariaDB: {getattr(Config, 'MARIADB_HOST', 'Local')})...")
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Garante que a tabela user_cost_centers existe
    if getattr(Config, 'USE_MARIADB', False):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_cost_centers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                codcencus INT NOT NULL,
                descricao_centro VARCHAR(255),
                canal VARCHAR(100),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uq_user_cc (user_id, codcencus),
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_cost_centers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                codcencus INTEGER NOT NULL,
                descricao_centro TEXT,
                canal TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (user_id, codcencus),
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)
    conn.commit()
    print("[+] Tabela user_cost_centers pronta!")

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        gestores = json.load(f)

    # Senha hash provisória
    pwd_hash = generate_password_hash(senha_padrao)

    for g in gestores:
        username = g["gestor"].lower().strip()
        nome = g["nome_completo"]
        canal = g["canal"]

        # Verifica se usuário já existe (usar placeholder '?' que o adapter converte para %s)
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_row = cursor.fetchone()
        
        if user_row:
            user_id = user_row["id"] if isinstance(user_row, dict) else user_row[0]
            print(f"  [i] Usuário existente: {username} (ID {user_id})")
        else:
            # Insere usuário novo
            insert_user_sql = """
                INSERT INTO users (username, name, email, password_hash, role, active)
                VALUES (?, ?, ?, ?, 'gestor', 1)
            """
            cursor.execute(insert_user_sql, (username, nome, f"{username}@mqhair.com.br", pwd_hash))
            user_id = cursor.lastrowid
            print(f"  [+] Novo usuário criado: {username} (ID {user_id})")

        # Insere / atualiza os centros de custo
        for cc in g["centros_de_custo"]:
            cod = cc["codigo"]
            desc = cc["descricao"]
            
            if getattr(Config, 'USE_MARIADB', False):
                # No MariaDB
                cursor.execute("""
                    INSERT INTO user_cost_centers (user_id, codcencus, descricao_centro, canal)
                    VALUES (?, ?, ?, ?)
                    ON DUPLICATE KEY UPDATE descricao_centro = VALUES(descricao_centro), canal = VALUES(canal)
                """, (user_id, cod, desc, canal))
            else:
                cursor.execute("""
                    INSERT OR REPLACE INTO user_cost_centers (user_id, codcencus, descricao_centro, canal)
                    VALUES (?, ?, ?, ?)
                """, (user_id, cod, desc, canal))

    conn.commit()
    conn.close()
    print("\n[OK] Todos os 9 gestores e centros de custo foram sincronizados com sucesso no banco!")

if __name__ == "__main__":
    sincronizar_gestores()
