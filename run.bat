@echo off
title Portal Intranet MQ Professional - Relatorios Power BI
color 06

echo =======================================================
echo          MQ PROFESSIONAL - PORTAL INTRANET
echo =======================================================
echo.
echo Verificando banco de dados e dependencias...
python -c "import database; database.init_db()"
echo.
echo Iniciando servidor Web na porta 5080...
echo Acesse: http://localhost:5080
echo.
echo Pressione CTRL+C para encerrar o servidor.
echo =======================================================
echo.

python app.py
pause
