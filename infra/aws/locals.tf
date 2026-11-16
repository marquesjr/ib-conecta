locals {
  name_prefix = "${var.project_name}-${var.environment}"

  # Nome da VM no Lightsail e do managed instance no SSM (o deploy procura por ele).
  app_name = "${local.name_prefix}-app"

  availability_zone = var.availability_zone != "" ? var.availability_zone : "${var.region}a"

  backup_bucket_name = var.backup_bucket_name != "" ? var.backup_bucket_name : "${local.name_prefix}-backups-${data.aws_caller_identity.current.account_id}"
}
