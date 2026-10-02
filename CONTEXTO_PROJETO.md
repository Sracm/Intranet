# Contexto e Histórico do Projeto - Intranet & Migração MariaDB

Data de Registro: 02/10/2026

---

## 1. O que foi feito nesta sessão

### 1.1 Validação do Banco MariaDB
- **Host / IP**: `192.168.1.22`
- **Porta**: `3306`
- **Usuário**: `antonio`
- **Banco**: `intranet`
- Conexão testada e validada com sucesso utilizando `pymysql`.

### 1.2 Migração de Dados (SQLite ➔ MariaDB)
- Criado o script `migrate_db.py`.
- Todas as tabelas e esquemas foram convertidos do SQLite (`intranet.db`) para o MariaDB `192.168.1.22`.
- Migração completa de dados sem perda de integridade (usuários, permissões, relatórios, logs, configurações, etc.).
- Tratamento de constraints e integridade referencial com `FOREIGN_KEY_CHECKS=0` e limpeza com `DELETE FROM`.

### 1.3 Atualização da Aplicação
- **`config.py`**: Atualizado para carregar configurações de banco via variáveis de ambiente com `python-dotenv` (`DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`), mantendo fallback seguro.
- **`.env`**: Configurado com as credenciais do MariaDB (protegido no `.gitignore`).
- **`.env.example`**: Atualizado com os modelos de variáveis necessárias para deploy.
- **`database.py`**:
  - Migrado de `sqlite3` para `pymysql`.
  - Criada a classe adaptadora `_MariaDBCursor` para converter parâmetros de queries de `?` (SQLite) para `%s` (MySQL/MariaDB), preservando retrocompatibilidade total com as dezenas de consultas do sistema.
- **`requirements.txt`**: Adicionados `pymysql`, `cryptography` e `python-dotenv`.

### 1.4 Correção de Bug em Produção
- **Problema**: `ProgrammingError (1064, ... near 'key, value FROM portal_settings')`.
- **Causa**: `key` é palavra reservada no MariaDB / MySQL.
- **Solução**: Ajustada a consulta no `database.py` para não usar `key` diretamente de forma não escapada (`SELECT * FROM portal_settings`).

### 1.5 Regras e Governança
- **Regra criada em `.agents/rules/requirements.md`**: Sempre que qualquer nova biblioteca ou pacote for adicionado ao projeto, deve ser obrigatoriamente registrado no `requirements.txt`.

### 1.6 Versionamento (Git & GitHub)
Todos os commits foram enviados para o branch `main`:
1. `e23d42b`: Migração de conexão SQLite para MariaDB e leitura via .env
2. `0a56a68`: ajuste no run
3. `2fa2fcb`: requi (dependências pymysql, python-dotenv)
4. `661826b`: Fix syntax error on portal_settings reserved keyword

---

## 2. Próximos Passos ao Abrir o Projeto

1. **No servidor Linux (onde roda a Intranet em produção)**:
   ```bash
   cd /home/antonio/Intranet
   git pull
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Reiniciar o serviço da Intranet** (ou script `run.sh` / systemd / gunicorn / supervisor).
3. **Validar no navegador**: Acessar o portal e confirmar que as configurações e telas carregam normalmente.
4. **Outros Dashboards**:
   - Verificar se o projeto `DASHBOARD_tv` ou outros dashboards integrados necessitam de ajustes de apontamento ou conexão.
