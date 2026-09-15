# Backups criptografados

Backup diário do PostgreSQL, da mídia (volumes Docker) e do `config.env` (cópia do `.env.prod`), cifrado com [age](https://age-encryption.org/) e enviado ao bucket S3 privado da stack `infra/aws`. A mídia **não** vive no S3 em operação normal (ADR 0005). Este procedimento cobre a issue #33.

## Política de retenção

| Prefixo S3 | O que é | Expiração (lifecycle) |
|---|---|---|
| `daily/YYYY-MM-DD/` | Um artefato por execução | 30 dias |
| `monthly/YYYY-MM/` | Primeiro backup bem-sucedido do mês (UTC) | 366 dias (~12 mensais) |

O nome do objeto é `ib-conecta-<timestamp UTC>.tar.age`. Versionamento do bucket continua ligado; versões não correntes de `daily/` expiram em 7 dias.

A chave **privada** age não está no servidor. Sem ela, o artefato não abre — copie-a para o gerenciador de senhas no dia em que for gerada (`age-keygen`). O destinatário público está em `backup/age-recipients.txt`.

Criptografia em camadas: age no arquivo + SSE-S3 AES256 no bucket.

## Produção (EC2)

Na VM (`/home/ubuntu/ib-conecta`), depois de `git pull`:

```bash
sudo scripts/install-backup-timer.sh
cp .env.backup.example .env.backup
# Confira BACKUP_S3_BUCKET (terraform output backup_bucket_name)
```

O timer dispara **06:00 UTC** (03:00 em Brasília, sem horário de verão) com atraso aleatório de até 10 minutos. Disparo manual:

```bash
sudo systemctl start ib-conecta-backup.service
journalctl -u ib-conecta-backup.service -n 50 --no-pager
```

A EC2 autentica no S3 pelo **instance profile**. Não coloque access keys no `.env.backup` de produção.

Pacotes: `age` e AWS CLI v2. O `user_data` de instâncias novas já os instala; a VM atual precisa do `install-backup-timer.sh` uma vez (o pacote `awscli` v1 não existe no Ubuntu 24.04 ARM).

## Local (notebook + LocalStack)

```bat
scripts\deploy-local.bat
scripts\backup-local.bat
```

Bucket local: `s3://ib-conecta-backups` em `http://localhost:4566`. Identidade de desenvolvimento: `.scratch/ib-conecta-backup.age.key` (gitignored).

## Restauração (passo a passo)

A restauração **padrão** sobe um PostgreSQL descartável e **não** toca o banco de produção.

1. Instale `age` (Ubuntu: `sudo apt-get install -y age`; Windows: binário oficial).
2. Recupere a identidade `AGE-SECRET-KEY` do gerenciador de senhas para um arquivo de permissão restrita, por exemplo `/tmp/ib-conecta-backup.age.key`.
3. Liste os artefatos:

   ```bash
   aws s3 ls s3://ib-conecta-prod-backups-354354997468/daily/ --recursive
   ```

   LocalStack: acrescente `--endpoint-url http://localhost:4566` e as chaves `test`/`test`.
4. Restaure num container jogável (confere `django_migrations`):

   ```bash
   scripts/restore.sh \
     --from s3://ib-conecta-prod-backups-354354997468/daily/YYYY-MM-DD/ib-conecta-....tar.age \
     --identity /tmp/ib-conecta-backup.age.key \
     --into throwaway
   ```

5. Se o throwaway passou e você **precisa** devolver o portal ao snapshot (apaga o banco e a mídia atuais):

   ```bash
   scripts/restore.sh \
     --from s3://.../ib-conecta-....tar.age \
     --identity /tmp/ib-conecta-backup.age.key \
     --into compose \
     --yes
   ```

   Depois: `docker compose -f docker-compose.prod.yml --env-file .env.prod up -d web` e confira `https://www.ibsantaleopoldina.com.br/healthz/`.
6. Apague a identidade do disco da VM (`shred -u` ou `rm` + reboot) — ela não deve permanecer no servidor.

Conteúdo do `.tar.age` depois de `age -d`: `MANIFEST`, `db.dump` (pg_dump `-Fc`), `media.tgz`, `config.env`.

## Rotação da chave age

1. `age-keygen -o novo.key` e acrescente a chave pública em `backup/age-recipients.txt` (pode haver vários destinatários).
2. Faça um backup novo (cifra para todos os recipients).
3. Só então retire o destinatário antigo, quando não precisar mais abrir artefatos velhos.

## O que não entra no artefato

- Volume do PostgreSQL em si (o dump basta)
- Dados do Caddy / certificados Let’s Encrypt (reemitidos)
- `.git` e o código (o repositório já está no GitHub)
