@echo off

:: Vérifier la présence de Python
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python n'est pas installé ou non configuré dans le PATH.
    echo Veuillez installer Python et réessayer.
    pause
    exit /b
)

:: Installer les dépendances
python -m pip install --upgrade pip
pip install -r requirements.txt

:: Exécuter le script
python spray_paint_app.py

pause