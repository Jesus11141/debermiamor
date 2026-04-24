@echo off
echo ============================================
echo  PRONACA PIFO - Instalacion y Ejecucion
echo ============================================
echo.
echo [1/2] Instalando dependencias...
pip install -r requirements.txt
echo.
echo [2/2] Selecciona el dashboard a ejecutar:
echo   1 - Dashboard Python (puerto 8050)
echo   2 - Dashboard IA     (puerto 8051)
echo.
set /p opcion="Ingresa 1 o 2: "
if "%opcion%"=="1" (
    echo Abriendo Dashboard 1 en http://127.0.0.1:8050
    python dashboard1_python.py
) else (
    echo Abriendo Dashboard 2 IA en http://127.0.0.1:8051
    python dashboard2_ia.py
)
pause
