# Infraestrutura AWS — IB Conecta

Stack Terraform da produção em **`us-east-2` (Ohio)**:

- Instância **Lightsail `micro_3_0`** (1 GB, x86_64, cerca de US$ 7/mês) com IP estático e firewall da instância.
- Bucket S3 privado, usado só para backups, mais um IAM user restrito a ele.
- Registro híbrido da VM no SSM e role OIDC para o deploy pelo GitHub Actions.
- AWS Budget de US$ 12/mês.

Decisões: ADRs `0001`–`0013` em `docs/adr/`, com destaque para a [0013](../../docs/adr/0013-lightsail-1gb.md) (Lightsail). Épico [#17](https://github.com/marquesjr/ib-conecta/issues/17).

Para migrar a partir da EC2 antiga, siga [`docs/ops/migracao-lightsail.md`](../../docs/ops/migracao-lightsail.md).

## Pré-requisitos

- Terraform >= 1.5.
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) com profile `default` (usuário IAM, não a root), com permissão de Lightsail, SSM, IAM, S3 e Budgets.
- Chave pública SSH para a VM.

## Bootstrap (do zero)

```bash
cd infra/aws
cp terraform.tfvars.example terraform.tfvars
# Edite terraform.tfvars: chave SSH, CIDR de SSH, e-mail do budget

terraform init
terraform fmt -recursive
terraform validate
terraform plan
terraform apply
```

Anote:

```bash
terraform output instance_public_ip
terraform output backup_bucket_name
terraform output ssh_command
terraform output ssm_activation_id
terraform output -raw ssm_activation_code
```

O IP estático vai para os registros A no Registro.br (procedimento no README da raiz, seção DNS).

## Depois do apply

O launch script (`user_data.sh`) instala Docker Engine + Compose, age e AWS CLI v2 e cria 2 GB de swap na primeira inicialização. Isso leva alguns minutos; acompanhe com `cloud-init status --wait`. Na VM (usuário `ubuntu`):

```bash
git clone https://github.com/marquesjr/ib-conecta.git
cd ib-conecta
sudo SSM_ACTIVATION_ID='<id>' SSM_ACTIVATION_CODE='<code>' scripts/install-ssm-agent.sh
cp .env.prod.example .env.prod
# Preencha os secrets; WEB_CONCURRENCY=1; CADDY_TLS vazio
docker compose -f docker-compose.prod.yml --env-file .env.prod up --build -d
```

Backups (access key do IAM user `ib-conecta-prod-backup` + timer): [`docs/backup.md`](../../docs/backup.md).

## Deploy contínuo (GitHub Actions)

Push em `master` publica na VM via SSM híbrido, sem abrir SSH. Runbook: [`docs/ops/deploy.md`](../../docs/ops/deploy.md). ADRs 0012 e 0013.

## Variáveis principais

| Variável | Descrição |
|---|---|
| `region` | Padrão `us-east-2` |
| `aws_profile` | Profile AWS CLI (padrão `default`) |
| `availability_zone` | Vazio = `<region>a` |
| `lightsail_bundle_id` | Padrão `micro_3_0` (1 GB). Veja `aws lightsail get-bundles` |
| `lightsail_blueprint_id` | Padrão `ubuntu_24_04` |
| `ssh_public_key` | Chave pública OpenSSH |
| `github_oidc_sub_prefix` | Prefixo imutável do claim `sub` (padrão `repo:marquesjr@2216233/ib-conecta@1314311915`) |
| `ssh_allowed_cidrs` | CIDRs da porta 22 |
| `budget_limit_usd` | Teto do budget (padrão 12, com alerta em 80%) |
| `budget_alert_email` | Destino do alerta |
| `enable_budget` | `false` se o IAM não tiver `budgets:*` |

## Cuidados

- `user_data` e `blueprint_id` estão em `ignore_changes`. Mudar qualquer um dos dois recriaria a VM e apagaria os volumes Docker (banco e mídia).
- Para trocar de plano (`lightsail_bundle_id`), o Terraform também recria a VM. O caminho seguro é fazer um snapshot pelo console do Lightsail, criar a instância nova a partir dele e importar no state, ou repetir o runbook de migração com backup e restore.

## Destroy

```bash
terraform destroy
```

Esvazie o bucket de backups antes, se o destroy falhar por causa de objetos versionados.

## LocalStack

S3 local (não emula o Lightsail): na raiz do repo, rode `scripts\deploy-local.bat`. Backup/restore: `docs/backup.md`.

Lifecycle do bucket: o prefixo `daily/` expira em 30 dias e o `monthly/` em 366 dias.
