output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.capstone_presentations.bucket
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.capstone_presentations.arn
}

output "s3_bucket_region" {
  description = "Region of the S3 bucket"
  value       = aws_s3_bucket.capstone_presentations.region
}

output "s3_bucket_url" {
  description = "S3 bucket URL"
  value       = "https://${aws_s3_bucket.capstone_presentations.bucket}.s3.${var.aws_region}.amazonaws.com"
}

output "ec2_instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.marsh_backend.id
}

output "ec2_instance_public_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.marsh_backend.public_ip
}

output "ec2_instance_public_dns" {
  description = "Public DNS name of the EC2 instance"
  value       = aws_instance.marsh_backend.public_dns
}

output "security_group_id" {
  description = "ID of the security group"
  value       = aws_security_group.marsh_backend.id
}

output "secrets_manager_arn" {
  description = "ARN of the Secrets Manager secret"
  value       = data.aws_secretsmanager_secret.marsh_backend_secrets.arn
}

output "secrets_manager_name" {
  description = "Name of the Secrets Manager secret"
  value       = data.aws_secretsmanager_secret.marsh_backend_secrets.name
}

output "iam_role_arn" {
  description = "ARN of the IAM role"
  value       = aws_iam_role.ec2_role.arn
}

output "iam_instance_profile_name" {
  description = "Name of the IAM instance profile"
  value       = aws_iam_instance_profile.ec2_profile.name
}

output "backend_api_url" {
  description = "Backend API URL (via nginx)"
  value       = "http://${aws_instance.marsh_backend.public_ip}"
}

output "backend_docs_url" {
  description = "Backend API documentation URL"
  value       = "http://${aws_instance.marsh_backend.public_ip}/docs"
}