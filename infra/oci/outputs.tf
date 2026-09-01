output "region" {
  description = "Região OCI provisionada."
  value       = var.region
}

output "vcn_id" {
  description = "OCID da VCN."
  value       = oci_core_vcn.app.id
}

output "public_subnet_id" {
  description = "OCID da subnet pública."
  value       = oci_core_subnet.public.id
}

output "instance_id" {
  description = "OCID da instância compute."
  value       = oci_core_instance.app.id
}

output "instance_private_ip" {
  description = "IP privado da instância."
  value       = data.oci_core_private_ips.app.private_ips[0].ip_address
}

output "instance_public_ip" {
  description = "IP público reservado da VM (usar no DNS www)."
  value       = oci_core_public_ip.app.ip_address
}

output "public_ip_id" {
  description = "OCID do IP público reservado."
  value       = oci_core_public_ip.app.id
}

output "object_storage_namespace" {
  description = "Namespace Object Storage do tenancy."
  value       = data.oci_objectstorage_namespace.app.namespace
}

output "object_storage_bucket_name" {
  description = "Nome do bucket Object Storage para mídia e backups."
  value       = oci_objectstorage_bucket.app.name
}

output "object_storage_bucket_id" {
  description = "OCID do bucket Object Storage."
  value       = oci_objectstorage_bucket.app.id
}

output "availability_domain" {
  description = "Availability Domain usado pela instância."
  value       = local.availability_domain
}

output "ssh_command" {
  description = "Comando SSH sugerido (ajuste o usuário conforme a imagem)."
  value       = "ssh ubuntu@${oci_core_public_ip.app.ip_address}"
}
