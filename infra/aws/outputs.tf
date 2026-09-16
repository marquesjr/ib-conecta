output "region" {
  description = "Região AWS provisionada."
  value       = var.region
}

output "availability_zone" {
  description = "Availability Zone da VM."
  value       = local.availability_zone
}

output "vpc_id" {
  description = "ID da VPC."
  value       = aws_vpc.app.id
}

output "instance_id" {
  description = "ID da instância EC2."
  value       = aws_instance.app.id
}

output "instance_private_ip" {
  description = "IP privado da instância."
  value       = aws_instance.app.private_ip
}

output "instance_public_ip" {
  description = "Elastic IP da VM (usar no DNS www)."
  value       = aws_eip.app.public_ip
}

output "backup_bucket_name" {
  description = "Bucket S3 privado para backups criptografados."
  value       = aws_s3_bucket.backups.bucket
}

output "ssh_command" {
  description = "Comando SSH sugerido (usuário ubuntu, chave local)."
  value       = "ssh -i ~/.ssh/id_ed25519_ib_conecta ubuntu@${aws_eip.app.public_ip}"
}

output "github_actions_deploy_role_arn" {
  description = "Role assumida pelo workflow Deploy produção (OIDC). Override: variável AWS_DEPLOY_ROLE_ARN."
  value       = aws_iam_role.github_deploy.arn
}

output "github_oidc_provider_arn" {
  description = "Provider OIDC do GitHub Actions nesta conta."
  value       = aws_iam_openid_connect_provider.github.arn
}
