resource "helm_release" "broker" {
  name       = "broker"
  chart      = "${path.module}/../../../helm/broker"
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
