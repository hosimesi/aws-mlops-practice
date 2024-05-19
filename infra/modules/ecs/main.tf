resource "aws_ecs_cluster" "mlops_practice" {
  name = "${var.name}-mlops-practice-ecs"
}

resource "aws_ecs_task_definition" "ml_pipeline" {
  family                   = "${var.name}-ml-pipeline"
  network_mode             = "awsvpc"
  cpu                      = 1024
  memory                   = 2048
  requires_compatibilities = ["FARGATE"]
  container_definitions = templatefile("./modules/ecs/container_definitions/ml_pipeline.json", {
    ml_pipeline_ecr_uri = "${var.ml_pipeline_ecr_uri}",
    name                = "${var.name}"
  })
  task_role_arn      = var.ecs_task_role_arn
  execution_role_arn = var.ecs_task_execution_role_arn
}


resource "aws_ecs_task_definition" "update_server" {
  family                   = "${var.name}-update-server"
  network_mode             = "awsvpc"
  cpu                      = 1024
  memory                   = 2048
  requires_compatibilities = ["FARGATE"]
  container_definitions = templatefile("./modules/ecs/container_definitions/update_server.json", {
    ml_pipeline_ecr_uri = "${var.ml_pipeline_ecr_uri}",
    name                = "${var.name}"
  })
  task_role_arn      = var.ecs_task_role_arn
  execution_role_arn = var.ecs_task_execution_role_arn
}

resource "aws_ecs_task_definition" "predictor" {
  family                   = "${var.name}-predictor"
  network_mode             = "awsvpc"
  cpu                      = 1024
  memory                   = 2048
  requires_compatibilities = ["FARGATE"]
  container_definitions = templatefile("./modules/ecs/container_definitions/predictor.json", {
    predictor_ecr_uri    = "${var.predictor_ecr_uri}",
    fluentd_ecr_uri      = "${var.fluentd_ecr_uri}",
    ecs_exporter_ecr_uri = "${var.ecs_exporter_ecr_uri}",
    name                 = "${var.name}"
  })
  volume {
    name = "logs"
  }
  task_role_arn      = var.ecs_task_role_arn
  execution_role_arn = var.ecs_task_execution_role_arn
}

resource "aws_ecs_service" "predictor" {
  name                               = "${var.name}-predictor-service"
  cluster                            = aws_ecs_cluster.mlops_practice.name
  task_definition                    = aws_ecs_task_definition.predictor.arn
  desired_count                      = 1
  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 200
  launch_type                        = "FARGATE"
  network_configuration {
    security_groups = [var.predictor_security_group]
    subnets         = var.private_subnets
  }

  load_balancer {
    target_group_arn = var.predictor_target_group_arn
    container_name   = "predictor"
    container_port   = 8080
  }
}

resource "aws_appautoscaling_target" "predictor" {
  max_capacity       = 3
  min_capacity       = 2
  resource_id        = "service/${aws_ecs_cluster.mlops_practice.name}/${aws_ecs_service.predictor.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "predictor" {
  name               = "${var.name}-predictor-auto-scaling-policy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.predictor.resource_id
  scalable_dimension = aws_appautoscaling_target.predictor.scalable_dimension
  service_namespace  = aws_appautoscaling_target.predictor.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    scale_in_cooldown  = 60
    scale_out_cooldown = 60
    target_value       = 70.0
  }
}


#########Dashboard#########
# Dashboard用クラスター
resource "aws_ecs_cluster" "mlops_practice_dashboard" {
  name = "${var.name}-dashboard-ecs"
}

# Dashboard用タスク定義
resource "aws_ecs_task_definition" "dashboard" {
  family                   = "${var.name}-dashboard"
  network_mode             = "awsvpc"
  cpu                      = 1024
  memory                   = 2048
  requires_compatibilities = ["FARGATE"]
  container_definitions = templatefile("./modules/ecs/container_definitions/dashboard.json", {
    grafana_ecr_uri = "${var.grafana_ecr_uri}",
    name            = "${var.name}"
  })
  task_role_arn      = var.ecs_task_role_arn
  execution_role_arn = var.ecs_task_execution_role_arn
}


# ECS Service
resource "aws_ecs_service" "dashboard" {
  name                               = "${var.name}-dashboard-service"
  cluster                            = aws_ecs_cluster.mlops_practice_dashboard.name
  task_definition                    = aws_ecs_task_definition.dashboard.arn
  desired_count                      = 1
  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 200
  launch_type                        = "FARGATE"
  network_configuration {
    security_groups = [
      "${var.dashboard_security_group}"
    ]
    subnets = var.private_subnets
  }

  load_balancer {
    target_group_arn = var.dashboard_target_group_arn
    container_name   = "grafana"
    container_port   = 3000
  }
}

# Auto Scaling Target
resource "aws_appautoscaling_target" "dashboard" {
  max_capacity       = 2
  min_capacity       = 1
  resource_id        = "service/${aws_ecs_cluster.mlops_practice_dashboard.name}/${aws_ecs_service.dashboard.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# Auto Scaling Policy
resource "aws_appautoscaling_policy" "dashboard" {
  name               = "${var.name}-dashboard-auto-scaling-policy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.dashboard.resource_id
  scalable_dimension = aws_appautoscaling_target.dashboard.scalable_dimension
  service_namespace  = aws_appautoscaling_target.dashboard.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    scale_in_cooldown  = 60
    scale_out_cooldown = 60
    target_value       = 70.0
  }
}


####### Prometheus ########
# タスク定義
resource "aws_ecs_task_definition" "prometheus" {
  family                   = "${var.name}-prometheus"
  network_mode             = "awsvpc"
  cpu                      = 1024
  memory                   = 2048
  requires_compatibilities = ["FARGATE"]
  container_definitions = templatefile("./modules/ecs/container_definitions/prometheus.json", {
    prometheus_ecr_uri = "${var.prometheus_ecr_uri}",
    name               = "${var.name}"
  })
  volume {
    name = "logs"
  }
  task_role_arn      = var.ecs_task_role_arn
  execution_role_arn = var.ecs_task_execution_role_arn
}

# Prometheus ECS Service
resource "aws_ecs_service" "prometheus" {
  name                               = "${var.name}-prometheus-service"
  cluster                            = aws_ecs_cluster.mlops_practice_dashboard.name
  task_definition                    = aws_ecs_task_definition.prometheus.arn
  desired_count                      = 1
  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 200
  launch_type                        = "FARGATE"
  network_configuration {
    security_groups = ["${var.prometheus_security_group}"]
    subnets         = var.private_subnets
  }
}
############################################


####### Pushgateway ########
# タスク定義
resource "aws_ecs_task_definition" "pushgateway" {
  family                   = "${var.name}-pushgateway"
  network_mode             = "awsvpc"
  cpu                      = 1024
  memory                   = 2048
  requires_compatibilities = ["FARGATE"]
  container_definitions = templatefile("./modules/ecs/container_definitions/pushgateway.json", {
    pushgateway_ecr_uri = "${var.pushgateway_ecr_uri}",
    name                = "${var.name}"
  })
  task_role_arn      = var.ecs_task_role_arn
  execution_role_arn = var.ecs_task_execution_role_arn
}

# Pushgateway ECS Service
resource "aws_ecs_service" "pushgateway" {
  name                               = "${var.name}-pushgateway-service"
  cluster                            = aws_ecs_cluster.mlops_practice_dashboard.name
  task_definition                    = aws_ecs_task_definition.pushgateway.arn
  desired_count                      = 1
  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 200
  launch_type                        = "FARGATE"
  network_configuration {
    security_groups = [
      "${var.pushgateway_security_group}"
    ]
    subnets = var.private_subnets
  }
}
############################################
