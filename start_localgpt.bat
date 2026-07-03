@echo off

cd /d E:\chatbot\projects\streamlit_chat

call E:\chatbot\venv\Scripts\activate.bat

start "" ollama serve

timeout /t 5 > nul

start "" python -m streamlit run app.py

timeout /t 5 > nul

start http://localhost:8501