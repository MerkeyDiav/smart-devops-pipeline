variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "tech-news-reader"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

# MAUVAISE PRATIQUE: Variable sensible sans sensitive = true
variable "db_password" {
  description = "Database password"
  type        = string
  default     = "SuperSecret123!"
}

# MAUVAISE PRATIQUE: API key en variable sans protection
variable "api_key" {
  description = "API Key for external service"
  type        = string
  default     = "sk-1234567890abcdef-FAKE-KEY"
}

variable "container_port" {
  description = "Container port"
  type        = number
  default     = 3000
}

variable "container_cpu" {
  description = "Container CPU units"
  type        = number
  default     = 256
}

variable "container_memory" {
  description = "Container memory in MB"
  type        = number
  default     = 512
}

variable "desired_count" {
  description = "Desired number of tasks"
  type        = number
  default     = 1
}
