# 🌍 Phase 4 - Root Infrastructure Configuration
# ScriptSynthCore Multi-Cloud Kubernetes Platform

terraform {
  required_version = ">= 1.8"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Terraform Cloud/Enterprise backend configuration
  # Uncomment and configure for production use
  # backend "remote" {
  #   organization = "your-org"
  #   workspaces {
  #     name = "scriptsynthcore-${var.environment}"
  #   }
  # }
  
  # S3 backend configuration (alternative)
  # backend "s3" {
  #   bucket         = "scriptsynthcore-terraform-state"
  #   key            = "infrastructure/${var.environment}/terraform.tfstate"
  #   region         = "us-west-2"
  #   encrypt        = true
  #   dynamodb_table = "scriptsynthcore-terraform-locks"
  # }
}

# Configure AWS Provider
provider "aws" {
  region = var.region
  
  default_tags {
    tags = {
      Project     = "ScriptSynthCore"
      Phase       = "4"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = "DevOps"
    }
  }
}

# Local values
locals {
  name_prefix = "${var.project_name}-${var.environment}"
  
  common_tags = {
    Project     = "ScriptSynthCore"
    Phase       = "4"
    Environment = var.environment
    Region      = var.region
    ManagedBy   = "Terraform"
    CreatedAt   = timestamp()
  }
}

# Network Module
module "network" {
  source = "./network"
  
  environment            = var.environment
  project_name          = var.project_name
  region                = var.region
  availability_zones    = var.availability_zones
  vpc_cidr              = var.vpc_cidr
  private_subnet_cidrs  = var.private_subnet_cidrs
  public_subnet_cidrs   = var.public_subnet_cidrs
  enable_nat_gateway    = var.enable_nat_gateway
  enable_dns_hostnames  = var.enable_dns_hostnames
  enable_dns_support    = var.enable_dns_support
  enable_flow_logs      = var.enable_flow_logs
  
  tags = local.common_tags
}

# EKS Module
module "eks" {
  source = "./eks"
  
  # Pass through variables
  environment   = var.environment
  project_name  = var.project_name
  region        = var.region
  
  # Network configuration from network module
  vpc_id                               = module.network.vpc_id
  private_subnet_ids                   = module.network.private_subnet_ids
  public_subnet_ids                    = module.network.public_subnet_ids
  eks_control_plane_security_group_id  = module.network.eks_control_plane_security_group_id
  eks_nodes_security_group_id          = module.network.eks_nodes_security_group_id
  
  # EKS configuration
  cluster_version                      = var.cluster_version
  cluster_endpoint_private_access      = var.cluster_endpoint_private_access
  cluster_endpoint_public_access       = var.cluster_endpoint_public_access
  cluster_endpoint_public_access_cidrs = var.cluster_endpoint_public_access_cidrs
  cluster_log_types                    = var.cluster_log_types
  cluster_log_retention_days           = var.cluster_log_retention_days
  
  # Node groups
  node_groups = var.node_groups
  
  # Add-ons
  cluster_addons = var.cluster_addons
  
  # IRSA
  enable_irsa = var.enable_irsa
  irsa_roles  = var.irsa_roles
  
  # Karpenter
  enable_karpenter   = var.enable_karpenter
  karpenter_version  = var.karpenter_version
  
  # Monitoring
  enable_cloudwatch_logging = var.enable_cloudwatch_logging
  enable_prometheus         = var.enable_prometheus
  
  # Security
  enable_encryption_at_rest = var.enable_encryption_at_rest
  kms_key_id               = var.kms_key_id
  
  tags = local.common_tags
  
  depends_on = [module.network]
} 