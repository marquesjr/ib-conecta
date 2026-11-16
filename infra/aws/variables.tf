variable "aws_profile" {
  description = "Profile em ~/.aws/config. O padrão é o usuário IAM cursor (não a root)."
  type        = string
  default     = "default"
}

variable "region" {
  description = "Região AWS da produção (ADR 0002)."
  type        = string
  default     = "us-east-2"
}

variable "project_name" {
  description = "Nome base do projeto, usado em tags e nomes de recursos."
  type        = string
  default     = "ib-conecta"
}

variable "environment" {
  description = "Ambiente lógico (ex.: prod)."
  type        = string
  default     = "prod"
}

variable "tags" {
  description = "Tags extras aplicadas aos recursos."
  type        = map(string)
  default = {
    owner = "igreja-batista-santa-leopoldina"
  }
}

variable "availability_zone" {
  description = "AZ do Lightsail. Vazio = <region>a."
  type        = string
  default     = ""
}

variable "lightsail_bundle_id" {
  description = "Plano do Lightsail (ADR 0013: 1 GB). IDs em: aws lightsail get-bundles."
  type        = string
  default     = "micro_3_0"
}

variable "lightsail_blueprint_id" {
  description = "Imagem do Lightsail. IDs em: aws lightsail get-blueprints."
  type        = string
  default     = "ubuntu_24_04"
}

variable "ssh_public_key" {
  description = "Chave pública SSH (OpenSSH, uma linha)."
  type        = string
  sensitive   = true
}

variable "github_repository" {
  description = "org/name cujo workflow em master pode assumir a role de deploy (ADR 0012)."
  type        = string
  default     = "marquesjr/ib-conecta"
}

variable "github_oidc_sub_prefix" {
  description = "Prefixo do claim sub do GitHub Actions OIDC (Settings → Actions → OIDC, ou GET .../actions/oidc/customization/sub). Repos criados após 15/07/2026 incluem owner_id e repo_id."
  type        = string
  default     = "repo:marquesjr@2216233/ib-conecta@1314311915"
}

variable "ssh_allowed_cidrs" {
  description = "CIDRs autorizados na porta 22. Não use 0.0.0.0/0."
  type        = list(string)

  validation {
    condition     = length(var.ssh_allowed_cidrs) > 0
    error_message = "Informe ao menos um CIDR em ssh_allowed_cidrs."
  }
}

variable "backup_bucket_name" {
  description = "Nome fixo do bucket S3 de backups. Vazio = ib-conecta-prod-backups-<account_id>."
  type        = string
  default     = ""
}

variable "budget_limit_usd" {
  description = "Teto mensal do AWS Budget, em US$ (ADR 0013)."
  type        = number
  default     = 12
}

variable "budget_alert_email" {
  description = "E-mail do alerta de 80% do budget."
  type        = string
}

variable "enable_budget" {
  description = "Criar o AWS Budget. Desligue se o IAM não tiver permissão budgets:*."
  type        = bool
  default     = true
}
