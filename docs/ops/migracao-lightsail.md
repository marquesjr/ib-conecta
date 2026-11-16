# Migração EC2 → Lightsail (ADR 0013)

Este é um runbook de execução única. Ao fim dele, o portal estará no Lightsail de 1 GB, o DNS apontará para o IP estático novo e o Terraform terá destruído EC2, VPC e Elastic IP. **O bucket de backups não muda.**

Janela fora do ar: do passo 5 ao 7, cerca de 20 a 40 minutos. O tempo depende do restore e da propagação do DNS.

**Congele os merges em `master` até o passo 9.** Este branch muda o `deploy-prod-ssm.sh` para procurar a managed instance híbrida. Por isso:

- Se ele for mergeado antes, o deploy automático falha.
- Se outro PR for mergeado durante a migração, ele publica na EC2 velha.

## 0. Preparação (no dia anterior)

- No Registro.br, baixe o TTL dos dois registros A para 300 s, se o painel permitir.
- Tenha em mãos a chave privada age de backup (gerenciador de senhas), a chave SSH `~/.ssh/id_ed25519_ib_conecta` e o profile AWS `default` válido.
- No laptop, faça checkout deste branch em `infra/aws` e confira se o state local é o de produção: `terraform state list | grep aws_instance.app`.
- Tire do `terraform.tfvars` as variáveis que não existem mais (`instance_type`, `boot_volume_size_gbs`). Acrescente `budget_limit_usd = 12` se quiser deixar explícito.
- Confira os IDs do bundle e do blueprint:

  ```bash
  aws lightsail get-bundles --region us-east-2 --query "bundles[?ramSizeInGb==\`1.0\`].[bundleId,price,isActive]" --output table
  aws lightsail get-blueprints --region us-east-2 --query "blueprints[?contains(blueprintId,'ubuntu')].blueprintId"
  ```

## 1. Criar só os recursos novos

Com `-target`, a EC2 e a rede antigas ficam intactas. Elas saem do código, mas continuam no state até o passo 8.

```bash
cd infra/aws
terraform plan \
  -target=aws_lightsail_key_pair.app \
  -target=aws_lightsail_instance.app \
  -target=aws_lightsail_static_ip.app \
  -target=aws_lightsail_static_ip_attachment.app \
  -target=aws_lightsail_instance_public_ports.app \
  -target=aws_iam_user.backup \
  -target=aws_iam_user_policy.backup_s3 \
  -target=aws_iam_role.ssm_hybrid \
  -target=aws_iam_role_policy_attachment.ssm_hybrid_core \
  -target=aws_ssm_activation.app \
  -out=lightsail.tfplan
# Revise: só "create". Nada de destroy nem de change no bucket.
terraform apply lightsail.tfplan
terraform output instance_public_ip
terraform output ssm_activation_id
terraform output -raw ssm_activation_code
```

O usuário `cursor` tem as permissões de Lightsail, SSM, IAM e Budgets que este apply exige. Em 16/11/2026 elas foram conferidas com `aws iam simulate-principal-policy`, e os IDs `micro_3_0` (US$ 7), `ubuntu_24_04` e `us-east-2a` foram confirmados com `get-bundles`, `get-blueprints` e `get-regions`.

A activation vence em 24 h. Se passar do prazo antes do passo 2, rode `terraform apply -replace=aws_ssm_activation.app -target=aws_ssm_activation.app`.

## 2. Preparar a VM nova

Espere de 3 a 5 minutos para o launch script terminar (Docker, swap e AWS CLI). Depois:

```bash
ssh -i ~/.ssh/id_ed25519_ib_conecta ubuntu@<IP novo>
cloud-init status --wait          # deve terminar em "status: done"
free -m                           # Swap: 2047
docker --version && aws --version

git clone https://github.com/marquesjr/ib-conecta.git
cd ib-conecta
git switch infra/lightsail        # até o merge; depois, master
sudo SSM_ACTIVATION_ID='<id>' SSM_ACTIVATION_CODE='<code>' scripts/install-ssm-agent.sh
```

Do laptop, confirme que o nó `mi-…` está `Online` e com a tag `Name=ib-conecta-prod-app`. Os comandos estão em [`deploy.md`](deploy.md), passo 2.

## 3. Segredos na VM nova

Copie o `.env.prod` da EC2 para a VM nova sem passar pelo repositório:

```bash
# no laptop
scp -i ~/.ssh/id_ed25519_ib_conecta ubuntu@52.14.75.54:ib-conecta/.env.prod /tmp/ib.env.prod
scp -i ~/.ssh/id_ed25519_ib_conecta /tmp/ib.env.prod ubuntu@<IP novo>:ib-conecta/.env.prod
shred -u /tmp/ib.env.prod 2>/dev/null || rm -f /tmp/ib.env.prod
```

Na VM nova, confira `WEB_CONCURRENCY=1`, `CADDY_TLS=` (vazio) e `SITE_ADDRESS=www.ibsantaleopoldina.com.br`.

Crie a access key do usuário de backup e o `.env.backup`:

```bash
# no laptop
aws iam create-access-key --user-name ib-conecta-prod-backup
```

```bash
# na VM nova
cp .env.backup.example .env.backup
chmod 600 .env.backup
# preencha AWS_ACCESS_KEY_ID e AWS_SECRET_ACCESS_KEY com a saída acima
sudo scripts/install-backup-timer.sh
```

## 4. Subir o stack vazio e testar o build

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up --build -d db web
docker compose -f docker-compose.prod.yml --env-file .env.prod ps   # web healthy
free -m
```

O Caddy ainda não sobe, porque o DNS aponta para a EC2 e o Let's Encrypt falharia.

## 5. Congelar a EC2 e fazer o último backup (início da janela)

```bash
ssh -i ~/.ssh/id_ed25519_ib_conecta ubuntu@52.14.75.54
cd ib-conecta
docker compose -f docker-compose.prod.yml --env-file .env.prod stop web caddy
sudo systemctl start ib-conecta-backup.service   # com web parado, BACKUP_SKIP_DISCARD=1 se falhar no discard
journalctl -u ib-conecta-backup.service -n 20 --no-pager   # anote o DAILY_KEY
```

Se o backup reclamar do `discard_retreat_sensitive_data` porque o `web` está parado, rode `BACKUP_SKIP_DISCARD=1 bash scripts/backup.sh` como `ubuntu`. O descarte volta a rodar no entrypoint da VM nova.

## 6. Restaurar na VM nova

Copie a identidade age para um arquivo temporário na VM nova e restaure:

```bash
cd ~/ib-conecta
scripts/restore.sh \
  --from s3://ib-conecta-prod-backups-354354997468/daily/<DIA>/<ARQUIVO>.tar.age \
  --identity /tmp/ib-conecta-backup.age.key \
  --into compose --yes
shred -u /tmp/ib-conecta-backup.age.key
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --wait
```

`up -d --wait` sobe o Caddy junto. Ele tenta o certificado e vai repetir até o DNS mudar.

## 7. Trocar o DNS (fim da janela)

No Registro.br, aponte os dois registros A (`ibsantaleopoldina.com.br` e `www`) para o IP estático novo. Depois:

```bash
dig +short www.ibsantaleopoldina.com.br        # IP novo
docker compose -f docker-compose.prod.yml --env-file .env.prod logs -f caddy   # "certificate obtained successfully"
curl -fsS https://www.ibsantaleopoldina.com.br/healthz/
```

Se o Caddy desistiu antes da propagação, rode `docker compose ... restart caddy`. Por fim, confira login, documentos privados e uma imagem em `/media/`.

## 8. Destruir a infraestrutura antiga

Espere pelo menos um dia de funcionamento normal e um backup noturno bem-sucedido na VM nova (`aws s3 ls s3://…/daily/`). Então:

```bash
cd infra/aws
terraform plan -out=cleanup.tfplan
```

O plano deve ter:

- **destroy:** `aws_instance.app`, `aws_eip.app`, `aws_key_pair.app`, `aws_vpc.app`, `aws_subnet.public`, `aws_internet_gateway.app`, `aws_route_table*`, `aws_security_group.app`, `aws_iam_instance_profile.app`, `aws_iam_role.app`, `aws_iam_role_policy.backup_s3`, `aws_iam_role_policy_attachment.ssm_core`.
- **update in-place:** `aws_iam_role_policy.github_deploy` (troca EC2 por managed instance) e `aws_budgets_budget.monthly` (US$ 12).
- **nenhuma** mudança em `aws_s3_bucket.*`.

```bash
terraform apply cleanup.tfplan
```

Isso apaga o volume da EC2. O último backup da EC2 (passo 5) continua no S3 por 30 dias (`daily/`) e o mensal por 366.

## 9. Merge e primeiro deploy pelo pipeline

1. Faça merge do PR deste branch em `master`. Na VM: `git switch master && git pull`.
2. O push dispara o **Deploy produção**. Ele deve achar o `mi-…` e ficar verde.
3. Descongele os merges.
4. Nos dias seguintes, confira no Billing que a EC2, o EBS e o IPv4 público pararam de cobrar. No mês da migração os dois ambientes cobram juntos por alguns dias, então o alerta de 80% de US$ 12 pode disparar uma vez.

## Rollback

- **Até o passo 7:** volte o DNS (se já trocou) e rode `docker compose ... up -d` na EC2. Ela continua intacta.
- **Depois do passo 8:** não há EC2. Recrie a VM com `terraform apply -replace=aws_lightsail_instance.app` e restaure o backup mais recente (passos 2 a 7).
