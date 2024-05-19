output "ml_pipeline_ecr_uri" {
  value = aws_ecr_repository.ml_pipeline.repository_url
}

output "predictor_ecr_uri" {
  value = aws_ecr_repository.predictor.repository_url
}

output "predictor_canary_ecr_uri" {
  value = aws_ecr_repository.predictor_canary.repository_url
}

output "grafana_ecr_uri" {
  value = aws_ecr_repository.grafana.repository_url
}

output "prometheus_ecr_uri" {
  value = aws_ecr_repository.prometheus.repository_url
}

output "pushgateway_ecr_uri" {
  value = aws_ecr_repository.pushgateway.repository_url
}

output "fluentd_ecr_uri" {
  value = aws_ecr_repository.fluentd.repository_url
}

output "importer_ecr_uri" {
  value = aws_ecr_repository.importer.repository_url
}

output "ecs_exporter_ecr_uri" {
  value = aws_ecr_repository.ecs_exporter.repository_url
}
