@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo === IB Conecta: verificando Docker ===
docker version >nul 2>&1
if errorlevel 1 (
  echo Docker nao esta em execucao. Inicie o Docker Desktop e tente de novo.
  exit /b 1
)

set "COMPOSE=docker compose"
docker compose version >nul 2>&1
if errorlevel 1 (
  docker-compose version >nul 2>&1
  if errorlevel 1 (
    echo Docker Compose nao encontrado. Instale o Docker Desktop e tente de novo.
    exit /b 1
  )
  set "COMPOSE=docker-compose"
)

if not exist ".env" (
  if exist ".env.example" (
    echo Copiando .env.example para .env
    copy /Y ".env.example" ".env" >nul
  ) else (
    echo Arquivo .env.example nao encontrado.
    exit /b 1
  )
)

echo === Gerando imagem do container web ===
%COMPOSE% build web
if errorlevel 1 (
  echo Falha ao gerar a imagem do container web.
  exit /b 1
)

echo === Subindo o sistema ===
echo Site: http://localhost:8000/
echo Admin Wagtail: http://localhost:8000/admin/
%COMPOSE% up
exit /b %ERRORLEVEL%
