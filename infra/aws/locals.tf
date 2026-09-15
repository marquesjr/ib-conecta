locals {
  name_prefix = "${var.project_name}-${var.environment}"

  availability_zone = var.availability_zone != "" ? var.availability_zone : sort(data.aws_ec2_instance_type_offerings.app.locations)[0]

  backup_bucket_name = var.backup_bucket_name != "" ? var.backup_bucket_name : "${local.name_prefix}-backups-${data.aws_caller_identity.current.account_id}"
}
