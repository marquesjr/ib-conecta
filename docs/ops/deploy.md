# Deploy produção ao fazer push em master (issue #17)

O portal em `https://www.ibsantaleopoldina.com.br` **não** atualiza sozinho só com o merge. Quem publica é o workflow **Deploy produção**: push em `master` (ou *Run workflow*) assume uma role IAM por OIDC, manda um SSM Run Command na EC2 e a VM faz o mesmo `git` + `docker compose` documentado no README.

Não abre a porta 22 para o GitHub. Não usa runner self-hosted (o repositório é público). Não grava access key da AWS no GitHub.

## O que o pipeline faz

1. Job `verify` — `bash -n` nos scripts (também roda em pull request).
2. Job `deploy` — só em `push`/`workflow_dispatch` em `master`:
   - OIDC → role `ib-conecta-prod-github-deploy`
   - Localiza a EC2 pela tag `Name=ib-conecta-prod-app`
   - SSM: `git fetch` + `checkout` do SHA do push + `scripts/deploy-prod.sh`
   - `docker compose -f docker-compose.prod.yml --env-file .env.prod up --build -d --wait`
   - Checagem externa: `python scripts/check-uptime.py` (igual ao monitoramento)

O rebuild **é obrigatório**: a imagem Docker de produção não faz bind-mount do código.

## Passos únicos (operador com AWS + SSH)

Faça **uma vez**. Sem isso a Action falha (não inventamos credenciais da conta).

### 1. IAM + OIDC (Terraform, máquina que tem o state)

```bash
cd infra/aws
terraform init
terraform apply
terraform output github_actions_deploy_role_arn
terraform output github_oidc_provider_arn
```

Isso **não** recria a EC2 (`user_data` está em `ignore_changes`). Só entra: policy `AmazonSSMManagedInstanceCore` na role da VM, provider OIDC do GitHub e a role de deploy.

A Action usa, por padrão:

`arn:aws:iam::354354997468:role/ib-conecta-prod-github-deploy`

Se o apply imprimir outro ARN, grave em GitHub → Settings → Secrets and variables → Actions → **Variables** → `AWS_DEPLOY_ROLE_ARN`.

### 2. Agente SSM na VM (SSH uma vez)

O `user_data` novo instala o agente em instâncias futuras. A VM atual ignora mudança de `user_data`, então:

```bash
ssh -i ~/.ssh/id_ed25519_ib_conecta ubuntu@52.14.75.54
cd /home/ubuntu/ib-conecta
git pull origin master
sudo scripts/install-ssm-agent.sh
```

Se o `git pull` ainda não tiver este commit, baixe o instalador do `master` depois do merge:

```bash
curl -fsSL https://raw.githubusercontent.com/marquesjr/ib-conecta/master/scripts/install-ssm-agent.sh | sudo bash
```

Reinicie o agente se o Terraform/IAM tiver sido aplicado **depois** da instalação:

```bash
sudo systemctl restart amazon-ssm-agent
```

Do laptop (profile `default`, região `us-east-2`):

```bash
aws ssm describe-instance-information \
  --region us-east-2 \
  --query 'InstanceInformationList[].{Id:InstanceId,Ping:PingStatus,Name:ComputerName}' \
  --output table
```

`PingStatus` tem de ser `Online`. Se a lista vier vazia: a role `ib-conecta-prod-ec2` ainda não tem `AmazonSSMManagedInstanceCore`, ou o agente não está rodando.

### 3. Disparar o primeiro deploy

Depois do merge deste pipeline (ou com o workflow já em `master`):

1. GitHub → Actions → **Deploy produção** → **Run workflow** → branch `master`.
2. O run tem de ficar verde.
3. Confirme o SHA no log (`HEAD …`) e `https://www.ibsantaleopoldina.com.br/healthz/` → `{"status":"ok"}`.

A partir daí, **cada push/merge em `master` publica sozinho**. Não é preciso SSH.

## Fallback sem o state do Terraform

Na mesma conta (`354354997468`), profile `default`. Role da VM: `ib-conecta-prod-ec2`.

```bash
aws iam attach-role-policy \
  --role-name ib-conecta-prod-ec2 \
  --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore

# Se ainda não existir o provider OIDC do GitHub nesta conta:
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

A role `ib-conecta-prod-github-deploy` (trust `repo:marquesjr/ib-conecta:ref:refs/heads/master` + `aud=sts.amazonaws.com`, permissões SSM/EC2 Describe) é a do arquivo `infra/aws/deploy.tf`. Prefira `terraform apply`; o fallback CLI completo é copiar o JSON gerado por `terraform show` depois do apply numa máquina que tenha o state.

Não crie access keys de IAM user para o GitHub.

## O que **não** entra em GitHub Secrets

| Item | Onde fica |
|---|---|
| `.env.prod` (Django, Postgres, Let's Encrypt) | Só na VM, gitignored |
| Chave SSH da EC2 | Só no laptop do operador; a Action **não** SSH |
| Access keys AWS | Não usar; a Action assume role por OIDC |

Não é necessário secret `PROD_SSH_KEY` nem runner `self-hosted`.

## Como conferir o próximo merge

1. Merge (ou push) em `master`.
2. Actions → **Deploy produção** deve iniciar em segundos no SHA do merge.
3. Concurrency `production-deploy`: um deploy por vez; o seguinte espera (não cancela rebuild).
4. Site: `https://www.ibsantaleopoldina.com.br/healthz/` e a mudança do PR (ex.: página nova).
5. Se falhar: logs da Action (stdout/stderr do SSM, truncados em ~24 KB). SSH só para diagnóstico, não para publicar:

   ```bash
   cd /home/ubuntu/ib-conecta
   git log -1 --oneline
   docker compose -f docker-compose.prod.yml --env-file .env.prod ps
   docker compose -f docker-compose.prod.yml --env-file .env.prod logs --tail=150 web caddy db
   ```

   Publicação manual de emergência (mesmo script da Action):

   ```bash
   bash scripts/deploy-prod.sh
   ```

## Arquivos

- `.github/workflows/deploy.yml` — verify + deploy
- `scripts/deploy-prod.sh` — git + compose na VM
- `scripts/deploy-prod-ssm.sh` — SSM a partir do runner hospedado
- `scripts/install-ssm-agent.sh` — agente na Ubuntu ARM
- `infra/aws/deploy.tf` — OIDC, role, policy SSM na EC2
- ADR `docs/adr/0012-deploy-on-push-to-master.md`
