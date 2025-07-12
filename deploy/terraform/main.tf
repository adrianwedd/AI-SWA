terraform {
  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = ">= 2.9.0"
    }
  }
}

provider "helm" {
  kubernetes {
    config_path = var.kubeconfig
  }
}

module "orchestrator" {
  source         = "./modules/orchestrator"
  namespace      = var.namespace
  image_tag      = var.orchestrator_image_tag
  replica_count  = var.orchestrator_replicas
}

module "worker" {
  source         = "./modules/worker"
  namespace      = var.namespace
  image_tag      = var.worker_image_tag
  replica_count  = var.worker_replicas
}

module "broker" {
  source         = "./modules/broker"
  namespace      = var.namespace
  image_tag      = var.broker_image_tag
  replica_count  = var.broker_replicas
}

module "plugin_marketplace" {
  source         = "./modules/plugin-marketplace"
  namespace      = var.namespace
  image_tag      = var.plugin_marketplace_image_tag
  replica_count  = var.plugin_marketplace_replicas
}

module "prometheus" {
  source    = "./modules/prometheus"
  namespace = var.namespace
}

module "grafana" {
  source    = "./modules/grafana"
  namespace = var.namespace
}
