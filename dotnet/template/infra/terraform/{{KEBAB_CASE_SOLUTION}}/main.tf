provider "aws" {
  region  = var.aws_region
}

module "vpc-info" {
  source  = "app.terraform.io/shipstation-devops/vpc-info/aws"
  version = "1.0.1"
  vpc_name     = var.vpc_name
  subnet_names = var.subnet_names
}

data "aws_sns_topic" "main" {
  name = var.alarm_sns_name
}
