@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "PYW="
for /f "delims=" %%i in ('where pythonw 2^>nul') do if not defined PYW set "PYW=%%i"
if not defined PYW (
  echo ERRO: pythonw.exe nao encontrado. Verifique se o Python esta instalado.
  pause & exit /b 1
)
schtasks /Create /TN "Fabricio Instagram - Agenda" /TR "\"%PYW%\" \"%~dp0scripts\publicar_agenda.py\"" /SC MINUTE /MO 15 /F
if errorlevel 1 ( echo ERRO ao criar a tarefa. & pause & exit /b 1 )
echo.
echo Agendador instalado! Ele confere a agenda.txt a cada 15 minutos.
echo Historico das publicacoes: agenda_log.txt
echo Para desligar: DESINSTALAR_AGENDADOR.bat
pause
