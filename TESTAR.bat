@echo off
cd /d "%~dp0"
pip install requests python-dotenv -q
python scripts\testar_conexao.py
pause
