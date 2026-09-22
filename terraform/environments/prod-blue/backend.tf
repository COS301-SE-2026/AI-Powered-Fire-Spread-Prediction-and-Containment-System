terraform {
  backend "s3" {
    bucket       = "fireaway-terraform-state-856820204904"
    key          = "prod-blue/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
    encrypt      = true
  }
}
