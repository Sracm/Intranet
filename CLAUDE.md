# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Comandos

```cmd
run.bat                  :: inicializa o schema e sobe o servidor (uso normal)
python app.py            :: sobe o servidor em http://localhost:5080
python seed.py           :: popula departamentos/usuários/relatórios padrão (no-op se já houver usuários)
python update_reports.py :: script pontual (só SQLite): reescreve os 4 relatórios de Logística
python migrate_to_postgres.py [--reset] :: copia intranet.db -> PostgreSQL (lê DATABASE_URL do ambiente ou .env)
pip install -r requirements.txt
```

Deploy: Vercel (`vercel.json` + `api/index.py`) com Neon PostgreSQL, auto-deploy no push para `main`.
Passos operacionais em `PASSOS_MANUAIS.md`; plano original em `plano.md`.

Variáveis de ambiente: `DATABASE_URL` (se definida, usa PostgreSQL; senão SQLite em `SQLITE_PATH`
ou `intranet.db`), `FLASK_ENV=production` (desliga DEBUG, liga cookie Secure e `ProxyFix`),
`SECRET_KEY` (obrigatória em produção — `config.py` levanta erro se estiver com o valor padrão).

Não há suíte de testes, linter ou build. A validação é manual: subir o app e navegar
(`admin/admin` para o painel administrativo; `logistica/123` e `comercial/123` para testar
o recorte de permissões).

`init_db()` roda automaticamente no import de `app.py` e só usa `CREATE TABLE IF NOT EXISTS` —
**não há migrações**. Mudar uma coluna exige ALTER manual no `intranet.db` ou apagar o arquivo
e rodar `seed.py` de novo. `intranet.db` está no `.gitignore`.

## Arquitetura

Flask monolítico, sem blueprints e sem ORM, em 3 arquivos:

- `config.py` — `Config` (SECRET_KEY, caminho do SQLite, HOST `0.0.0.0`, PORT 5080, DEBUG).
- `database.py` — schema + **toda** a camada de dados. Cada função abre e fecha sua própria
  conexão via `get_db()`. Nenhum SQL deve ser escrito fora deste arquivo; rotas novas chamam ou
  adicionam funções aqui. **Dois backends com o mesmo código:** em PostgreSQL, `get_db()` devolve
  um wrapper (`_PgConnection`) que aceita placeholders `?` e retorna linhas como dict. SQL novo
  precisa rodar nos dois: use `_insert_returning_id()` em vez de `cursor.lastrowid`,
  `ON CONFLICT DO NOTHING` em vez de `INSERT OR IGNORE`, capture `IntegrityError` do módulo (não
  `sqlite3.IntegrityError`), inclua no `GROUP BY` toda coluna não agregada, e mantenha
  `_SCHEMA_POSTGRES` sincronizado com o schema SQLite de `init_db()`.
- `app.py` — rotas e regras de apresentação. Views administrativas são POST-por-`action`
  (`create` / `edit` / `delete` no mesmo endpoint), sempre terminando em `flash()` + redirect.

Tabelas: `departments`, `users`, `user_departments` (N:N), `reports`, `user_reports` (N:N,
exceções por usuário), `access_logs`. `DER.excalidraw` tem o diagrama.

### Modelo de permissão (núcleo do projeto)

Um usuário enxerga um relatório ativo se **qualquer** das condições valer:
`reports.is_public = 1`, ou o departamento do relatório estar em `user_departments`, ou o
relatório estar em `user_reports`. Admin (`session['role'] == 'admin'`) vê tudo.

Esse mesmo OR está replicado em três funções de `database.py` — `get_reports_for_user`,
`get_user_accessible_departments` e `user_can_access_report`. Ao mudar a regra, mude nas três,
senão a grade e a tela de visualização divergem.

`users.department_id` é só o departamento "principal" para exibição; a autorização real vem de
`user_departments`. `create_user`/`update_user` sempre reinserem o principal lá dentro.

Guardas: decorators `@login_required` / `@admin_required` em `app.py`. `view_report` checa
`user_can_access_report` antes de renderizar — nunca renderize um embed sem essa checagem.

### Detalhes com pegadinha

- `resolve_embed_url` (`app.py`) reescreve `localhost`/`127.0.0.1` nas embed URLs para o host da
  requisição, para que dashboards internos hospedados em outra porta (ex.: `:5100`) funcionem
  quando alguém acessa o portal pelo IP da rede. Exposto aos templates como `resolve_url`.
- `portal()` promove a banner um relatório "em destaque" usando um match frágil:
  `r['id'] == 5 or 'Cockpit Geral' in r['title']`.
- Logs: `log_access(user_id, report_id, action, ip)` grava `login`, `logout` e `view_report`;
  `get_stats()` alimenta o dashboard admin.

## Frontend

Jinja2 + CSS puro, sem build e sem framework JS. `templates/base.html` é o layout;
`static/css/mq_theme.css` define os tokens do MQ Design System — use as variáveis
(`--mq-gold #CB9727`, `--mq-black-bg #121212`, `--mq-creme-2 #EDE4DA`, gradientes `--mq-grad-*`)
em vez de cores literais. Tipografia Montserrat e ícones Bootstrap Icons vêm por `@import` de CDN.
Campos `icon` em departamentos/relatórios guardam classes Bootstrap Icons (`bi-truck`, ...) e
`color` guarda hex usado direto no CSS inline dos cards.

A UI e todos os textos são em **português (pt-BR)** — mensagens de `flash`, labels e comentários
devem seguir o mesmo idioma.
