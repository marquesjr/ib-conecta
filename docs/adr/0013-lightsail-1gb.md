# Produção no Lightsail de 1 GB

A partir de 16/11/2026 a conta passou a ser paga. Com a EC2 `t4g.small` ligada 24 horas, o custo ficava em cerca de US$ 18/mês: ~12 da instância, ~2,4 do EBS e ~3,7 do IPv4. A VM de produção passa a ser uma instância **Lightsail** `micro_3_0` (1 GB de RAM, 2 vCPU, 40 GB de SSD, IPv4 incluso, cerca de US$ 7/mês) em `us-east-2a`. Na medição de 16/11, web + db + Caddy usavam ~580 MB. O `user_data` cria 2 GB de swap, e o Gunicorn roda com 1 worker de 2 threads.

O que continua igual: Compose + Caddy + Postgres na VM (ADRs 0004 e 0006), o bucket S3 de backups com age (ADRs 0005 e 0010), Terraform em `infra/aws/` com o mesmo state (ADR 0007) e o deploy por OIDC + SSM em push para `master` (ADR 0012).

O que muda:

- **Rede:** saem VPC, security group e Elastic IP. Entram o firewall da própria instância (80/443 abertos e 22 só nos CIDRs do operador) e um IP estático do Lightsail, que não é cobrado enquanto está anexado.
- **SSM:** o Lightsail não aceita instance profile. A VM entra no SSM como *managed instance* híbrida (`mi-…`), por meio de uma activation do Terraform com service role `AmazonSSMManagedInstanceCore`. O tier padrão do SSM não cobra nada. A role de deploy só pode chamar `SendCommand` em managed instances com a tag `Name=ib-conecta-prod-app`.
- **Backup:** sem instance profile, a VM usa a access key de um IAM user (`ib-conecta-prod-backup`) que só alcança o bucket. A chave é criada à mão, para não ir parar no state, e fica no `.env.backup` com `chmod 600`.
- **Arquitetura:** o Lightsail é x86_64, então os scripts escolhem o binário pela arquitetura.
- **Budget:** o teto cai para US$ 12, com alerta em 80%.

Opções recusadas:

- `t4g.micro` com swap (~US$ 12,4) mantém EBS e IPv4 cobrados à parte e economiza metade do que o Lightsail economiza.
- Lightsail de 2 GB (~US$ 12) quase empata com a `t4g.micro`.
- Deploy por SSH a partir do Actions exigiria abrir a porta 22 para os IPs do GitHub e guardar a chave privada como secret de um repositório público.
- O object storage do Lightsail perderia o versionamento e o lifecycle do bucket atual.

Substitui a ADR 0003 e o valor da ADR 0008. Na ADR 0006, troca Elastic IP por IP estático. Migração: `docs/ops/migracao-lightsail.md`.
