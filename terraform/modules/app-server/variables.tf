variable "environment" {
  type        = string
  description = "staging | prod-blue | prod-green"
}

variable "instance_type" {
  type        = string
  description = "t3.small"
}

variable "security_group_id" {
  type = string
}

variable "key_name" {
  type        = string
  description = "Name of the existing EC2 key pair in AWS"
}

variable "env_secret_name" {
  type        = string
  description = "fireaway/prod/env or fireaway/prod/env as an example"
}

variable "caddyfile_content" {
  type = string
}
