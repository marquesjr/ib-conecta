variable "region" {
  description = "Região OCI (ex.: sa-saopaulo-1 para São Paulo)."
  type        = string
  default     = "sa-saopaulo-1"
}

variable "oci_config_profile" {
  description = "Profile em ~/.oci/config usado pelo provider OCI."
  type        = string
  default     = "ib_conecta"
}

variable "tenancy_ocid" {
  description = "OCID do tenancy OCI."
  type        = string
}

variable "compartment_ocid" {
  description = "OCID do compartment onde os recursos serão criados."
  type        = string
}

variable "project_name" {
  description = "Nome base do projeto, usado em tags e nomes de recursos."
  type        = string
  default     = "ib-conecta"
}

variable "environment" {
  description = "Ambiente lógico (ex.: prod, staging)."
  type        = string
  default     = "prod"
}

variable "tags" {
  description = "Tags freeform aplicadas aos recursos."
  type        = map(string)
  default = {
    project     = "ib-conecta"
    managed_by  = "terraform"
    environment = "prod"
  }
}

variable "vcn_cidr" {
  description = "CIDR da VCN."
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR da subnet pública."
  type        = string
  default     = "10.0.0.0/24"
}

variable "instance_display_name" {
  description = "Nome de exibição da instância compute."
  type        = string
  default     = "ib-conecta-app"
}

variable "instance_shape" {
  description = "Shape da VM (Always Free Ampere: VM.Standard.A1.Flex)."
  type        = string
  default     = "VM.Standard.A1.Flex"
}

variable "instance_ocpus" {
  description = "OCPUs da instância A1 Flex (Always Free: até 4 OCPUs no total da conta)."
  type        = number
  default     = 2

  validation {
    condition     = var.instance_ocpus >= 1 && var.instance_ocpus <= 4
    error_message = "instance_ocpus deve ficar entre 1 e 4 para o tier Always Free A1."
  }
}

variable "instance_memory_gbs" {
  description = "Memória em GB da instância A1 Flex (Always Free: até 24 GB no total da conta)."
  type        = number
  default     = 12

  validation {
    condition     = var.instance_memory_gbs >= 6 && var.instance_memory_gbs <= 24
    error_message = "instance_memory_gbs deve ficar entre 6 e 24 para o tier Always Free A1."
  }
}

variable "boot_volume_size_gbs" {
  description = "Tamanho do boot volume em GB (Always Free: até 200 GB total de boot+block por instância A1)."
  type        = number
  default     = 50

  validation {
    condition     = var.boot_volume_size_gbs >= 47 && var.boot_volume_size_gbs <= 200
    error_message = "boot_volume_size_gbs deve ficar entre 47 e 200."
  }
}

variable "availability_domain" {
  description = "Availability Domain (ex.: AD-1). Deixe vazio para usar o primeiro AD disponível."
  type        = string
  default     = ""
}

variable "operating_system" {
  description = "Sistema operacional da imagem de boot."
  type        = string
  default     = "Canonical Ubuntu"
}

variable "operating_system_version" {
  description = "Versão do sistema operacional da imagem de boot."
  type        = string
  default     = "22.04"
}

variable "ssh_public_key" {
  description = "Chave pública SSH para acesso à VM (formato OpenSSH, uma linha)."
  type        = string
  sensitive   = true
}

variable "ssh_allowed_cidrs" {
  description = "CIDRs autorizados para SSH (porta 22). Não use 0.0.0.0/0 em produção."
  type        = list(string)

  validation {
    condition     = length(var.ssh_allowed_cidrs) > 0
    error_message = "Informe ao menos um CIDR em ssh_allowed_cidrs."
  }
}

variable "object_storage_bucket_name" {
  description = "Nome do bucket Object Storage (único no namespace). Deixe vazio para gerar automaticamente."
  type        = string
  default     = ""
}

variable "object_storage_versioning" {
  description = "Habilitar versionamento no bucket Object Storage."
  type        = string
  default     = "Enabled"

  validation {
    condition     = contains(["Enabled", "Disabled"], var.object_storage_versioning)
    error_message = "object_storage_versioning deve ser Enabled ou Disabled."
  }
}
