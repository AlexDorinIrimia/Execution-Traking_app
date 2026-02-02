variable "aws_region" {
    description = "Default aws region to deploy"
    default = "eu-central-1"
}

variable "db_name" {
    description = "Database name"
    default = "execution_db"
}

variable "db_username" {
  description = "Database username"
  default = "user_exec"
}

variable "db_password" {
    description = "Postgres password"
    sensitive = true
}

variable "ec2_key_name" {
  description = "SSH key name for EC2"
  type        = string
  default = "myKey"
}