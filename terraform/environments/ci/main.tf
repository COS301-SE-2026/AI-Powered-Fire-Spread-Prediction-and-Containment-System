terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  backend "s3" {
    bucket       = "fireaway-terraform-state-856820204904"
    key          = "ci/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
    encrypt = true
  }
}

provider "aws" {
  region = "us-east-1"
}

data "aws_caller_identity" "current" {}

locals {
  account        = data.aws_caller_identity.current.account_id
  repo           = "COS301-SE-2026/AI-Powered-Fire-Spread-Prediction-and-Containment-System"
  instance_names = ["fireaway-staging", "fireaway-prod-blue", "fireaway-prod-green"]
}

#Github OIDC

resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
}

data "aws_iam_policy_document" "trust" {
  statement {
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
      values = [
        "repo:${local.repo}:environment:staging",
        "repo:${local.repo}:environment:production",
      ]
    }
  }
}

resource "aws_iam_role" "gha_deploy" {
  name                 = "fireaway-gha-deploy"
  assume_role_policy   = data.aws_iam_policy_document.trust.json
  max_session_duration = 3600
}

#permissions

data "aws_iam_policy_document" "deploy" {
  #ECR login
  statement {
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }

  #ECR push and pull and image lookup
  statement {
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:InitiateLayerUpload",
      "ecr:UploadLayerPart",
      "ecr:CompleteLayerUpload",
      "ecr:PutImage",
      "ecr:BatchGetImage",
      "ecr:GetDownloadUrlForLayer",
      "ecr:DescribeImages",
    ]
    resources = [
      "arn:aws:ecr:us-east-1:${local.account}:repository/fireaway-ryan-backend",
      "arn:aws:ecr:us-east-1:${local.account}:repository/fireaway-ryan-frontend",
    ]
  }

  statement {
    actions   = ["s3:PutObject"]
    resources = ["arn:aws:s3:::fireaway-ryan-artifacts/deploy/*"]
  }

  # describe calls can't be resource stopped
  statement {
    actions = [
      "ec2:DescribeInstances",
      "ec2:DescribeAddresses",
      "ssm:DescribeInstanceInformation",
      "ssm:GetCommandInvocation",
    ]
    resources = ["*"]
  }

  #start stope only the 3 instances
  statement {
    actions   = ["ec2:StartInstances", "ec2:StopInstances"]
    resources = ["arn:aws:ec2:us-east-1:${local.account}:instance/*"]
    condition {
      test     = "StringEquals"
      variable = "aws:ResourceTag/Name"
      values   = local.instance_names
    }
  }

  # EIP swap
  statement {
    actions   = ["ec2:AssociateAddress"]
    resources = ["*"]
  }

  # ssm the document
  statement {
    actions   = ["ssm:SendCommand"]
    resources = ["arn:aws:ssm:us-east-1::document/AWS-RunShellScript"]
  }

  # and only the 3 instances
  statement {
    actions   = ["ssm:SendCommand"]
    resources = ["arn:aws:ec2:us-east-1:${local.account}:instance/*"]
    condition {
      test     = "StringEquals"
      variable = "aws:ResourceTag/Name"
      values   = local.instance_names
    }
  }

  # active color  
  statement {
    actions   = ["ssm:GetParameter", "ssm:PutParameter"]
    resources = ["arn:aws:ssm:us-east-1:${local.account}:parameter/fireaway/prod/active_color"]
  }
}

resource "aws_iam_role_policy" "deploy" {
  name   = "deploy"
  role   = aws_iam_role.gha_deploy.id
  policy = data.aws_iam_policy_document.deploy.json
}

output "role_arn" {
  value = aws_iam_role.gha_deploy.arn
}
