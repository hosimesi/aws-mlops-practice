output "predictor_target_group_arn" {
  value = aws_lb_target_group.mlops_practice_predictor.arn
}

output "dashboard_target_group_arn" {
  value = aws_lb_target_group.mlops_practice_dashboard.arn
}

output "predictor_canary_target_group_arn" {
  value = aws_lb_target_group.mlops_practice_predictor_canary.arn
}
