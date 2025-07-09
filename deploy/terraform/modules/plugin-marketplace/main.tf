resource "helm_release" "plugin_marketplace" {
  name       = "plugin-marketplace"
  chart      = "${path.module}/../../../helm/plugin-marketplace"
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
