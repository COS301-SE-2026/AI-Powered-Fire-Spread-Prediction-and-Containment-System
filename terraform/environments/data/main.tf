data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_db_subnet_group" "fireaway" {
  name = "fireaway-db-subnet-group"
  subnet_ids = data.aws_subnets.default.ids
}

resource "aws_security_group" "rds" {
  name = "fireaway-rds-sg"
  vpc_id = data.aws_vpc.default.id

  ingress {
    from_port = 5432
    to_port = 5432
    protocol = "tcp"
    cidr_blocks = [data.aws_vpc.default.cidr_block] # reachable from anything inside the vpc
  }

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_instance" "fireaway" {
  identifier = "fireaway-db"
  engine = "postgres"
  engine_version = "15"
  instance_class = "db.t4g.micro"
  allocated_storage = 20
  db_name = "fireaway_prod"
  username = "fireaway_admin"
  password = var.db_password
  db_subnet_group_name = aws_db_subnet_group.fireaway.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible = false
  skip_final_snapshot = true
  apply_immediately = true
}

output "rds_endpoint" {
  value = aws_db_instance.fireaway.address
}