# Infraestrutura OCI — IB Conecta

Stack Terraform para o ambiente **Always Free** da Oracle Cloud Infrastructure (OCI), cobrindo:

- VCN com subnet pública, Internet Gateway e security lists (HTTP/HTTPS abertos, SSH restrito)
- VM **Ampere A1 Flex** (`VM.Standard.A1.Flex`) com IP público reservado
- Bucket **Object Storage** privado para mídia e backups

Relacionado à issue [#32](https://github.com/marquesjr/ib-conecta/issues/32) (épico [#17](https://github.com/marquesjr/ib-conecta/issues/17)).

## Pré-requisitos

- [Terraform](https://developer.hashicorp.com/terraform/downloads) >= 1.5
- Conta OCI com tier Always Free habilitado
- [OCI CLI](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm) configurado (recomendado) ou variáveis de ambiente equivalentes
- API key de usuário com permissão para criar recursos no compartment alvo
- Chave pública SSH para acesso à VM

## Autenticação

O provider `oracle/oci` lê credenciais do arquivo padrão `~/.oci/config`. O profile padrão da stack é `ib_conecta` (`oci_config_profile`). Alternativa: variáveis de ambiente:

```bash
export OCI_CLI_USER="<user-ocid>"
export OCI_CLI_TENANCY="<tenancy-ocid>"
export OCI_CLI_FINGERPRINT="<api-key-fingerprint>"
export OCI_CLI_KEY_FILE="$HOME/.oci/oci_api_key.pem"
export OCI_CLI_REGION="sa-saopaulo-1"
```

Alternativa: defina `TF_VAR_*` para variáveis do Terraform (veja `terraform.tfvars.example`).

## Bootstrap

```bash
cd infra/oci
cp terraform.tfvars.example terraform.tfvars
# Edite terraform.tfvars com OCIDs, chave SSH e CIDRs permitidos para SSH

terraform init
terraform fmt -recursive
terraform validate
terraform plan
terraform apply
```

Após o `apply`, anote os outputs:

```bash
terraform output instance_public_ip
terraform output object_storage_bucket_name
```

Use o IP público na issue [#35 — DNS e domínio canônico](https://github.com/marquesjr/ib-conecta/issues/35).

## Variáveis principais

| Variável | Descrição |
|----------|-----------|
| `region` | Região OCI (padrão: `sa-saopaulo-1`) |
| `oci_config_profile` | Profile em `~/.oci/config` (padrão: `ib_conecta`) |
| `tenancy_ocid` | OCID do tenancy |
| `compartment_ocid` | OCID do compartment |
| `instance_shape` | Shape da VM (padrão: `VM.Standard.A1.Flex`) |
| `instance_ocpus` / `instance_memory_gbs` | Recursos A1 Flex (padrão: 2 OCPU / 12 GB) |
| `ssh_public_key` | Chave pública SSH (OpenSSH) |
| `ssh_allowed_cidrs` | Lista de CIDRs autorizados na porta 22 |
| `tags` | Tags freeform nos recursos |

Consulte `variables.tf` para a lista completa.

## Always Free — limites relevantes

- **Compute A1 Flex:** até 4 OCPUs e 24 GB RAM no total da conta (esta stack usa 2/12 por padrão)
- **Boot volume:** até 200 GB por instância A1
- **Object Storage:** 20 GB gratuitos (standard tier); ajuste retenção de backups conforme necessidade

Se o `apply` falhar por capacidade A1 na região/AD, tente outro Availability Domain em `availability_domain` ou outra região compatível com Always Free.

## Destroy

```bash
terraform destroy
```

Isso remove VCN, instância, IP reservado e bucket (bucket deve estar vazio ou o destroy pode falhar — esvazie objetos antes se necessário).

## Estrutura

```
infra/oci/
  versions.tf          # Versões Terraform/provider
  variables.tf         # Entrada configurável
  locals.tf            # Nomes/tags derivados
  main.tf              # Provider e data sources
  network.tf           # VCN, subnet, firewall
  compute.tf           # VM Ampere A1 + IP reservado
  object_storage.tf    # Bucket privado
  outputs.tf           # IP, OCIDs, bucket
  terraform.tfvars.example
```

## Próximos passos

- [#34 — Stack de produção (Docker Compose + Caddy)](https://github.com/marquesjr/ib-conecta/issues/34): deploy da aplicação na VM provisionada aqui
- [#35 — DNS](https://github.com/marquesjr/ib-conecta/issues/35): apontar `www.ibsantaleopoldina.com.br` para `instance_public_ip`
