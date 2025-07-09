@echo off
title Configuração do OGG Audio Transcriber
echo ========================================
echo   CONFIGURAÇÃO DO OGG AUDIO TRANSCRIBER
echo ========================================
echo.

REM Verificar se está executando como administrador
net session >nul 2>&1
if errorlevel 1 (
    echo Este script precisa ser executado como Administrador.
    echo Clique com o botão direito e selecione "Executar como administrador"
    echo.
    pause
    exit /b 1
)

echo Verificando instalação do Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python não encontrado. Baixando e instalando...
    echo.
    echo Por favor, baixe o Python manualmente de: https://python.org/downloads
    echo Durante a instalação, marque "Add Python to PATH"
    echo Depois execute este script novamente.
    echo.
    pause
    exit /b 1
) else (
    echo ✓ Python encontrado!
)

echo.
echo Instalando dependências Python...
pip install --upgrade pip
pip install streamlit ffmpeg-python google-genai psycopg2-binary sqlalchemy

if errorlevel 1 (
    echo Erro ao instalar dependências Python.
    pause
    exit /b 1
) else (
    echo ✓ Dependências Python instaladas!
)

echo.
echo Verificando FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo FFmpeg não encontrado.
    echo.
    echo Opções para instalar FFmpeg:
    echo 1. Baixar de: https://ffmpeg.org/download.html
    echo 2. Ou usar Chocolatey: choco install ffmpeg
    echo.
    echo Depois de instalar, execute este script novamente.
    pause
    exit /b 1
) else (
    echo ✓ FFmpeg encontrado!
)

echo.
echo ========================================
echo   CONFIGURAÇÃO DA CHAVE API GEMINI
echo ========================================
echo.
echo Para usar o aplicativo, você precisa de uma chave da API do Google Gemini.
echo.
echo Como obter:
echo 1. Acesse: https://ai.google.dev
echo 2. Crie uma conta gratuita
echo 3. Gere uma chave da API
echo 4. Copie a chave (começa com "AIza...")
echo.

set /p api_key="Digite sua chave da API Gemini: "

if "%api_key%"=="" (
    echo Nenhuma chave fornecida. Execute o script novamente quando tiver a chave.
    pause
    exit /b 1
)

REM Configurar variável de ambiente
setx GEMINI_API_KEY "%api_key%"
set GEMINI_API_KEY=%api_key%

echo.
echo ✓ Chave da API configurada!
echo.
echo ========================================
echo          CONFIGURAÇÃO CONCLUÍDA!
echo ========================================
echo.
echo Tudo está pronto! Você pode agora:
echo.
echo 1. Duplo clique em "run_app.bat" para executar o aplicativo
echo 2. O aplicativo abrirá em http://localhost:5000
echo 3. Faça upload de arquivos .ogg para transcrever
echo.
echo IMPORTANTE: Reinicie o computador antes de usar o aplicativo
echo para que a variável de ambiente seja carregada corretamente.
echo.
pause