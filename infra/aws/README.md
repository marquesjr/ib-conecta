# Infraestrutura AWS — IB Conecta

Stack Terraform da produção em **`us-east-2` (Ohio)**: VPC pública mínima, EC2 **`t4g.small`** (Graviton, 2 GB), Elastic IP, bucket S3 privado só para backups, instance profile e AWS Budget de US$ 20/mês.

Decisões: ADRs `0001`–`0009` em `docs/adr/`. Épico [#17](https://github.com/marquesjr/ib-conecta/issues/17).

## Pré-requisitos

- Terraform >= 1.5
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) com profile `default` (usuário IAM, não a root)
- Chave pública SSH para a VM

A conta está no **Free Plan** até **16/11/2026** (créditos). Antes dessa data é preciso passar ao plano pago; senão a conta fecha. Depois disso o teto operacional é o budget de US$ 20.

## Bootstrap

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
```

O IP público vai para os registros A no Registro.br (procedimento no README da raiz, seção DNS). Elastic IP atual de produção: veja `terraform output instance_public_ip`.

## Depois do apply

Na VM (usuário `ubuntu`), instale o app com o Compose de produção:

```bash
git clone https://github.com/marquesjr/ib-conecta.git
cd ib-conecta
cp .env.prod.example .env.prod
# Preencha secrets; WEB_CONCURRENCY=1; CADDY_TLS vazio
docker compose -f docker-compose.prod.yml --env-file .env.prod up --build -d
```

O `user_data` já instala Docker Engine + plugin Compose e o Amazon SSM Agent na primeira inicialização (pode levar alguns minutos). Instâncias criadas antes desse change precisam de `sudo scripts/install-ssm-agent.sh` uma vez.

## Deploy contínuo (GitHub Actions)

Push em `master` publica a VM via SSM (sem abrir SSH). Runbook: [`docs/ops/deploy.md`](../../docs/ops/deploy.md). ADR 0012.

Depois de `terraform apply` nesta pasta, anote também:

```bash
terraform output github_actions_deploy_role_arn
```

## Variáveis principais

| Variável | Descrição |
|---|---|
| `region` | Padrão `us-east-2` |
| `aws_profile` | Profile AWS CLI (padrão `default`) |
| `instance_type` | Padrão `t4g.small` |
| `ssh_public_key` | Chave pública OpenSSH |
| `github_repository` | Repo do OIDC de deploy (padrão `marquesjr/ib-conecta`) |
| `ssh_allowed_cidrs` | CIDRs da porta 22 |
| `budget_alert_email` | Destino do alerta de 80% de US$ 20 |
| `enable_budget` | `false` se o IAM não tiver `budgets:*` |

## Destroy

```bash
terraform destroy
```

Esvazie o bucket de backups antes se o destroy falhar em objetos versionados.

## LocalStack

S3 local (não a VPC/EC2): na raiz do repo, `scripts\deploy-local.bat`. Backup/restore: `docs/backup.md`.

Lifecycle do bucket: prefixo `daily/` expira em 30 dias; `monthly/` em 366 dias.
