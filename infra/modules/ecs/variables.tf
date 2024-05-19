variable "private_subnets" {
  description = "List of private subnet ids to place to predictor"
}

variable "predictor_security_group" {
  description = "security group id for predictor"
}

variable "dashboard_security_group" {
  description = "security group id for dashboard"
}

variable "prometheus_security_group" {
  description = "security group id for prometheus"
}

variable "pushgateway_security_group" {
  description = "security group id for pushgateway"
}

variable "predictor_target_group_arn" {
  description = "target group for predictor load balancer"
}

variable "predictor_canary_target_group_arn" {
  description = "target group for predictor canary load balancer"
}

variable "dashboard_target_group_arn" {
  description = "target group for dashboard load balancer"
}

variable "ml_pipeline_ecr_uri" {
  description = "ECR URI for ml pipeline ecs task"
}

variable "predictor_ecr_uri" {
  description = "ECR URI for predictor ecs task"
}

variable "predictor_canary_ecr_uri" {
  description = "ECR URI for predictor canary ecs task"
}

variable "grafana_ecr_uri" {
  description = "ECR URI for grafana ecs task"
}

variable "prometheus_ecr_uri" {
  description = "ECR URI for prometheus ecs task"
}

variable "pushgateway_ecr_uri" {
  description = "ECR URI for pushgateway ecs task"
}

variable "fluentd_ecr_uri" {
  description = "ECR URI for fluentd ecs task"
}

variable "ecs_exporter_ecr_uri" {
  description = "ECR URI for ecs exporter ecs task"
}

variable "ecs_task_role_arn" {
  description = "IAM Role for ecs task application"
}

variable "ecs_task_execution_role_arn" {
  description = "IAM Role for ecs task execution"
}

variable "name" {
  description = "Your name for ecs resources."
  type        = string
}
