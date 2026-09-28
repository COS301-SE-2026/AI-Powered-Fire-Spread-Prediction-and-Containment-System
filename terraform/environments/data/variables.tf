variable "db_password" {
  type      = string
  sensitive = true
}

variable "legacy_app_sg_id" {
  type        = string
  default     = ""
  description = "SG of the current EC2 host. Keeps its RDS access until retired"
}
