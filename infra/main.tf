provider "aws" { region = var.aws_region }

resource "aws_s3_bucket" "model_store" {
  bucket = "${var.project}-models-${var.env}"
  tags   = { Project = var.project, Env = var.env }
}

resource "aws_ecr_repository" "backend" {
  name                 = "${var.project}-backend"
  image_tag_mutability = "MUTABLE"
}

resource "aws_db_instance" "postgres" {
  identifier        = "${var.project}-db"
  engine            = "postgres"
  engine_version    = "15"
  instance_class    = "db.t3.micro"
  allocated_storage = 20
  db_name           = "churn_db"
  username          = "apha"
  password          = var.db_password
  skip_final_snapshot = true
  tags = { Project = var.project }
}
