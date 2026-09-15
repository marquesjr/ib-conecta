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

variable "vpc_cidr" {
  description = "CIDR da VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR da subnet pública."
  type        = string
  default     = "10.0.0.0/24"
}

variable "availability_zone" {
  description = "AZ da subnet/VM. Vazio = primeira AZ com o instance_type."
  type        = string
  default     = ""
}

variable "instance_type" {
  description = "Tipo da EC2 (ADR 0003: t4g.small)."
  type        = string
  default     = "t4g.small"
}

variable "boot_volume_size_gbs" {
  description = "Tamanho do volume raiz gp3, em GB."
  type        = number
  default     = 30

  validation {
    condition     = var.boot_volume_size_gbs >= 8 && var.boot_volume_size_gbs <= 50
    error_message = "boot_volume_size_gbs deve ficar entre 8 e 50 para o teto baixo de custo."
  }
}

variable "ssh_public_key" {
  description = "Chave pública SSH (OpenSSH, uma linha)."
  type        = string
  sensitive   = true
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

variable "budget_alert_email" {
  description = "E-mail do alerta de 80% do budget de US$ 20 (ADR 0008)."
  type        = string
}

variable "enable_budget" {
  description = "Criar o AWS Budget. Desligue se o IAM não tiver permissão budgets:*."
  type        = bool
  default     = true
}
