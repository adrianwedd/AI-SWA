variable "kubeconfig" {
  description = "Path to kubeconfig file"
  type        = string
  default     = "~/.kube/config"
}

variable "namespace" {
  description = "Kubernetes namespace to deploy into"
  type        = string
  default     = "ai-swa"
}

variable "orchestrator_image_tag" {
  type    = string
  default = "latest"
}

variable "worker_image_tag" {
  type    = string
  default = "latest"
}

variable "broker_image_tag" {
  type    = string
  default = "latest"
}

variable "plugin_marketplace_image_tag" {
  type    = string
  default = "latest"
}

variable "orchestrator_replicas" {
  type    = number
  default = 1
}

variable "worker_replicas" {
  type    = number
  default = 1
}

variable "broker_replicas" {
  type    = number
  default = 1
}

variable "plugin_marketplace_replicas" {
  type    = number
  default = 1
}
