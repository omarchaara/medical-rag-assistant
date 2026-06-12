@echo off
echo Lancement du projet Medical RAG Assistant...
cd /d "C:\Users\HP\Desktop\Projet 2  Assistant RAG avec LLMs"

echo.
echo VERIFICATION PYTHON...
python --version
if errorlevel 1 (
    echo Python n'est pas installe ou pas dans le PATH
    pause
    exit /b 1
)

echo.
echo INSTALLATION DES DEPENDANCES...
pip install -q fastapi uvicorn streamlit langchain chromadb sentence-transformers mlflow
if errorlevel 1 (
    echo Erreur lors de l'installation des dependances
    pause
    exit /b 1
)

echo.
echo LANCEMENT DE L'API FASTAPI...
start "API FastAPI" cmd /k "uvicorn src.api.main:app --reload"

echo.
echo LANCEMENT DE STREAMLIT...
timeout /t 10 /nobreak
start "Streamlit Interface" cmd /k "streamlit run src/frontend/app.py"

echo.
echo LANCEMENT DE MLFLOW...
timeout /t 15 /nobreak
start "MLflow Tracking" cmd /k "mlflow ui"

echo.
echo ==============
echo PROJET LANCE !
echo ==============
echo.
echo Interfices disponibles:
echo - API FastAPI: http://localhost:8000
echo - Streamlit: http://localhost:8501
echo - MLflow: http://localhost:5000
echo.
echo Appuyez sur une touche pour fermer...
pause