# VM de produção no Lightsail (ADR 0013). Substitui EC2 + VPC + Elastic IP.
# O preço do bundle inclui IPv4 público, 40 GB de SSD e transferência.

resource "aws_lightsail_key_pair" "app" {
  name       = "${local.name_prefix}-ssh"
  public_key = var.ssh_public_key
}

resource "aws_lightsail_instance" "app" {
  name              = local.app_name
  availability_zone = local.availability_zone
  blueprint_id      = var.lightsail_blueprint_id
  bundle_id         = var.lightsail_bundle_id
  key_pair_name     = aws_lightsail_key_pair.app.name
  ip_address_type   = "ipv4"
  user_data         = file("${path.module}/user_data.sh")

  tags = {
    Name = local.app_name
  }

  # Mudar user_data ou blueprint recriaria a VM (e apagaria os volumes Docker).
  lifecycle {
    ignore_changes = [user_data, blueprint_id]
  }
}

resource "aws_lightsail_static_ip" "app" {
  name = "${local.name_prefix}-ip"
}

resource "aws_lightsail_static_ip_attachment" "app" {
  static_ip_name = aws_lightsail_static_ip.app.name
  instance_name  = aws_lightsail_instance.app.name
}

# Substitui todas as regras do firewall da instância (o default do Lightsail abre 22 para o mundo).
resource "aws_lightsail_instance_public_ports" "app" {
  instance_name = aws_lightsail_instance.app.name

  port_info {
    protocol  = "tcp"
    from_port = 80
    to_port   = 80
    cidrs     = ["0.0.0.0/0"]
  }

  port_info {
    protocol  = "tcp"
    from_port = 443
    to_port   = 443
    cidrs     = ["0.0.0.0/0"]
  }

  # HTTP/3 do Caddy.
  port_info {
    protocol  = "udp"
    from_port = 443
    to_port   = 443
    cidrs     = ["0.0.0.0/0"]
  }

  port_info {
    protocol  = "tcp"
    from_port = 22
    to_port   = 22
    cidrs     = var.ssh_allowed_cidrs
  }
}
