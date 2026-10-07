# 🔐 Plano de Implantação: Gestores e Centros de Custo (Intranet & DRE Gestores)

Este documento contém todo o detalhamento técnico e o passo a passo de implantação da governança de acessos por Centro de Custo para os Gestores da MQ HAIR.

---

## 1. Mapeamento Oficial de Gestores e Centros de Custo

| Gestor (Login) | Nome | Canal / Área | Centros de Custo Autorizados |
| :--- | :--- | :--- | :--- |
| **`ricardo.pavao`** | Ricardo Pavão | Distribuição | `1010200` (RJ), `1010300` (ND), `1010400` (SUL), `1020000` (Distribuição) |
| **`vinicius.resina`** | Vinicius Resina | E-commerce | `24000000` (FCC Ecom), `12190000` (Shopee), `12130000` (VTEX), `12090000` (Magalu), `12050000` (Mercado Livre), `12040000` (Loja Física), `12140000` (DM/Parlux) |
| **`thiago.figueiredo`** | Thiago Figueiredo | Desenv. Produto | `10020000` (Desenvolvimento de Produtos) |
| **`ricardo.stobodzian`** | Ricardo Stobodzian | Regional SP | `1010100` (Varejo SP) |
| **`felipe.castellano`** | Felipe Castellano | Comex | `1050000` (Comex), `24010101` (FCC Amazon), `23020000` (FCC Comércio), `23010000` (FCC Comércio EUA) |
| **`maria.macedo`** | Maria Macedo | RH | `9010000` (Recursos Humanos) |
| **`dirceu.parente`** | Dirceu Parente | Logística | `4010500` (Logística SP), `4010600` (Logística RJ), `4010700` (Logística SC) |
| **`seije.luz`** | Seije Luz | Marketing & TI | `10010000` (MKT Geral), `10011001` (MKT Nacional MQ), `10011002` (Force Barb), `10011003` (Acessórios), `10011005` (Digital), `7010000` (TI Interno), `7020000` (Serviços TI) |
| **`frederico.donizeti`** | Frederico Donizeti | Assit. & Adm | `6040000` (Adm), `19000000` (Adm Corp), `3000000` (Assistência Técnica), `2010000` (SAC) |

---

## 2. Arquitetura de Segurança & Integração

1. **Intranet (`http://host:5080`)**:
   - É o **Hub Central**. O gestor entra com seu login e senha.
   - O menu da Intranet lista apenas o dashboard **DRE - Meus Resultados** (além dos outros permitidos para o perfil dele).
   - Ao carregar o DRE dentro do iframe, a Intranet assina a requisição ou gera um link seguro com o identificador do gestor.

2. **DRE Gestores (`http://host:5100`)**:
   - O DRE Gestores recebe a identificação do gestor.
   - **Dupla Camada de Trava**:
     - **Interface (Frontend)**: O seletor de Centros de Custo só exibe os centros autorizados daquele gestor.
     - **API (Backend)**: Toda requisição para `/api/dre` e `/api/filtros` é validada pelo backend. Mesmo se o usuário tentar alterar parâmetros no DevTools, a query do banco bloqueia centros que não pertencem a ele.

---

## 3. Passo a Passo de Execução e Deploy no Linux

### Passo 1: Executar Carga no Banco (Local ou no Servidor Linux)
Na pasta do projeto Intranet:
```bash
python "login e acessos/seed_gestores.py"
```
*Isso criará a tabela `user_cost_centers`, cadastrará os 9 gestores e aplicará os 33 centros de custo com senha provisória `MQ@gestor2026`.*

### Passo 2: Enviar ao GitHub (Windows)
```bash
git add "login e acessos"
git commit -m "feat: adicionar módulo de login e acessos dos gestores com centros de custo"
git push origin main
```

### Passo 3: Atualizar no Servidor Linux
No servidor onde a Intranet e o DRE Gestores rodam:
```bash
cd /home/antonio/Intranet
git pull origin main
source .venv/bin/activate
python "login e acessos/seed_gestores.py"
```

### Passo 4: Reiniciar os Serviços no Servidor Linux
Reiniciar os processos da Intranet e DRE Gestores (via systemd, supervisor ou pm2/nohup):
```bash
sudo systemctl restart intranet.service
# ou bash run.sh
```
