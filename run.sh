#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON="$VENV_DIR/bin/python"

cd "$SCRIPT_DIR"

if [[ ! -x "$PYTHON" ]]; then
	printf '%s\n' 'Criando ambiente virtual Python...'
	python3 -m venv "$VENV_DIR"
fi

if ! "$PYTHON" -c 'import flask, werkzeug, psycopg2' 2>/dev/null; then
	printf '%s\n' 'Instalando dependencias Python...'
	"$PYTHON" -m pip install -r requirements.txt
fi

printf '%s\n' '======================================================='
printf '%s\n' '         MQ PROFESSIONAL - PORTAL INTRANET'
printf '%s\n' '======================================================='
printf '\n%s\n' 'Verificando banco de dados e dependencias...'
"$PYTHON" -c "import database; database.init_db()"
printf '\n%s\n' 'Iniciando servidor Web na porta 5080...'
printf '%s\n' 'Acesse: http://localhost:5080'
printf '%s\n' 'Pressione CTRL+C para encerrar o servidor.'
printf '%s\n\n' '======================================================='

exec "$PYTHON" app.py
