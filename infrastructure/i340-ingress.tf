resource "kubernetes_ingress_v1" "ingress" {
  metadata {
    name = "lawandorga-backend-service"
    annotations = {
      # "nginx.ingress.kubernetes.io/configuration-snippet"  = "more_set_headers 'Access-Control-Allow-Origin: $http_origin'"
      # "nginx.ingress.kubernetes.io/cors-allow-origin"      = "*"
      # "nginx.ingress.kubernetes.io/cors-allow-credentials" = "true"
      # "nginx.ingress.kubernetes.io/cors-allow-methods"     = "PUT, GET, POST, OPTIONS, DELETE, PATCH"
      "nginx.ingress.kubernetes.io/enable-cors"        = "true"
      "nginx.ingress.kubernetes.io/cors-allow-headers" = "accept, accept-encoding, authorization, content-type, dnt, origin, user-agent, x-csrftoken, x-requested-with, baggage, sentry-trace"
      "nginx.ingress.kubernetes.io/cors-allow-origin"  = "https://www.law-orga.de, https://law-orga.de"
    }
  }

  spec {
    rule {
      host = "auth.law-orga.de"
      http {
        path {
          backend {
            service {
              name = kubernetes_service_v1.service.metadata.0.name
              port {
                number = 80
              }
            }
          }
        }
      }
    }
    rule {
      host = "backend.law-orga.de"
      http {
        path {
          backend {
            service {
              name = kubernetes_service_v1.service.metadata.0.name
              port {
                number = 80
              }
            }
          }
        }
      }
    }
    rule {
      host = "calendar.law-orga.de"
      http {
        path {
          backend {
            service {
              name = kubernetes_service_v1.service.metadata.0.name
              port {
                number = 80
              }
            }
          }
        }
      }
    }
    tls {
      hosts       = ["auth.law-orga.de", "backend.law-orga.de", "calendar.law-orga.de"]
      secret_name = var.certificate_name
    }
  }
}

