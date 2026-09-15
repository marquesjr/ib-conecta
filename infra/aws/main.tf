provider "aws" {
  region  = var.region
  profile = var.aws_profile

  default_tags {
    tags = merge(var.tags, {
      project     = var.project_name
      environment = var.environment
      managed_by  = "terraform"
    })
  }
}

data "aws_caller_identity" "current" {}

data "aws_ec2_instance_type_offerings" "app" {
  filter {
    name   = "instance-type"
    values = [var.instance_type]
  }

  location_type = "availability-zone"
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-arm64-server-*"]
  }

  filter {
    name   = "architecture"
    values = ["arm64"]
  }

  filter {
    name   = "state"
    values = ["available"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}
