# Infra AWS como Terraform em infra/aws

A infraestrutura de produção é código Terraform em `infra/aws/` (provider `hashicorp/aws`): rede pública mínima, security group, EC2 `t4g.small`, Elastic IP, bucket S3 de backup e IAM instance profile para esse bucket — sem access keys no `.env`. `infra/oci/` é removido do repositório. State continua local e fora do git, como na stack OCI. Clique no console não é o procedimento de criação.
