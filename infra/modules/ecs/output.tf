output "ml_pipeline_task_definition_arn" {
  value = aws_ecs_task_definition.ml_pipeline.arn
}

output "update_server_task_definition_arn" {
  value = aws_ecs_task_definition.update_server.arn
}

output "cluster_arn" {
  value = aws_ecs_cluster.mlops_practice.arn
}
