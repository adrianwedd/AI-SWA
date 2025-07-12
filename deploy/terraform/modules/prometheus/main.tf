resource "helm_release" "prometheus" {
  name       = "prometheus"
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "prometheus"
  namespace  = var.namespace

  set {
    name  = "server.service.type"
    value = "ClusterIP"
  }
}
