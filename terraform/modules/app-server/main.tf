data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

data "aws_region" "current" {}

resource "aws_iam_role" "app_server" {
  name = "fireaway-${var.environment}-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "read_env_secret" {
  role = aws_iam_role.app_server.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action = "secretsmanager:GetSecretValue"
      Resource    = "arn:aws:secretsmanager:${data.aws_region.current.name}:*:secret:${var.env_secret_name}-*"
    }]
  })
}

resource "aws_iam_role_policy" "queues_and_bucket" {
  role = aws_iam_role.app_server.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = ["sqs:SendMessage", "sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"]
        Resource = [
          "arn:aws:sqs:${data.aws_region.current.name}:856820204904:fireaway-ryan-inference",
          "arn:aws:sqs:${data.aws_region.current.name}:856820204904:fireaway-ryan-results",
        ]
      },
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject"]
        Resource = "arn:aws:s3:::fireaway-ryan-artifacts/*"
      }
    ]
  })
}

resource "aws_iam_instance_profile" "app_server" {
  name = "fireaway-${var.environment}-profile"
  role = aws_iam_role.app_server.name
}

resource "aws_instance" "app_server" {
  ami = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  key_name = var.key_name
  vpc_security_group_ids = [var.security_group_id]
  iam_instance_profile = aws_iam_instance_profile.app_server.name

  user_data = templatefile("${path.module}/user_data.sh.tftpl", {
    env_secret_name = var.env_secret_name
    aws_region = data.aws_region.current.name
    caddyfile_content = var.caddyfile_content
  })

  tags = {
    Name = "fireaway-${var.environment}"
    Environment = var.environment
  }
}
