data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# App servers

resource "aws_security_group" "app" {
  name        = "fireaway-app-sg"
  description = "FireAway app servers - Caddy on 80/443"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# stable public ip where dns points to
resource "aws_eip" "prod" {
  domain = "vpc"
  tags   = { Name = "fireaway-prod-live" }

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_eip" "staging" {
  domain = "vpc"
  tags   = { Name = "fireaway-staging" }
}

# which production color is live
# deploy script will own the value after creation
resource "aws_ssm_parameter" "active_color" {
  name  = "/fireaway/prod/active_color"
  type  = "String"
  value = "blue"

  lifecycle {
    ignore_changes = [value]
  }
}

# Secret containers only. Values uploaded using the CLI and never enter state
resource "aws_secretsmanager_secret" "env" {
  for_each                = toset(["staging", "prod"])
  name                    = "fireaway/${each.key}/env"
  recovery_window_in_days = 7
}

resource "aws_s3_bucket" "reports" {
  bucket = "fireaway-ryan-fire-reports"
}

resource "aws_s3_bucket_public_access_block" "reports" {
  bucket                  = aws_s3_bucket.reports.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# database stuff

resource "aws_db_subnet_group" "fireaway" {
  name       = "fireaway-db-subnet-group"
  subnet_ids = data.aws_subnets.default.ids
}

resource "aws_security_group" "rds" {
  name   = "fireaway-rds-sg"
  vpc_id = data.aws_vpc.default.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = compact([aws_security_group.app.id, var.legacy_app_sg_id])
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "fireaway" {
  identifier                = "fireaway-db"
  engine                    = "postgres"
  engine_version            = "15"
  instance_class            = "db.t4g.micro"
  allocated_storage         = 20
  db_name                   = "fireaway_prod"
  username                  = "fireaway_admin"
  password                  = var.db_password
  db_subnet_group_name      = aws_db_subnet_group.fireaway.name
  vpc_security_group_ids    = [aws_security_group.rds.id]
  publicly_accessible       = false
  skip_final_snapshot       = false
  final_snapshot_identifier = "fireaway-db-final"
  deletion_protection       = true
  apply_immediately         = true
}