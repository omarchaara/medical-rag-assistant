@echo off
echo ====================================
echo LANCEMENT DE STREAMLIT
echo ====================================
echo.

cd /d "C:\Users\HP\Desktop\Projet 2  Assistant Medical RAG avec LLMs"

echo Verification de Python...
python --version
if errorlevel 1 (
    echo ERREUR: Python n'est pas installe ou pas dans le PATH
    pause
    exit /b 1
)

echo.
echo Verification de Streamlit...
python -c "import streamlit; print('Streamlit version:', streamlit.__version__)"
if errorlevel 1 (
    echo Installation de Streamlit...
    pip install streamlit
    if errorlevel 1 (
        echo ERREUR: Impossible d'installer Streamlit
        pause
        exit /b 1
    )
)

echo.
echo Lancement de Streamlit...
echo L'interface sera disponible sur: http://localhost:8501
echo.
echo ====================================
echo NE FERMEZ PAS CETTE FENETRE !
echo ====================================
echo.

streamlit run src/frontend/app.py

if errorlevel 1 (
    echo.
    echo ====================================
    echo ERREUR lors du lancement de Streamlit
    echo ====================================
    echo.
    echo Essayez avec un port different:
    echo streamlit run src/frontend/app.py --server.port 8502
    echo.
)

pause