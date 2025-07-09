resource "helm_release" "worker" {
  name       = "worker"
  chart      = "${path.module}/../../../helm/worker"
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
