resource "helm_release" "orchestrator" {
  name       = "orchestrator"
  chart      = "${path.module}/../../../helm/orchestrator"
  namespace  = var.namespace

  set {
    name  = "image.tag"
    value = var.image_tag
  }

  set {
    name  = "replicaCount"
    value = var.replica_count
  }
}
