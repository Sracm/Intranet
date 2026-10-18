@echo off
title Iniciador de Dashboards MQ
color 0A

echo =======================================================
echo          MQ PROFESSIONAL - INICIANDO DASHBOARDS
echo =======================================================
echo.

echo Iniciando Intranet (Porta 5080)...
cd /d "C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\ANTIGRAVITY\PROJETOS\INTRANET"
start "Intranet (5080)" cmd /k python app.py

echo Iniciando Portal de Dashboards (Porta 5000)...
cd /d "C:\Users\amello\.gemini\antigravity\scratch\mariadb_test"
start "Portal Dashboards (5000)" cmd /k python app.py

echo Iniciando Dashboard TV (Porta 5050)...
cd /d "C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\ANTIGRAVITY\PROJETOS\DASHBOARD_tv"
start "Dashboard TV (5050)" cmd /k python app.py

echo Iniciando DRE Gestores (Porta 5100)...
cd /d "C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\ANTIGRAVITY\PROJETOS\Dre_Gestores"
start "DRE Gestores (5100)" cmd /k python app.py

echo Iniciando DRE Empresa (Porta 5150)...
cd /d "C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\ANTIGRAVITY\PROJETOS\Dre_Empresa"
start "DRE Empresa (5150)" cmd /k python app.py

echo Iniciando Dir. Ecommerce (Porta 5200)...
cd /d "C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\ANTIGRAVITY\PROJETOS\Dir.Ecommerce"
start "Dir. Ecommerce (5200)" cmd /k python app.py

echo Iniciando Regional SP - Guelta (Porta 5250)...
cd /d "C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\ANTIGRAVITY\PROJETOS\Regional SP"
start "Regional SP (5250)" cmd /k python app.py

echo Iniciando Call Center, Assistencia Tecnica e SAC (Porta 5300)...
cd /d "C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\ANTIGRAVITY\PROJETOS\Diretoria ADM, Assistencia Tec. SAC"
start "Call Center e SAC (5300)" cmd /k python app.py

:: Retorna para a pasta da Intranet no final
cd /d "C:\Users\amello\OneDrive - MQHAIR\T.I\PROJETOS BI\ANTIGRAVITY\PROJETOS\INTRANET"

echo.
echo =======================================================
echo  Todos os dashboards foram iniciados em novas janelas!
echo =======================================================
echo.
pause
