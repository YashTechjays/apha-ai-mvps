variable "aws_region" { default = "us-east-1" }
variable "db_password" { sensitive = true }
variable "project" { default = "apha-churn" }
variable "env" { default = "prod" }
