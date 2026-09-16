# Deploy a partir do GitHub Actions (ADR 0012). Sem access keys no GitHub.

resource "aws_iam_role_policy_attachment" "ssm_core" {
  role       = aws_iam_role.app.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]

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

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${var.github_repository}:ref:refs/heads/master"]
    }
  }
}

resource "aws_iam_role" "github_deploy" {
  name               = "${local.name_prefix}-github-deploy"
  assume_role_policy = data.aws_iam_policy_document.github_deploy_assume.json
}

data "aws_iam_policy_document" "github_deploy" {
  statement {
    sid = "FindInstance"
    actions = [
      "ec2:DescribeInstances",
    ]
    resources = ["*"]
  }

  statement {
    sid = "SsmInventory"
    actions = [
      "ssm:DescribeInstanceInformation",
      "ssm:GetCommandInvocation",
    ]
    resources = ["*"]
  }

  statement {
    sid = "SsmRunShellOnApp"
    actions = [
      "ssm:SendCommand",
    ]
    resources = [
      "arn:aws:ssm:${var.region}::document/AWS-RunShellScript",
      "arn:aws:ec2:${var.region}:${data.aws_caller_identity.current.account_id}:instance/${aws_instance.app.id}",
    ]
  }
}

resource "aws_iam_role_policy" "github_deploy" {
  name   = "ssm-deploy"
  role   = aws_iam_role.github_deploy.id
  policy = data.aws_iam_policy_document.github_deploy.json
}
