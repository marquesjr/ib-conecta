@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

where docker >nul 2>&1
if errorlevel 1 (
  echo Docker nao esta no PATH. Instale o Docker Desktop e tente de novo.
  exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
  echo Docker nao esta em execucao. Abra o Docker Desktop e tente de novo.
  exit /b 1
)

echo [1/4] Subindo Compose local + LocalStack ^(S3^)...
docker compose -f docker-compose.yml -f docker-compose.localstack.yml up -d --build
if errorlevel 1 (
  echo Falha ao subir os containers.
  exit /b 1
)

echo [2/4] Esperando o LocalStack responder em http://localhost:4566 ...
set /a _tries=0
:wait_ls
curl -fsS http://localhost:4566/_localstack/health >nul 2>&1
if not errorlevel 1 goto ls_ready
set /a _tries+=1
if %_tries% GEQ 60 (
  echo LocalStack nao ficou pronto a tempo.
  exit /b 1
)
timeout /t 2 /nobreak >nul
goto wait_ls

:ls_ready
echo [3/4] Garantindo o bucket s3://ib-conecta-backups ...
docker compose -f docker-compose.yml -f docker-compose.localstack.yml exec -T localstack awslocal s3api head-bucket --bucket ib-conecta-backups >nul 2>&1
if errorlevel 1 (
  docker compose -f docker-compose.yml -f docker-compose.localstack.yml exec -T localstack awslocal s3 mb s3://ib-conecta-backups
  if errorlevel 1 (
    echo Falha ao criar o bucket no LocalStack.
    exit /b 1
  )
)

echo [4/4] Pronto.
echo.
echo   Portal:     http://localhost:8000/
echo   LocalStack: http://localhost:4566/
echo   Bucket:     s3://ib-conecta-backups
echo.
echo   AWS_ACCESS_KEY_ID=test
echo   AWS_SECRET_ACCESS_KEY=test
echo   AWS_DEFAULT_REGION=us-east-2
echo   AWS_ENDPOINT_URL=http://localhost:4566
echo.
echo   Parar: docker compose -f docker-compose.yml -f docker-compose.localstack.yml down
exit /b 0
