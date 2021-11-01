variable "kubernetes_cluster" {  
  description = "the name of the cluster, in domain name format (eg: kube.sslocal.com)"
}

variable "aws_region" {  
  default = "us-east-1"
}

variable "environment" {
}

variable "node_type" {
  default = "cache.m5.large"
}

variable "vpc_name"                 { default = "ShipStation" }
variable "alarm_sns_name"           { default = "PagerDutyCritical" }
variable "engine_version"           { default = "5.0.6" }
variable "parameter_group_family"   { default = "redis5.0" }
variable "maxmemory_policy"         { default = "volatile-lru" }
variable "idle_connection_timeout"  { default = "300" }
variable "initial_replica_count"    { default = "2" }

variable "subnet_names" { 
  type = list 
  default = ["Production-PrivateSubnetA",
             "Production-PrivateSubnetB",
             "Production-PrivateSubnetE"]
}

variable security_groups {
  default = [ "sg-2a7f6c48" ]
}
