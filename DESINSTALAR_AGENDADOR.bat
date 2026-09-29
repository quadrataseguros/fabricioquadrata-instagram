@echo off
chcp 65001 >nul
schtasks /Delete /TN "Fabricio Instagram - Agenda" /F
echo Agendador desligado. Nada mais sera publicado automaticamente.
pause
