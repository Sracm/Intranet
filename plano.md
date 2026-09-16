# Plano de Deploy — Intranet MQ
## Vercel (Flask Serverless) + Neon PostgreSQL + GitHub

> **Data:** 2026-09-14
> **Backup de segurança:** tag ``backup-pre-deploy-v1`` (commit ``33573eb``)
> **Status:** Aguardando execução

---

## Visão Geral da Arquitetura em Produção

```
Desenvolvedor (local)
    │
    │  git push
    ▼
GitHub (branch: main)
    │
    │  auto-deploy (webhook)
    ▼
Vercel — Flask Serverless
    │  entrypoint: api/index.py
    │
    │  DATABASE_URL (env var)
    ▼
Neon PostgreSQL (cloud, free tier)
    └── banco: intranet_prod
```

**Fluxo de desenvolvimento:**
- Localmente → usa ``intranet.db`` (SQLite, sem mudanças)
- Em produção → usa Neon PostgreSQL via ``DATABASE_URL``

---

## Fase 1 — Adaptação do Código

### 1.1 Modificar ``config.py``

**Objetivo:** suporte a PostgreSQL via variável de ambiente, mantendo SQLite como fallback local.

```python
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = os.environ.get(''SECRET_KEY'', ''mq-professional-intranet-secure-token-2026'')
    DATABASE_URL = os.environ.get(''DATABASE_URL'', '''')  # PostgreSQL em produção
    DATABASE = os.path.join(BASE_DIR, ''intranet.db'')     # SQLite em dev local
    HOST = ''0.0.0.0''
    PORT = int(os.environ.get(''PORT'', 5080))
    DEBUG = os.environ.get(''FLASK_ENV'', ''development'') != ''production''
    USE_POSTGRES = bool(DATABASE_URL)
```

---

### 1.2 Modificar ``database.py``

**Objetivo:** detectar automaticamente SQLite (dev) vs PostgreSQL (prod) e adaptar queries.

Principais mudanças:
- Função ``get_db()`` retorna conexão SQLite ou psycopg2 conforme ambiente
- Placeholders: ``?`` (SQLite) → ``%s`` (PostgreSQL) em todas as queries
- ``CREATE TABLE``: ``AUTOINCREMENT`` → ``SERIAL`` no PostgreSQL
- Tratamento de exceções: ``sqlite3.IntegrityError`` → ``psycopg2.errors.UniqueViolation``
- ``conn.row_factory = sqlite3.Row`` → cursor com ``RealDictCursor`` no psycopg2

---

### 1.3 Criar ``api/index.py`` — OBRIGATÓRIO para Vercel

**Objetivo:** entrypoint WSGI que a Vercel usa para invocar o Flask.

```python
# api/index.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app

# Handler que a Vercel chama
handler = app
```

> ATENÇÃO: Este arquivo é OBRIGATÓRIO. Sem ele, a Vercel não sabe como iniciar o Flask.

---

### 1.4 Criar ``vercel.json`` — OBRIGATÓRIO para Vercel

**Objetivo:** configurar o runtime Python e roteamento de todas as requisições.

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

---

### 1.5 Modificar ``requirements.txt``

```txt
Flask>=2.3.0,<3.0.0
Werkzeug>=2.3.0,<3.0.0
psycopg2-binary>=2.9.9
```

---

### 1.6 Modificar ``.gitignore``

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
.venv/

# Banco local (NUNCA subir para o GitHub)
*.db
intranet.db

# Variáveis de ambiente (segredos)
.env
.env.local

# Vercel
.vercel/
```

---

### 1.7 Criar ``.env.example``

```env
# Chave secreta do Flask
SECRET_KEY=sua-chave-secreta-aqui

# URL de conexão do banco PostgreSQL (Neon)
DATABASE_URL=postgresql://usuario:senha@ep-xxxx.neon.tech/intranet_prod?sslmode=require

# Ambiente
FLASK_ENV=production
```

---

### 1.8 Criar ``migrate_to_postgres.py``

Script utilitário para exportar dados do ``intranet.db`` local e importar no Neon PostgreSQL.
Executado UMA ÚNICA VEZ após configurar o banco Neon.

```bash
python migrate_to_postgres.py
```

O script:
1. Lê todas as tabelas do SQLite local (intranet.db)
2. Cria as tabelas no PostgreSQL (adaptando sintaxe)
3. Insere todos os registros existentes
4. Confirma contagem de registros migrados

---

## Fase 2 — Configurar Neon PostgreSQL

Passo a passo manual:

1. Criar conta em https://neon.tech (gratuito, sem cartão)
2. Criar projeto → nome: ``intranet-mq``
3. Criar banco → nome: ``intranet_prod``
4. Copiar a ``DATABASE_URL`` (formato abaixo):
   postgresql://usuario:senha@ep-xxxx.us-east-2.aws.neon.tech/intranet_prod?sslmode=require
5. Criar arquivo ``.env`` local (NÃO subir para o GitHub):
   DATABASE_URL=postgresql://... (URL copiada do Neon)
   SECRET_KEY=mq-intranet-prod-2026-chave-segura
   FLASK_ENV=production
6. Executar a migração localmente:
   python migrate_to_postgres.py
7. Verificar os dados no Neon Dashboard (Tables → verificar registros)

---

## Fase 3 — Deploy na Vercel

Passo a passo manual:

1. Push do código para o GitHub:
   git add -A
   git commit -m "feat: adaptar para deploy Vercel + Neon PostgreSQL"
   git push origin main

2. Acessar https://vercel.com → fazer login com GitHub

3. Importar repositório:
   - Clicar em "Add New Project"
   - Selecionar o repositório INTRANET
   - Framework Preset: Other (não é Next.js nem Vite)

4. Configurar variáveis de ambiente na Vercel:
   SECRET_KEY  → Chave segura gerada para produção
   DATABASE_URL → URL completa do Neon PostgreSQL
   FLASK_ENV    → production

5. Clicar em Deploy
   A Vercel vai detectar o vercel.json, instalar requirements.txt
   e publicar em https://intranet-mq.vercel.app

6. (Opcional) Configurar domínio personalizado:
   Project Settings → Domains → adicionar domínio próprio

---

## Fase 4 — Pós-Deploy

### 4.1 Atualizar URLs dos dashboards internos

Acessar o painel admin (/admin/reports) e atualizar as URLs dos relatórios DRE:

| Relatório        | URL atual                        | Ação                                        |
|------------------|----------------------------------|---------------------------------------------|
| DRE Regional FSP | http://localhost:5100/regional.fsp | Atualizar para IP/domínio público do DRE   |
| DRE RH           | http://localhost:5100/rh          | Atualizar para IP/domínio público do DRE   |

### 4.2 Checklist de Verificação

[ ] Login funciona em produção (usuário ``admin``)
[ ] Admin consegue criar/editar/excluir usuários
[ ] Admin consegue criar/editar/excluir relatórios
[ ] Filtro por departamento funciona no portal
[ ] Power BI embeds carregam corretamente
[ ] Logs de acesso são registrados no Neon
[ ] Sessões persistem após navegação
[ ] URLs dos dashboards DRE atualizadas para endereço público
[ ] Deploy automático funciona após um ``git push``

---

## Como Reverter (se necessário)

O backup foi salvo antes de qualquer alteração. Para voltar:

```bash
# Ver o estado do backup sem alterar nada
git checkout backup-pre-deploy-v1

# Reverter completamente para o estado de backup
git reset --hard backup-pre-deploy-v1
```

---

## Referências

- Vercel Python Runtime: https://vercel.com/docs/functions/runtimes/python
- Neon PostgreSQL Quickstart: https://neon.tech/docs/get-started-with-neon/signing-up
- psycopg2 Documentation: https://www.psycopg.org/docs/
- Flask Deployment Options: https://flask.palletsprojects.com/en/3.0.x/deploying/
