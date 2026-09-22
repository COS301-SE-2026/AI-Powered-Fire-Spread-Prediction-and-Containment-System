terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

data "terraform_remote_state" "data" {
  backend = "s3"
  config = {
    bucket = "fireaway-terraform-state-856820204904"
    key    = "data/terraform.tfstate"
    region = "us-east-1"
  }
}

locals {
  shared = data.terraform_remote_state.data.outputs
}

module "app" {
  source            = "../../modules/app-server"
  environment       = "staging"
  instance_type     = var.instance_type
  security_group_id = local.shared.app_sg_id
  key_name          = var.key_name
  env_secret_name   = local.shared.staging_secret_name
  caddyfile_content = file("${path.module}/../../templates/Caddyfile.staging")
}

resource "aws_eip_association" "staging" {
  allocation_id = local.shared.staging_eip_allocation_id
  instance_id   = module.app.instance_id
}

output "instance_id" {
  value = module.app.instance_id
}

output "public_ip" {
  value = local.shared.staging_eip_public_ip
}