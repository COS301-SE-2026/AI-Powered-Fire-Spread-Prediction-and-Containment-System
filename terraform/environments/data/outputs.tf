output "rds_endpoint" {
  value = aws_db_instance.fireaway.address
}

output "app_sg_id" {
  value = aws_security_group.app.id
}

output "prod_eip_allocation_id" {
  value = aws_eip.prod.allocation_id
}

output "prod_eip_public_ip" {
  value = aws_eip.prod.public_ip
}

output "staging_eip_allocation_id" {
  value = aws_eip.staging.allocation_id
}

output "staging_eip_public_ip" {
  value = aws_eip.staging.public_ip
}

output "staging_secret_name" {
  value = aws_secretsmanager_secret.env["staging"].name
}

output "prod_secret_name" {
  value = aws_secretsmanager_secret.env["prod"].name
}
