# terraform/variables.tf
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-southeast-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "capstone"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "public_key" {
  description = "Public key for EC2 key pair"
  type        = string
}

# Sensitive variables for secrets
variable "mongo_url" {
  description = "MongoDB connection URL"
  type        = string
  sensitive   = true
}

variable "tavily_api_key" {
  description = "Tavily API key"
  type        = string
  sensitive   = true
}

variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true
}

variable "phoenix_api_key" {
  description = "Phoenix API key"
  type        = string
  sensitive   = true
}

variable "otel_exporter_otlp_headers" {
  description = "OTEL exporter OTLP headers"
  type        = string
  sensitive   = true
}

variable "logo_dev_token" {
  description = "Logo.dev API token"
  type        = string
  sensitive   = true
}

variable "template_s3_key" {
  description = "S3 key for PowerPoint template"
  type        = string
  default     = "templates/PPT_Template.pptx"
}