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
