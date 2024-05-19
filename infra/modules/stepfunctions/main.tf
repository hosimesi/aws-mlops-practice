resource "aws_sfn_state_machine" "mlops_practice" {
  name     = "${var.name}-mlops-practice-ml-pipeline"
  role_arn = var.stepfunctions_role_arn

  definition = templatefile("./modules/stepfunctions/definition/execute_ml_pipeline.json", {
    cluster_arn         = "${var.cluster_arn}",
    task_definition_arn = "${var.task_definition_arn}",
    security_group      = "${var.security_group}",
    subnet              = "${var.subnet}"
  })
}

# resource "aws_sfn_state_machine" "mlops_practice_parallel" {
#   name     = "${var.name}-mlops-practice-ml-pipeline-parallel"
#   role_arn = var.stepfunctions_role_arn

#   definition = templatefile("./modules/stepfunctions/definition/execute_ml_pipeline_parallel.json", {
#     cluster_arn                       = "${var.cluster_arn}",
#     task_definition_arn               = "${var.task_definition_arn}",
#     update_server_task_definition_arn = "${var.update_server_task_definition_arn}",
#     security_group                    = "${var.security_group}",
#     subnet                            = "${var.subnet}"
#   })
# }
