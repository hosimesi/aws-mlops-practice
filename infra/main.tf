variable "aws_region" {
  description = "The AWS region to create resources in."
}

variable "aws_profile" {
  description = "The AWS-CLI profile for the account to create resources in."
}

variable "name" {
  description = "The name of the resources to create."
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}

terraform {
  required_version = "~> 1.4"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.42.0"
    }
  }

  backend "s3" {
    # FIXME:
    bucket  = "{名前}-mlops-practice-tfstate"
    region  = "ap-northeast-1"
    key     = "terraform.tfstate"
    encrypt = true
  }
}

module "s3" {
  source = "./modules/s3"
  name   = var.name
}

module "ecr" {
  source = "./modules/ecr"
  name   = var.name
}

module "iam" {
  source = "./modules/iam"
  name   = var.name
}

module "network" {
  source     = "./modules/network"
  aws_region = var.aws_region
  name       = var.name
}

module "alb" {
  source                       = "./modules/alb"
  predictor_alb_security_group = module.network.predictor_alb_security_group
  dashboard_alb_security_group = module.network.dashboard_alb_security_group
  alb_subnets                  = module.network.public_subnets
  vpc_id                       = module.network.vpc_id
  name                         = var.name
}


module "ecs" {
  source                            = "./modules/ecs"
  private_subnets                   = module.network.private_subnets
  predictor_security_group          = module.network.predictor_security_group
  predictor_target_group_arn        = module.alb.predictor_target_group_arn
  predictor_canary_target_group_arn = module.alb.predictor_canary_target_group_arn
  dashboard_security_group          = module.network.dashboard_security_group
  dashboard_target_group_arn        = module.alb.dashboard_target_group_arn
  prometheus_security_group         = module.network.prometheus_security_group
  pushgateway_security_group        = module.network.pushgateway_security_group
  ml_pipeline_ecr_uri               = module.ecr.ml_pipeline_ecr_uri
  predictor_ecr_uri                 = module.ecr.predictor_ecr_uri
  predictor_canary_ecr_uri          = module.ecr.predictor_canary_ecr_uri
  grafana_ecr_uri                   = module.ecr.grafana_ecr_uri
  prometheus_ecr_uri                = module.ecr.prometheus_ecr_uri
  pushgateway_ecr_uri               = module.ecr.pushgateway_ecr_uri
  fluentd_ecr_uri                   = module.ecr.fluentd_ecr_uri
  ecs_exporter_ecr_uri              = module.ecr.ecs_exporter_ecr_uri
  ecs_task_role_arn                 = module.iam.ecs_task_role_arn
  ecs_task_execution_role_arn       = module.iam.ecs_task_execution_role_arn
  name                              = var.name
}


module "stepfunctions" {
  source                            = "./modules/stepfunctions"
  stepfunctions_role_arn            = module.iam.step_functions_role_arn
  event_bridge_role_arn             = module.iam.event_bridge_role_arn
  task_definition_arn               = module.ecs.ml_pipeline_task_definition_arn
  update_server_task_definition_arn = module.ecs.update_server_task_definition_arn
  cluster_arn                       = module.ecs.cluster_arn
  security_group                    = module.network.ml_pipeline_security_group
  subnet                            = module.network.ml_pipeline_subnet
  name                              = var.name
}
