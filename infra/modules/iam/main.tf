resource "aws_iam_policy" "ecs_task_execution_policy" {
  name = "${var.name}-mlops-practice-ecs-task-execution-policy"

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "VisualEditor0",
        "Effect" : "Allow",
        "Action" : [
          "ec2:AuthorizeSecurityGroupIngress",
          "ec2:CreateSecurityGroup",
          "ec2:CreateTags",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DescribeSecurityGroups",
          "ec2:DescribeSubnets",
          "ec2:DescribeVpcs",
          "ec2:DeleteSecurityGroup",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "ssm:DescribeParameters",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:GetAuthorizationToken",
          "logs:PutLogEvents",
          "ecr:BatchCheckLayerAvailability"
        ],
        "Resource" : "*"
      }
    ]
  })
}

resource "aws_iam_policy" "ecs_task_policy" {
  name = "${var.name}-mlops-practice-ecs-task-policy"

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "VisualEditor0",
        "Effect" : "Allow",
        "Action" : [
          "ec2:AuthorizeSecurityGroupIngress",
          "ec2:CreateSecurityGroup",
          "ec2:CreateTags",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DescribeSecurityGroups",
          "ec2:DescribeSubnets",
          "ec2:DescribeVpcs",
          "ec2:DeleteSecurityGroup",
          "ec2:DescribeInstances",
          "aps:GetSeries",
          "aps:GetLabels",
          "aps:GetMetricMetadata",
          "ecs:CreateCluster",
          "ecs:DeleteCluster",
          "ecs:DeregisterTaskDefinition",
          "ecs:DescribeClusters",
          "ecs:DescribeTaskDefinition",
          "ecs:DescribeTasks",
          "ecs:ListAccountSettings",
          "ecs:ListClusters",
          "ecs:ListTaskDefinitions",
          "ecs:RegisterTaskDefinition",
          "ecs:RunTask",
          "ecs:StopTask",
          "ecs:UpdateService",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:GetAuthorizationToken",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:GetLogEvents",
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket",
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:Scan",
          "dynamodb:Query",
          "redshift:GetClusterCredentials",
          "redshift:DescribeClusters",
          "redshift:ExecuteQuery",
          "redshift-data:ExecuteStatement",
          "redshift-data:GetStatementResult",
          "redshift-data:DescribeStatement",
          "redshift-serverless:GetCredentials",
        ],
        "Resource" : "*"
      }
    ]
  })
}

resource "aws_iam_policy" "step_functions_policy" {
  name = "${var.name}-mlops-practice-step-functions-policy"

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "VisualEditor0",
        "Effect" : "Allow",
        "Action" : [
          "logs:CreateLogDelivery",
          "logs:GetLogDelivery",
          "logs:UpdateLogDelivery",
          "logs:DeleteLogDelivery",
          "logs:ListLogDeliveries",
          "logs:PutResourcePolicy",
          "logs:DescribeResourcePolicies",
          "logs:DescribeLogGroups",
          "ecs:RunTask",
          "xray:PutTraceSegments",
          "xray:PutTelemetryRecords",
          "xray:GetSamplingRules",
          "xray:GetSamplingTargets",
          "iam:PassRole",
          "states:CreateStateMachine",
          "iam:CreateServiceLinkedRole",
          "events:PutTargets",
          "events:PutRule",
          "events:DescribeRule"
        ],
        "Resource" : "*"
      }
    ]
  })
}


resource "aws_iam_policy" "event_bridge_policy" {
  name = "${var.name}-mlops-practice-event-bridge-policy"

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "VisualEditor0",
        "Effect" : "Allow",
        "Action" : [
          "states:StartExecution"
        ],
        "Resource" : "*"
      }
    ]
  })
}


resource "aws_iam_policy" "redshift_policy" {
  name = "${var.name}-mlops-practice-redshift-policy"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "redshift:*",
          "s3:GetObject",
          "s3:ListBucket",
          "redshift-data:ExecuteStatement",
          "redshift-data:DescribeStatement",
          "redshift-data:GetStatementResult",
          "redshift-data:ListDatabases"
        ],
        "Resource" : "*"
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_policy" {
  name = "${var.name}-mlops-practice-lambda-policy"
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "redshift:GetClusterCredentials",
          "redshift-data:ExecuteStatement",
          "redshift-data:DescribeStatement",
          "redshift-serverless:GetCredentials",
          "s3:GetObject",
          "s3:ListBucket",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        "Resource" : "*"
      }
    ]
  })
}


resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${var.name}-mlops-practice-ecs-task-execution-role"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "ecs-tasks.amazonaws.com"
        },
        "Action" : "sts:AssumeRole",
      }
    ]
  })
}


resource "aws_iam_role" "ecs_task_role" {
  name = "${var.name}-mlops-practice-ecs-task-role"

  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "ec2.amazonaws.com"
        },
        "Action" : "sts:AssumeRole",
        "Condition" : {}
      },
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "ssm.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      },
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "ecs-tasks.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      },
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "redshift.amazonaws.com"
        },
        "Action" : "sts:AssumeRole",
      }
    ]
  })
}

resource "aws_iam_role" "step_functions_role" {
  name = "${var.name}-mlops-practice-step-functions-role"

  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "states.amazonaws.com"
        },
        "Action" : "sts:AssumeRole",
      }
    ]
  })
}

resource "aws_iam_role" "event_bridge_role" {
  name = "${var.name}-mlops-practice-event-bridge-role"

  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "scheduler.amazonaws.com"
        },
        "Action" : "sts:AssumeRole",
      }
    ]
  })
}

resource "aws_iam_role" "redshift_role" {
  name = "${var.name}-mlops-practice-redshift-role"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "redshift.amazonaws.com"
        },
        "Action" : "sts:AssumeRole",
      }
    ]
  })
}

resource "aws_iam_role" "lambda_role" {
  name = "${var.name}-mlops-practice-lambda-role"

  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Action" : "sts:AssumeRole",
        "Principal" : {
          "Service" : ["lambda.amazonaws.com", "redshift.amazonaws.com"]
        },
        "Effect" : "Allow",
        "Sid" : ""
      }
    ]
  })
}


resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = aws_iam_policy.ecs_task_execution_policy.arn
}

resource "aws_iam_role_policy_attachment" "ecs_task_policy_attach" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.ecs_task_policy.arn
}

resource "aws_iam_role_policy_attachment" "step_functions_policy_attach" {
  role       = aws_iam_role.step_functions_role.name
  policy_arn = aws_iam_policy.step_functions_policy.arn
}

resource "aws_iam_role_policy_attachment" "event_bridge_policy_attach" {
  role       = aws_iam_role.event_bridge_role.name
  policy_arn = aws_iam_policy.event_bridge_policy.arn
}

resource "aws_iam_role_policy_attachment" "redshift_policy_attach" {
  role       = aws_iam_role.redshift_role.name
  policy_arn = aws_iam_policy.redshift_policy.arn
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}
