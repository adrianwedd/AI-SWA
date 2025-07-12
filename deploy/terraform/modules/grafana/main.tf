resource "helm_release" "grafana" {
  name       = "grafana"
  repository = "https://grafana.github.io/helm-charts"
  chart      = "grafana"
  namespace  = var.namespace

  set {
    name  = "service.type"
    value = "ClusterIP"
  }
}
