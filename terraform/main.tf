terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # MAUVAISE PRATIQUE: Pas de backend S3 configuré pour le state
  # Le state sera local, risque de perte et pas de collaboration
}

provider "aws" {
  region = var.aws_region

  # MAUVAISE PRATIQUE: Credentials potentiellement hardcodés
  # Ne jamais mettre access_key et secret_key ici
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}
