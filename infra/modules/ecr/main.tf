resource "aws_ecr_repository" "ml_pipeline" {
  name                 = "${var.name}-mlops-practice/ml-pipeline"
  image_tag_mutability = "MUTABLE"
}

resource "aws_ecr_repository" "predictor" {
  name                 = "${var.name}-mlops-practice/predictor"
  image_tag_mutability = "MUTABLE"
}

resource "aws_ecr_repository" "predictor_canary" {
  name                 = "${var.name}-mlops-practice/predictor-canary"
  image_tag_mutability = "MUTABLE"
}

resource "aws_ecr_repository" "grafana" {
  name                 = "${var.name}-mlops-practice/grafana"
  image_tag_mutability = "MUTABLE"
}

resource "aws_ecr_repository" "prometheus" {
  name                 = "${var.name}-mlops-practice/prometheus"
  image_tag_mutability = "MUTABLE"
}

resource "aws_ecr_repository" "pushgateway" {
  name                 = "${var.name}-mlops-practice/pushgateway"
  image_tag_mutability = "MUTABLE"
}

resource "aws_ecr_repository" "fluentd" {
  name                 = "${var.name}-mlops-practice/fluentd"
  image_tag_mutability = "MUTABLE"
}

resource "aws_ecr_repository" "importer" {
  name                 = "${var.name}-mlops-practice/importer"
  image_tag_mutability = "MUTABLE"
}

resource "aws_ecr_repository" "ecs_exporter" {
  name                 = "${var.name}-mlops-practice/ecs-exporter"
  image_tag_mutability = "MUTABLE"
}
