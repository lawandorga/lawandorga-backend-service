resource "kubernetes_service_v1" "service" {
  metadata {
    name = var.name
  }
  spec {
    selector = {
      app = kubernetes_deployment_v1.deployment.spec.0.selector.0.match_labels.app
    }
    port {
      name        = "http"
      port        = 80
      target_port = 8080
    }
  }
}
