#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON="$VENV_DIR/bin/python"
PIP="$VENV_DIR/bin/pip"

cd "$SCRIPT_DIR"

echo "======================================================="
echo "         MQ PROFESSIONAL - PORTAL INTRANET"
echo "======================================================="
echo

# -------------------------------------------------------
# Cria o ambiente virtual se não existir
# -------------------------------------------------------

if [[ ! -x "$PYTHON" ]]; then
    echo "Ambiente virtual não encontrado."
    echo "Criando .venv..."

    python3 -m venv "$VENV_DIR"
fi

# -------------------------------------------------------
# Instala / atualiza dependências
# -------------------------------------------------------

echo "Verificando dependências Python..."

"$PIP" install --upgrade pip

if [[ -f "$SCRIPT_DIR/requirements.txt" ]]; then
    echo "Instalando dependências do requirements.txt..."
    "$PIP" install -r "$SCRIPT_DIR/requirements.txt"
else
    echo "ERRO: requirements.txt não encontrado."
    exit 1
fi

# -------------------------------------------------------
# Banco de dados
# -------------------------------------------------------

echo
echo "Verificando banco de dados..."
"$PYTHON" -c "import database; database.init_db()"

# -------------------------------------------------------
# Inicia aplicação
# -------------------------------------------------------

echo
echo "Iniciando servidor Web na porta 5080..."
echo "Acesse: http://localhost:5080"
echo "Pressione CTRL+C para encerrar o servidor."
echo
echo "======================================================="

exec "$PYTHON" app.py