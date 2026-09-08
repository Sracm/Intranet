# 🏢 Portal Intranet MQ Professional — Central Power BI

Portal corporativo para centralização e governança de relatórios analíticos em **Power BI** da **MQ Professional**, com autenticação por login/senha, controle granular de acessos por departamento/colaborador e painel administrativo dinâmico.

Construído de acordo com as especificações oficiais do **MQ Design System** (Tipografia Montserrat, paleta Preto `#121212`, Dourado `#CB9727`, Creme `#EDE4DA` e componentes dark premium).

---

## 🚀 Como Iniciar o Projeto

### Opção 1: Pelo Script Windows (Recomendado)
Basta dar dois cliques no arquivo:
```cmd
run.bat
```

### Opção 2: Pelo Terminal / Linha de Comando
```cmd
python app.py
```
O servidor estará acessível no navegador em:
👉 **[http://localhost:5080](http://localhost:5080)**

---

## 🔑 Credenciais Padrão Pré-Cadastradas

| Perfil | Usuário | Senha | Acesso / Permissões |
|---|---|---|---|
| **Administrador Geral** | `admin` | `admin` | Acesso total a todos os relatórios e ao Painel de Administração |
| **Equipe Logística** | `logistica` | `123` | Acesso aos relatórios de **Logística** (Expedição, Kardex) e Institucionais |
| **Equipe Comercial** | `comercial` | `123` | Acesso aos relatórios de **Comercial & Vendas** e Institucionais |

> **Nota de Segurança:** As senhas são criptografadas com hash PBKDF2/SHA256 (`werkzeug.security`). O administrador pode criar novos colaboradores ou redefinir senhas a qualquer momento pelo painel `/admin/users`.

---

## 📁 Departamentos Pré-Cadastrados

1. 🚚 **Logística** (`logistica`) — Gestão de fretes, expedição, devoluções, estoque e prazos de entrega.
2. 📈 **Comercial & Vendas** (`comercial`) — Faturamento por canal, pedidos e representantes.
3. 💵 **Financeiro** (`financeiro`) — Fluxo de caixa, conciliação e DRE gerencial.
4. 📑 **Fiscal** (`fiscal`) — Auditoria de notas, tarefas fiscais e apuração de tributos.
5. 📣 **Marketing** (`marketing`) — Campanhas digitais, conversão de e-commerce e CAC/ROAS.
6. 💻 **TI & BI** (`ti_bi`) — Pipelines de dados, governança e monitoramento de infraestrutura.
7. 💼 **Diretoria** (`diretoria`) — Cockpit executivo e KPIs consolidados da empresa.

Novos departamentos podem ser criados dinamicamente em **Administração > Departamentos**.

---

## 📊 Como Cadastrar Novos Relatórios Power BI

1. Faça login com o perfil **Administrador** (`admin`).
2. No menu superior, clique em **Administração** e vá na aba **Relatórios Power BI**.
3. Clique em **"+ Novo Relatório Power BI"**.
4. Preencha:
   - **Título**: Nome do relatório exibido no portal.
   - **URL do Power BI**: Cole o link do relatório (*Publicar na Web / Embed URL* ou link seguro do Power BI Service).
   - **Departamento Responsável**: Escolha o setor (ex: Logística).
   - **Regra de Visibilidade**:
     - *Restrito ao Depto*: Apenas pessoas com permissão para esse departamento verão o relatório.
     - *Institucional*: Todos os colaboradores logados verão o relatório.
5. Clique em **Salvar Relatório**. O relatório já aparecerá instantaneamente para os usuários autorizados!

---

## 🛠️ Recursos de Interface e Experiência

- **Busca em Tempo Real**: Filtro instantâneo por nome, palavras-chave ou departamento enquanto digita.
- **Visualizador Imersivo**: Visualização limpa em tela cheia com botão de recarga de dados e abertura em nova aba.
- **Auditoria de Acessos**: Log de registros de acessos dos colaboradores para governança de dados.
- **Design Responsivo**: Adaptado para monitores ultra-wide, telas de TV, notebooks e dispositivos móveis.
"# Intranet" 
