# Passos Manuais — Deploy da Intranet MQ (Vercel + Neon)

> O código já foi adaptado e auditado (Fase 1 do `plano.md`).
> Este guia lista **apenas o que precisa ser feito por você**, na ordem.
> Backup do estado anterior: tag `backup-pre-deploy-v1`.

---

## Etapa 1 — Revisar e publicar o código no GitHub

1. Revise as alterações:
   ```bash
   git status
   git diff
   ```
2. Confirme que o `intranet.db` aparece como **removido do índice** (`D intranet.db`).
   O arquivo local continua existindo — ele só deixa de ser versionado.
3. Faça o commit e o push:
   ```bash
   git add -A
   git commit -m "feat: adaptar para deploy Vercel + Neon PostgreSQL"
   git push origin main
   ```
4. **Atenção:** o `intranet.db` (com hashes de senha) continua no *histórico* do git.
   O repositório `Sracm/Intranet` é **privado**, então o risco é baixo. Mantenha-o privado.
   Se um dia ele for tornado público, será preciso limpar o histórico
   (ex.: `git filter-repo --path intranet.db --invert-paths`) e trocar todas as senhas.

---

## Etapa 2 — Criar o banco no Neon

1. Acesse https://neon.tech e crie uma conta (gratuito).
2. Crie um projeto chamado `intranet-mq`.
   - **Região:** escolha a mesma região em que a função da Vercel vai rodar
     (ex.: `AWS us-east-1` ↔ Vercel `iad1`). Regiões diferentes deixam cada página lenta.
3. Crie o banco `intranet_prod`.
4. Em **Connection Details**, marque a opção **Pooled connection** e copie a URL.
   Ela tem `-pooler` no host, por exemplo:
   ```
   postgresql://usuario:senha@ep-xxxx-pooler.us-east-1.aws.neon.tech/intranet_prod?sslmode=require
   ```
   > O app abre uma conexão por consulta; o endpoint *pooler* evita esgotar conexões no ambiente serverless.

---

## Etapa 3 — Migrar os dados locais para o Neon

1. Gere uma chave secreta forte e **guarde-a** (vai usar de novo na Vercel):
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
2. Copie `.env.example` para `.env` e preencha:
   ```env
   SECRET_KEY=<chave gerada no passo 1>
   DATABASE_URL=<URL pooled do Neon>
   FLASK_ENV=production
   ```
   > O `.env` está no `.gitignore` — **nunca** faça commit dele.
3. Instale as dependências (inclui o `psycopg2-binary`):
   ```bash
   pip install -r requirements.txt
   ```
4. Execute a migração **uma única vez**:
   ```bash
   python migrate_to_postgres.py
   ```
5. Confira no final da saída que todas as tabelas aparecem como `OK`.
   - Se precisar refazer do zero: `python migrate_to_postgres.py --reset` (**apaga** os dados do Neon).
6. (Opcional) No painel do Neon, abra **Tables** e confira os registros.

---

## Etapa 4 — Deploy na Vercel

1. Acesse https://vercel.com e entre com a conta do GitHub.
2. Clique em **Add New → Project** e selecione o repositório `Intranet`.
3. Em **Framework Preset**, escolha **Other**.
4. Em **Environment Variables**, cadastre (ambiente *Production*):

   | Variável       | Valor                                   |
   |----------------|-----------------------------------------|
   | `SECRET_KEY`   | a mesma chave gerada na Etapa 3         |
   | `DATABASE_URL` | a URL *pooled* do Neon                  |
   | `FLASK_ENV`    | `production`                            |

   > Sem `SECRET_KEY`, o app **se recusa a iniciar** em produção (proteção intencional).
5. Clique em **Deploy** e aguarde a URL (ex.: `https://intranet-mq.vercel.app`).
6. Em **Project Settings → Functions**, confirme que a região da função é a mesma do Neon.
7. (Opcional) Em **Project Settings → Domains**, adicione um domínio próprio.

---

## Etapa 5 — Segurança pós-deploy (obrigatório)

1. Entre em produção com `admin` e **troque a senha** em *Meu Perfil*.
2. Em **Administração → Usuários**, redefina as senhas dos usuários de demonstração
   (`logistica`, `comercial`, `ricardo.pavao`, `maria.macedo` — todas `123`)
   ou desative os que não forem usados.

---

## Etapa 6 — Atualizar URLs dos dashboards internos

Os relatórios DRE apontam para um servidor local que não existe na Vercel.
Em **Administração → Relatórios Power BI**, edite:

1. **DRE Regional FSP** — `http://localhost:5100/regional.fsp` → endereço público (HTTPS) do DRE.
2. **DRE RH** — `http://localhost:5100/rh` → endereço público (HTTPS) do DRE.

> A página da Vercel é HTTPS: o navegador bloqueia embeds `http://` dentro dela.

---

## Etapa 7 — Checklist de validação em produção

1. [ ] Login com `admin` funciona.
2. [ ] Criar, editar e excluir um usuário de teste.
3. [ ] Criar, editar e excluir um relatório de teste.
4. [ ] Logar com um usuário comum e confirmar que só aparecem os relatórios do departamento dele.
5. [ ] Filtro por departamento no portal funciona.
6. [ ] Os embeds do Power BI carregam.
7. [ ] Dashboard do admin mostra os acessos recentes (logs gravados no Neon).
8. [ ] A sessão continua ativa ao navegar entre páginas.
9. [ ] URLs dos DRE atualizadas e carregando (Etapa 6).
10. [ ] Fazer um commit pequeno, dar `git push` e confirmar o deploy automático na Vercel.

---

## Pontos de atenção (não bloqueiam o deploy)

1. **Sem proteção CSRF** nos formulários do admin. Mitigado parcialmente pelo cookie `SameSite=Lax`;
   o ideal futuro é adicionar `Flask-WTF`/`CSRFProtect`.
2. **Relatório em destaque** no portal é escolhido por `id == 5` ou título contendo "Cockpit Geral".
   Após a migração os ids foram preservados, mas vale conferir se o banner correto aparece.
3. **Sem migrações de schema:** qualquer coluna nova precisa de `ALTER TABLE` manual no Neon.
4. `update_reports.py` continua sendo um script **somente SQLite local** — não use em produção.

---

## Como reverter

```bash
git checkout backup-pre-deploy-v1        # ver o estado anterior sem alterar nada
git reset --hard backup-pre-deploy-v1    # voltar completamente (descarta as alterações)
```
