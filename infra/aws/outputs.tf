output "region" {
  description = "Região AWS provisionada."
  value       = var.region
}

output "availability_zone" {
  description = "Availability Zone da VM."
  value       = local.availability_zone
}

output "instance_name" {
  description = "Nome da instância Lightsail (e do managed instance no SSM)."
  value       = aws_lightsail_instance.app.name
}

output "instance_public_ip" {
  description = "IP estático da VM (usar nos registros A do DNS)."
  value       = aws_lightsail_static_ip.app.ip_address
}

output "backup_bucket_name" {
  description = "Bucket S3 privado para backups criptografados."
  value       = aws_s3_bucket.backups.bucket
}

output "backup_iam_user" {
  description = "IAM user cujas access keys vão no .env.backup da VM."
  value       = aws_iam_user.backup.name
}

output "ssh_command" {
  description = "Comando SSH sugerido (usuário ubuntu, chave local)."
  value       = "ssh -i ~/.ssh/id_ed25519_ib_conecta ubuntu@${aws_lightsail_static_ip.app.ip_address}"
}

output "ssm_activation_id" {
  description = "ID da activation híbrida do SSM (scripts/install-ssm-agent.sh)."
  value       = aws_ssm_activation.app.id
}

output "ssm_activation_code" {
  description = "Código da activation híbrida. Leia com: terraform output -raw ssm_activation_code"
  value       = aws_ssm_activation.app.activation_code
  sensitive   = true
}

output "github_actions_deploy_role_arn" {
  description = "Role assumida pelo workflow Deploy produção (OIDC). Override: variável AWS_DEPLOY_ROLE_ARN."
  value       = aws_iam_role.github_deploy.arn
}

output "github_oidc_provider_arn" {
  description = "Provider OIDC do GitHub Actions nesta conta."
  value       = aws_iam_openid_connect_provider.github.arn
}

output "github_oidc_sub_master" {
  description = "Claim sub que a trust policy da role de deploy aceita (push e workflow_dispatch em master)."
  value       = local.github_oidc_sub_master
}
