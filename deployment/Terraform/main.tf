terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Random suffix for unique bucket naming
resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

# S3 Bucket for storing PowerPoint templates and generated presentations
resource "aws_s3_bucket" "capstone_presentations" {
  bucket = "${var.project_name}-presentations-${var.environment}-${random_string.suffix.result}"

  tags = {
    Name        = "${var.project_name}-presentations"
    Environment = var.environment
    Project     = var.project_name
  }
}

# Bucket versioning
resource "aws_s3_bucket_versioning" "presentations_versioning" {
  bucket = aws_s3_bucket.capstone_presentations.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Bucket encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "presentations_encryption" {
  bucket = aws_s3_bucket.capstone_presentations.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "presentations_pab" {
  bucket = aws_s3_bucket.capstone_presentations.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Create some initial folder structure
resource "aws_s3_object" "templates_folder" {
  bucket = aws_s3_bucket.capstone_presentations.id
  key    = "templates/"
  content_type = "application/x-directory"
}

resource "aws_s3_object" "generated_folder" {
  bucket = aws_s3_bucket.capstone_presentations.id
  key    = "generated/"
  content_type = "application/x-directory"
}

resource "aws_s3_object" "archives_folder" {
  bucket = aws_s3_bucket.capstone_presentations.id
  key    = "archives/"
  content_type = "application/x-directory"
}

# Data source for default VPC
data "aws_vpc" "default" {
  default = true
}

data "aws_subnet" "default" {
  vpc_id            = data.aws_vpc.default.id
  availability_zone = "${var.aws_region}a"  # Adjust as needed
  default_for_az    = true
}

# Security Group for backend
resource "aws_security_group" "marsh_backend" {
  name        = "Marsh_Cyber_Content_Tool-backend"
  description = "Security group for Marsh Cyber Content Tool FastAPI backend - allows SSH, HTTP, and API access"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["222.164.146.199/32"]  # Your specific IP from CloudTrail
    description = "SSH access"
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP traffic for Nginx"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "Marsh_Cyber_Content_Tool-backend"
  }
}

# IAM role for EC2 instance
resource "aws_iam_role" "ec2_role" {
  name = "marsh-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# Custom IAM policy for Secrets Manager access
resource "aws_iam_policy" "secrets_access_policy" {
  name        = "marsh-secrets-access-policy"
  description = "Custom policy to access Secrets Manager for Marsh backend"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = data.aws_secretsmanager_secret.marsh_backend_secrets.arn
      }
    ]
  })
}

# Attach custom secrets policy to role
resource "aws_iam_role_policy_attachment" "secrets_policy" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.secrets_access_policy.arn
}

# IAM instance profile
resource "aws_iam_instance_profile" "ec2_profile" {
  name = "marsh-ec2-profile"
  role = aws_iam_role.ec2_role.name
}

# Attach SSM managed policy to role
resource "aws_iam_role_policy_attachment" "ssm_policy" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# Key pair for EC2 instance
resource "aws_key_pair" "capstone_key" {
  key_name   = "capstone-key"
  public_key = var.public_key  # You'll need to define this variable
}

# Use data source for AMI instead of hardcoded
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# EC2 instance
resource "aws_instance" "marsh_backend" {
  ami                    = data.aws_ami.ubuntu.id  # Use dynamic AMI
  instance_type          = var.instance_type
  key_name              = aws_key_pair.capstone_key.key_name
  vpc_security_group_ids = [aws_security_group.marsh_backend.id]
  subnet_id             = data.aws_subnet.default.id
  iam_instance_profile  = aws_iam_instance_profile.ec2_profile.name

  tags = {
    Name = "Marsh-Backend-Instance"
  }
}

# Reference existing secret instead of creating new one
data "aws_secretsmanager_secret" "marsh_backend_secrets" {
  name = "marsh-backend/all-secrets"
}