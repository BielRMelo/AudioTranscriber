@echo off
title Construindo o Executável do OGG Audio Transcriber
echo ===================================================
echo   Construindo OGG Audio Transcriber (PyInstaller)
echo ===================================================
echo.

echo 1. Verificando ambiente virtual...
if not exist .venv (
    echo ERRO: Ambiente virtual (.venv) não encontrado.
    echo Execute setup.bat antes de construir o executável.
    pause
    exit /b 1
)

echo 2. Instalando dependências de build no ambiente virtual...
.venv\Scripts\python -m pip install pyinstaller imageio-ffmpeg

echo.
echo 2. Empacotando com PyInstaller...
echo Isso pode levar alguns minutos. Aguarde...

.venv\Scripts\pyinstaller --noconfirm --onedir --windowed ^
  --add-data "app.py;." ^
  --add-data "audio_processor.py;." ^
  --add-data "database_service.py;." ^
  --add-data "transcription_service.py;." ^
  --copy-metadata streamlit ^
  --copy-metadata google-genai ^
  --name "AudioTranscriber" ^
  run_main.py

echo.
if %ERRORLEVEL% EQU 0 (
    echo ===================================================
    echo   CONSTRUÇÃO CONCLUÍDA COM SUCESSO!
    echo ===================================================
    echo O aplicativo executável foi gerado na pasta "dist\AudioTranscriber".
    echo Para compartilhar o aplicativo, copie toda a pasta "dist\AudioTranscriber"
    echo ou crie um arquivo ZIP dela.
) else (
    echo ===================================================
    echo   ERRO NA CONSTRUÇÃO!
    echo ===================================================
    echo Verifique as mensagens de erro acima.
)

pause
