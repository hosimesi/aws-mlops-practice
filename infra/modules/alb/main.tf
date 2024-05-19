# ALB for MLOps Practice Predictor
resource "aws_lb" "mlops_practice_predictor" {
  load_balancer_type = "application"
  name               = "${var.name}-predictor-alb"

  security_groups = ["${var.predictor_alb_security_group}"]
  subnets         = var.alb_subnets
}


# ELB Target Group for MLOps Practice Predictor
resource "aws_lb_target_group" "mlops_practice_predictor" {
  name = "${var.name}-predictor-tg"

  port        = 8080
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = var.vpc_id
  health_check {
    port = 8080
    path = "/"
  }
}

# Listener for MLOps Practice Predictor
resource "aws_lb_listener" "mlops_practice_predictor" {
  load_balancer_arn = aws_lb.mlops_practice_predictor.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.mlops_practice_predictor.arn
  }
}


resource "aws_lb_listener_rule" "mlops_practice_predictor" {
  listener_arn = aws_lb_listener.mlops_practice_predictor.arn

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.mlops_practice_predictor.arn
  }

  condition {
    path_pattern {
      values = ["/", "/predict"]
    }
  }
}


resource "aws_lb_target_group" "mlops_practice_predictor_canary" {
  name = "${var.name}-predictor-canary-tg"

  port        = 8080
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = var.vpc_id
  health_check {
    port = 8080
    path = "/"
  }
}


# ALB for MLOps Practice Dashboard
resource "aws_lb" "mlops_practice_dashboard" {
  load_balancer_type = "application"
  name               = "${var.name}-dashboard-alb"

  security_groups = ["${var.dashboard_alb_security_group}"]
  subnets         = var.alb_subnets
}


# ELB Target Group for MLOps Practice Dashboard
resource "aws_lb_target_group" "mlops_practice_dashboard" {
  name = "${var.name}-dashboard-tg"

  port        = 3000
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = var.vpc_id
  health_check {
    port = 3000
    path = "/api/health"
  }
}

# Listener for MLOps Practice Dashboard
resource "aws_lb_listener" "mlops_practice_dashboard" {
  load_balancer_arn = aws_lb.mlops_practice_dashboard.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.mlops_practice_dashboard.arn
  }
}
