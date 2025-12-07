# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"

  # MAUVAISE PRATIQUE: Container Insights désactivé
  setting {
    name  = "containerInsights"
    value = "disabled"
  }

  # MAUVAISE PRATIQUE: Pas de tags
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/${var.project_name}"
  retention_in_days = 7

  # MAUVAISE PRATIQUE: Pas d'encryption KMS
  # MAUVAISE PRATIQUE: Rétention trop courte pour la production
  # MAUVAISE PRATIQUE: Pas de tags
}

# ECS Task Definition
resource "aws_ecs_task_definition" "app" {
  family                   = var.project_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.container_cpu
  memory                   = var.container_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = var.project_name
      image     = "${aws_ecr_repository.app.repository_url}:latest"
      essential = true

      portMappings = [
        {
          containerPort = var.container_port
          protocol      = "tcp"
        }
      ]

      # MAUVAISE PRATIQUE: Secrets en clair dans les variables d'environnement
      environment = [
        {
          name  = "NODE_ENV"
          value = "production"
        },
        {
          name  = "API_KEY"
          value = var.api_key
        },
        {
          name  = "DATABASE_PASSWORD"
          value = var.db_password
        },
        {
          name  = "AWS_ACCESS_KEY_ID"
          value = "AKIAIOSFODNN7EXAMPLE"
        },
        {
          name  = "AWS_SECRET_ACCESS_KEY"
          value = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.app.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      # MAUVAISE PRATIQUE: Pas de healthcheck défini
      # MAUVAISE PRATIQUE: Pas de resource limits stricts
    }
  ])

  # MAUVAISE PRATIQUE: Pas de tags
}

# ECS Service
resource "aws_ecs_service" "app" {
  name            = "${var.project_name}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    security_groups  = [aws_security_group.ecs_tasks.id]
    subnets          = data.aws_subnets.default.ids
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = var.project_name
    container_port   = var.container_port
  }

  depends_on = [aws_lb_listener.http]

  # MAUVAISE PRATIQUE: Pas de deployment configuration optimisée
  # MAUVAISE PRATIQUE: Pas de service discovery
  # MAUVAISE PRATIQUE: Pas de tags
}
