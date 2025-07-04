# 🌍 Phase 4 - Root Infrastructure Variables
# ScriptSynthCore Multi-Cloud Platform Configuration

# Global Configuration
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "scriptsynthcore"
  
  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.project_name))
    error_message = "Project name must contain only lowercase letters, numbers, and hyphens."
  }
}

variable "region" {
  description = "AWS region for infrastructure deployment"
  type        = string
  default     = "us-west-2"
}

# Network Configuration
variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-west-2a", "us-west-2b", "us-west-2c"]
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
  
  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "VPC CIDR must be a valid IPv4 CIDR block."
  }
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnets"
  type        = bool
  default     = true
}

variable "enable_dns_hostnames" {
  description = "Enable DNS hostnames in VPC"
  type        = bool
  default     = true
}

variable "enable_dns_support" {
  description = "Enable DNS support in VPC"
  type        = bool
  default     = true
}

variable "enable_flow_logs" {
  description = "Enable VPC Flow Logs"
  type        = bool
  default     = true
}

# EKS Configuration
variable "cluster_version" {
  description = "Kubernetes version for EKS cluster"
  type        = string
  default     = "1.30"
}

variable "cluster_endpoint_private_access" {
  description = "Enable private API server endpoint"
  type        = bool
  default     = true
}

variable "cluster_endpoint_public_access" {
  description = "Enable public API server endpoint"
  type        = bool
  default     = true
}

variable "cluster_endpoint_public_access_cidrs" {
  description = "CIDR blocks that can access the public API server endpoint"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "cluster_log_types" {
  description = "List of control plane logging types to enable"
  type        = list(string)
  default     = ["api", "audit", "authenticator", "controllerManager", "scheduler"]
}

variable "cluster_log_retention_days" {
  description = "CloudWatch log retention period for cluster logs"
  type        = number
  default     = 30
}

# Node Group Configuration
variable "node_groups" {
  description = "EKS node group configurations"
  type = map(object({
    instance_types        = list(string)
    capacity_type        = string
    min_size             = number
    max_size             = number
    desired_size         = number
    disk_size            = number
    ami_type             = string
    labels               = map(string)
    taints = list(object({
      key    = string
      value  = string
      effect = string
    }))
  }))
  default = {
    general = {
      instance_types = ["t3.medium", "t3.large"]
      capacity_type  = "ON_DEMAND"
      min_size       = 1
      max_size       = 10
      desired_size   = 2
      disk_size      = 50
      ami_type       = "AL2_x86_64"
      labels = {
        role = "general"
        workload = "system"
      }
      taints = []
    }
    compute = {
      instance_types = ["c5.large", "c5.xlarge", "c5.2xlarge"]
      capacity_type  = "SPOT"
      min_size       = 0
      max_size       = 20
      desired_size   = 2
      disk_size      = 100
      ami_type       = "AL2_x86_64"
      labels = {
        role = "compute"
        workload = "arena-nodes"
      }
      taints = [{
        key    = "compute-optimized"
        value  = "true"
        effect = "NO_SCHEDULE"
      }]
    }
    gpu = {
      instance_types = ["g4dn.xlarge", "g4dn.2xlarge"]
      capacity_type  = "SPOT"
      min_size       = 0
      max_size       = 5
      desired_size   = 0
      disk_size      = 100
      ami_type       = "AL2_x86_64_GPU"
      labels = {
        role = "gpu"
        workload = "ml-training"
      }
      taints = [{
        key    = "nvidia.com/gpu"
        value  = "true"
        effect = "NO_SCHEDULE"
      }]
    }
  }
}

# Add-ons Configuration
variable "cluster_addons" {
  description = "EKS cluster add-ons configuration"
  type = map(object({
    version               = string
    resolve_conflicts     = string
    service_account_role_arn = string
  }))
  default = {
    coredns = {
      version               = null
      resolve_conflicts     = "OVERWRITE"
      service_account_role_arn = null
    }
    kube-proxy = {
      version               = null
      resolve_conflicts     = "OVERWRITE"
      service_account_role_arn = null
    }
    vpc-cni = {
      version               = null
      resolve_conflicts     = "OVERWRITE"
      service_account_role_arn = null
    }
    aws-ebs-csi-driver = {
      version               = null
      resolve_conflicts     = "OVERWRITE"
      service_account_role_arn = null
    }
  }
}

# IRSA Configuration
variable "enable_irsa" {
  description = "Enable IAM Roles for Service Accounts"
  type        = bool
  default     = true
}

variable "irsa_roles" {
  description = "IRSA roles to create"
  type = map(object({
    namespace                    = string
    service_account_name        = string
    policy_arns                 = list(string)
    inline_policy_statements    = list(object({
      effect    = string
      actions   = list(string)
      resources = list(string)
    }))
  }))
  default = {
    cluster_autoscaler = {
      namespace            = "kube-system"
      service_account_name = "cluster-autoscaler"
      policy_arns         = []
      inline_policy_statements = [{
        effect = "Allow"
        actions = [
          "autoscaling:DescribeAutoScalingGroups",
          "autoscaling:DescribeAutoScalingInstances",
          "autoscaling:DescribeLaunchConfigurations",
          "autoscaling:DescribeTags",
          "autoscaling:SetDesiredCapacity",
          "autoscaling:TerminateInstanceInAutoScalingGroup",
          "ec2:DescribeLaunchTemplateVersions"
        ]
        resources = ["*"]
      }]
    }
    aws_load_balancer_controller = {
      namespace            = "kube-system"
      service_account_name = "aws-load-balancer-controller"
      policy_arns         = []
      inline_policy_statements = [{
        effect = "Allow"
        actions = [
          "iam:CreateServiceLinkedRole",
          "ec2:DescribeAccountAttributes",
          "ec2:DescribeAddresses",
          "ec2:DescribeAvailabilityZones",
          "ec2:DescribeInternetGateways",
          "ec2:DescribeVpcs",
          "ec2:DescribeSubnets",
          "ec2:DescribeSecurityGroups",
          "ec2:DescribeInstances",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DescribeTags",
          "ec2:GetCoipPoolUsage",
          "ec2:DescribeCoipPools",
          "elasticloadbalancing:DescribeLoadBalancers",
          "elasticloadbalancing:DescribeLoadBalancerAttributes",
          "elasticloadbalancing:DescribeListeners",
          "elasticloadbalancing:DescribeListenerCertificates",
          "elasticloadbalancing:DescribeSSLPolicies",
          "elasticloadbalancing:DescribeRules",
          "elasticloadbalancing:DescribeTargetGroups",
          "elasticloadbalancing:DescribeTargetGroupAttributes",
          "elasticloadbalancing:DescribeTargetHealth",
          "elasticloadbalancing:DescribeTags"
        ]
        resources = ["*"]
      }]
    }
    scriptsynthcore_arena = {
      namespace            = "scriptsynthcore"
      service_account_name = "arena-service-account"
      policy_arns         = []
      inline_policy_statements = [{
        effect = "Allow"
        actions = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket",
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        resources = [
          "arn:aws:s3:::scriptsynthcore-*",
          "arn:aws:s3:::scriptsynthcore-*/*",
          "arn:aws:dynamodb:*:*:table/scriptsynthcore-*",
          "arn:aws:secretsmanager:*:*:secret:scriptsynthcore-*"
        ]
      }]
    }
  }
}

# Karpenter Configuration
variable "enable_karpenter" {
  description = "Enable Karpenter for node auto-scaling"
  type        = bool
  default     = true
}

variable "karpenter_version" {
  description = "Karpenter version to install"
  type        = string
  default     = "v0.37.0"
}

# Monitoring and Observability
variable "enable_cloudwatch_logging" {
  description = "Enable CloudWatch container insights"
  type        = bool
  default     = true
}

variable "enable_prometheus" {
  description = "Enable Prometheus monitoring"
  type        = bool
  default     = true
}

# Security
variable "enable_encryption_at_rest" {
  description = "Enable encryption at rest for EKS secrets"
  type        = bool
  default     = true
}

variable "kms_key_id" {
  description = "KMS key ID for EKS encryption (if not provided, AWS managed key will be used)"
  type        = string
  default     = null
} 