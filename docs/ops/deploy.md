# Deploy produção ao fazer push em master (issue #17)

O portal em `https://www.ibsantaleopoldina.com.br` **não** se atualiza só com o merge. Quem publica é o workflow **Deploy produção**. Um push em `master` (ou *Run workflow*) faz o seguinte:

1. Assume uma role IAM por OIDC.
2. Manda um SSM Run Command para a VM do Lightsail.
3. A VM roda o mesmo `git` + `docker compose` documentado no README.

O deploy não abre a porta 22 para o GitHub, não usa runner self-hosted (o repositório é público) e não grava access key da AWS no GitHub.

A VM do Lightsail não tem instance profile. Por isso ela entra no SSM como **managed instance híbrida** (ID `mi-…`), registrada uma única vez com uma activation (ADR 0013).

## O que o pipeline faz

1. Job `verify`: roda `bash -n` nos scripts e as asserções de `scripts/test-deploy-scripts.sh`. Também roda em pull request.
2. Job `deploy`: só em `push`/`workflow_dispatch` em `master`.
   - Assume a role `ib-conecta-prod-github-deploy` por OIDC.
   - Localiza a managed instance **Online** com `Name=ib-conecta-prod-app` (`ssm describe-instance-information`).
   - Pelo SSM, faz `git fetch` + `checkout` do SHA do push e roda `scripts/deploy-prod.sh`.
   - O script roda `docker compose -f docker-compose.prod.yml --env-file .env.prod up --build -d --wait`.
   - Por fim, faz a checagem externa com `python scripts/check-uptime.py` (a mesma do monitoramento).

O rebuild **é obrigatório**, porque a imagem Docker de produção não faz bind-mount do código.

## Passos únicos (operador com AWS + SSH)

Faça estes passos **uma vez** por VM. Sem eles a Action falha. Se for a migração a partir da EC2, siga [`migracao-lightsail.md`](migracao-lightsail.md), que já inclui estes passos na ordem certa.

### 1. IAM + OIDC + activation (Terraform, na máquina que tem o state)

```bash
cd infra/aws
terraform init
terraform apply
terraform output github_actions_deploy_role_arn
terraform output ssm_activation_id
terraform output -raw ssm_activation_code   # segredo: não cole em issue/PR
```

A trust policy aceita **somente** o `sub` imutável deste repositório, criado em 27/07/2026 (depois do corte do GitHub de 15/07/2026):

`repo:marquesjr@2216233/ib-conecta@1314311915:ref:refs/heads/master`

O formato antigo, `repo:marquesjr/ib-conecta:ref:refs/heads/master`, **não** casa com o token. O sintoma é `Could not assume role with OIDC: Not authorized to perform sts:AssumeRoleWithWebIdentity`.

Por padrão, a Action usa `arn:aws:iam::354354997468:role/ib-conecta-prod-github-deploy`. Se o apply imprimir outro ARN, grave-o em GitHub → Settings → Secrets and variables → Actions → **Variables** → `AWS_DEPLOY_ROLE_ARN`.

A activation vale **24 horas** e registra **uma** VM. Se ela vencer ou a VM for recriada:

```bash
terraform apply -replace=aws_ssm_activation.app
```

### 2. Registrar a VM no SSM (SSH uma vez)

As imagens Ubuntu da AWS trazem o agente pelo snap (`amazon-ssm-agent` classic). Nesse caso a unit systemd é `snap.amazon-ssm-agent.amazon-ssm-agent`, e não `amazon-ssm-agent`. Instalar o `.deb` por cima falha, porque o preinst do dpkg recusa. `scripts/install-ssm-agent.sh` detecta o snap, **pula o .deb**, registra a VM com a activation e sobe a unit.

```bash
ssh -i ~/.ssh/id_ed25519_ib_conecta ubuntu@<IP estático>
cd /home/ubuntu/ib-conecta
sudo SSM_ACTIVATION_ID='<id>' SSM_ACTIVATION_CODE='<code>' scripts/install-ssm-agent.sh
```

O script imprime `registro híbrido: {"ManagedInstanceID":"mi-…",…}` e `OK snap.amazon-ssm-agent.amazon-ssm-agent.service` (ou `amazon-ssm-agent.service`, quando a imagem não tem o snap).

Do laptop (profile `default`, região `us-east-2`), confira se o nó está `Online` e se tem a tag `Name`. A role de deploy só alcança nós com `Name=ib-conecta-prod-app`. A activation já aplica essa tag, mas o `add-tags-to-resource` abaixo pode ser repetido sem efeito colateral:

```bash
aws ssm describe-instance-information \
  --region us-east-2 \
  --query 'InstanceInformationList[].{Id:InstanceId,Name:Name,Ping:PingStatus,Ip:IPAddress}' \
  --output table

aws ssm add-tags-to-resource --region us-east-2 \
  --resource-type ManagedInstance --resource-id mi-XXXXXXXXXXXXXXXXX \
  --tags Key=Name,Value=ib-conecta-prod-app
```

Se sobrar um nó antigo com o mesmo `Name` (VM recriada), ele aparece como `ConnectionLost` e o deploy o ignora. Mesmo assim, remova-o:

```bash
aws ssm deregister-managed-instance --region us-east-2 --instance-id mi-ANTIGO
```

### 3. Disparar o primeiro deploy

1. GitHub → Actions → **Deploy produção** → **Run workflow** → branch `master`.
2. O run tem de ficar verde.
3. Confirme o SHA no log (`HEAD …`) e que `https://www.ibsantaleopoldina.com.br/healthz/` responde `{"status":"ok"}`.

A partir daí, **cada push/merge em `master` publica sozinho**, sem SSH.

## O que **não** entra em GitHub Secrets

| Item | Onde fica |
|---|---|
| `.env.prod` (Django, Postgres, Let's Encrypt) | Só na VM, gitignored |
| `.env.backup` (access key do IAM user de backup) | Só na VM, `chmod 600` |
| Chave SSH da VM | Só no laptop do operador, porque a Action **não** usa SSH |
| Código da activation SSM | Só no state do Terraform. Usado uma vez no registro |

Não é necessário secret `PROD_SSH_KEY` nem runner `self-hosted`.

## Como conferir o próximo merge

1. Faça merge (ou push) em `master`.
2. Em Actions, o **Deploy produção** deve iniciar em segundos no SHA do merge.
3. A concurrency `production-deploy` roda um deploy por vez. O seguinte espera, sem cancelar o rebuild.
4. No site, confira `https://www.ibsantaleopoldina.com.br/healthz/` e a mudança do PR.
5. Se falhar, veja os logs da Action (stdout/stderr do SSM, truncados em ~24 KB). Use SSH só para diagnóstico, não para publicar:

   ```bash
   cd /home/ubuntu/ib-conecta
   git log -1 --oneline
   free -m
   docker compose -f docker-compose.prod.yml --env-file .env.prod ps
   docker compose -f docker-compose.prod.yml --env-file .env.prod logs --tail=150 web caddy db
   ```

   Para uma publicação manual de emergência (o mesmo script da Action):

   ```bash
   bash scripts/deploy-prod.sh
   ```

## Arquivos

- `.github/workflows/deploy.yml`: verify + deploy.
- `scripts/deploy-prod.sh`: git + compose na VM.
- `scripts/deploy-prod-ssm.sh`: SSM a partir do runner hospedado.
- `scripts/install-ssm-agent.sh`: agente e registro híbrido na VM.
- `infra/aws/deploy.tf`: OIDC, role de deploy, activation e service role do SSM.
- ADRs `docs/adr/0012-deploy-on-push-to-master.md` e `docs/adr/0013-lightsail-1gb.md`.
