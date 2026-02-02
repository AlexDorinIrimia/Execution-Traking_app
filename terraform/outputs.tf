output "db_endpoint" {
    value = aws_db_instance.postgres.endpoint
}

output "db_port" {
    value = aws_db_instance.postgres.port
}

output "ec2_public_ip" {
  value = aws_instance.flask_ec2.public_ip
}