# Backups criptografados com age, retenção no S3

O backup diário é um `pg_dump` custom + `media.tgz` (volumes de mídia pública e privada) + `config.env`, cifrado com **age** para o destinatário em `backup/age-recipients.txt` e enviado ao bucket S3 privado. A identidade (`AGE-SECRET-KEY`) fica só com o operador — não vai para a VM nem para o git. Lifecycle do bucket: 30 dias em `daily/`, 366 dias em `monthly/` (primeiro snapshot bem-sucedido do mês). Issue #33, ADR 0010.
