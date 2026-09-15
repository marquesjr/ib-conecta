@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

if not exist ".scratch\ib-conecta-backup.age.key" (
  echo Gere a identidade age em .scratch\ib-conecta-backup.age.key ^(age-keygen^) antes do backup local.
  exit /b 1
)

set "BACKUP_S3_BUCKET=ib-conecta-backups"
set "BACKUP_S3_REGION=us-east-2"
set "BACKUP_COMPOSE_FILE=docker-compose.yml"
set "BACKUP_ENV_FILE=.env"
set "BACKUP_AGE_RECIPIENTS=backup/age-recipients.txt"
set "AWS_ENDPOINT_URL=http://localhost:4566"
set "AWS_ACCESS_KEY_ID=test"
set "AWS_SECRET_ACCESS_KEY=test"
set "AWS_DEFAULT_REGION=us-east-2"

where docker >nul 2>&1
if errorlevel 1 (
  echo Docker nao esta no PATH.
  exit /b 1
)

"C:\Program Files\Git\bin\bash.exe" scripts/backup.sh
exit /b %ERRORLEVEL%
