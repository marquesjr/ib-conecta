# S3 só para backups, mídia no volume

Um bucket S3 privado em `us-east-2` guarda artefatos de backup criptografados (issue #33). Uploads públicos do Wagtail e arquivos privados (documentos, partituras) permanecem nos volumes Docker no EBS, servidos pelo Caddy em `/media/` ou pela área autenticada. O gancho `OCI_S3_*` de mídia pública não será portado para produção agora — object storage não entra no caminho do visitante.
