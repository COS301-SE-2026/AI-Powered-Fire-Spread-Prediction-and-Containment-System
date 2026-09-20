terraform {
  backend "s3" {
    bucket         = "fireaway-terraform-state-856820204904"
    key            = "prod-green/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "fireaway-terraform-locks"
    encrypt        = true
  }
}
