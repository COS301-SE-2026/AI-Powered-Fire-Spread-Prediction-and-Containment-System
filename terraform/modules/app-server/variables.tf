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
  default     = null
  description = "Optional ec2 key pair, now using ssm which doesnt need key pair"
}

variable "env_secret_name" {
  type        = string
  description = "fireaway/prod/env or fireaway/staging/env as an example"
}

variable "caddyfile_content" {
  type = string
}
