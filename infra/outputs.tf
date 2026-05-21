output "db_endpoint"     { value = aws_db_instance.postgres.endpoint }
output "s3_bucket"       { value = aws_s3_bucket.model_store.bucket }
output "ecr_backend_url" { value = aws_ecr_repository.backend.repository_url }
