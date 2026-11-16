# Deploy a partir do GitHub Actions (ADR 0012, ADR 0013). Sem access keys no GitHub.
# A VM do Lightsail entra no SSM como managed instance híbrida (mi-...), registrada
# uma vez com a activation abaixo (scripts/install-ssm-agent.sh). Tier padrão: sem custo.

locals {
  github_oidc_sub_master = "${var.github_oidc_sub_prefix}:ref:refs/heads/master"
}

# --- Registro híbrido da VM no SSM ---

data "aws_iam_policy_document" "ssm_hybrid_assume" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ssm.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [data.aws_caller_identity.current.account_id]
    }
  }
}

resource "aws_iam_role" "ssm_hybrid" {
  name               = "${local.name_prefix}-ssm-hybrid"
  assume_role_policy = data.aws_iam_policy_document.ssm_hybrid_assume.json
}

resource "aws_iam_role_policy_attachment" "ssm_hybrid_core" {
  role       = aws_iam_role.ssm_hybrid.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# Vale 24 h e registra uma VM só. Para registrar de novo (VM recriada ou activation vencida):
#   terraform apply -replace=aws_ssm_activation.app
resource "aws_ssm_activation" "app" {
  name               = local.app_name
  description        = "Registro da VM Lightsail ${local.app_name} no SSM"
  iam_role           = aws_iam_role.ssm_hybrid.name
  registration_limit = 1

  tags = {
    Name = local.app_name
  }

  depends_on = [aws_iam_role_policy_attachment.ssm_hybrid_core]
}

# --- Role assumida pelo workflow Deploy produção ---

# AWS valida o GitHub OIDC por CA confiável; o thumbprint só satisfaz o schema do provider.
resource "aws_iam_openid_connect_provider" "github" {
  url            = "https://token.actions.githubusercontent.com"
  client_id_list = ["sts.amazonaws.com"]
  thumbprint_list = [
    "6938fd4d98bab03faadb97b34396831e3780aea1",
    "1c58a3a8518e8759bf075b76b750d4f2df264fcd",
  ]

  tags = {
    Name = "${local.name_prefix}-github-oidc"
  }
}

data "aws_iam_policy_document" "github_deploy_assume" {
  statement {
    sid     = "GitHubActionsMaster"
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    # Repositório criado em 2026-07-27: GitHub emite sub imutável (owner@id/repo@id),
    # não repo:marquesjr/ib-conecta:ref:refs/heads/master.
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      values   = [local.github_oidc_sub_master]
    }
  }
}

resource "aws_iam_role" "github_deploy" {
  name               = "${local.name_prefix}-github-deploy"
  assume_role_policy = data.aws_iam_policy_document.github_deploy_assume.json
}

data "aws_iam_policy_document" "github_deploy" {
  statement {
    sid = "SsmInventory"
    actions = [
      "ssm:DescribeInstanceInformation",
      "ssm:GetCommandInvocation",
    ]
    resources = ["*"]
  }

  statement {
    sid       = "SsmRunShellDocument"
    actions   = ["ssm:SendCommand"]
    resources = ["arn:aws:ssm:${var.region}::document/AWS-RunShellScript"]
  }

  # O id mi-... só existe depois do registro; a tag Name restringe o alvo à VM do portal.
  statement {
    sid       = "SsmRunShellOnApp"
    actions   = ["ssm:SendCommand"]
    resources = ["arn:aws:ssm:${var.region}:${data.aws_caller_identity.current.account_id}:managed-instance/*"]

    condition {
      test     = "StringEquals"
      variable = "ssm:resourceTag/Name"
      values   = [local.app_name]
    }
  }
}

resource "aws_iam_role_policy" "github_deploy" {
  name   = "ssm-deploy"
  role   = aws_iam_role.github_deploy.id
  policy = data.aws_iam_policy_document.github_deploy.json
}
