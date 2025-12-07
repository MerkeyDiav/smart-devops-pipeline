# ECR Repository pour stocker les images Docker
resource "aws_ecr_repository" "app" {
  name                 = "${var.project_name}-${var.environment}"
  image_tag_mutability = "MUTABLE"

  # MAUVAISE PRATIQUE: Scan des images désactivé
  image_scanning_configuration {
    scan_on_push = false
  }

  # MAUVAISE PRATIQUE: Pas de politique de lifecycle
  # Les anciennes images vont s'accumuler et coûter cher

  # MAUVAISE PRATIQUE: Pas d'encryption KMS
  encryption_configuration {
    encryption_type = "AES256"
  }

  # MAUVAISE PRATIQUE: Pas de tags
}

# MAUVAISE PRATIQUE: Repository policy trop permissive
resource "aws_ecr_repository_policy" "app" {
  repository = aws_ecr_repository.app.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowPushPull"
        Effect = "Allow"
        Principal = {
          AWS = "*"
        }
        Action = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload"
        ]
      }
    ]
  })
}
