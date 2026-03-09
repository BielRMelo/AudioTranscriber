@echo off
echo Iniciando OGG Audio Transcriber...
echo =====================================
echo.

REM Verificar se o Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python não está instalado ou não está no PATH do sistema.
    echo Por favor, instale o Python 3.7+ e adicione ao PATH.
    echo.
    pause
    exit /b 1
)

REM Verificar se o Streamlit está instalado
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo Instalando dependências necessárias...
    pip install streamlit ffmpeg-python google-genai psycopg2-binary sqlalchemy
    if errorlevel 1 (
        echo ERRO: Falha ao instalar as dependências.
        echo.
        pause
        exit /b 1
    )
)

REM Verificar se as variáveis de ambiente estão configuradas
if "%GEMINI_API_KEY%"=="" (
    echo.
    echo AVISO: GEMINI_API_KEY não está configurada!
    echo Configure sua chave da API do Gemini antes de usar o app.
    echo.
    echo Como configurar:
    echo 1. Abra o Prompt de Comando como Administrador
    echo 2. Execute: setx GEMINI_API_KEY "sua_chave_aqui"
    echo 3. Reinicie este programa
    echo.
    pause
    exit /b 1
)

echo Todas as dependências estão OK!
echo Iniciando o aplicativo...
echo.
echo O aplicativo será aberto no seu navegador em: http://localhost:5000
echo.
echo Para parar o aplicativo, feche esta janela ou pressione Ctrl+C
echo =====================================
echo.

REM Executar o aplicativo Streamlit
streamlit run app.py --server.port 5000

echo.
echo Aplicativo encerrado.
pause