resource "kubernetes_ingress_v1" "ingress" {
  metadata {
    name = "lawandorga-backend-service"
    annotations = {
      "nginx.ingress.kubernetes.io/enable-cors"        = "true"
      "nginx.ingress.kubernetes.io/cors-allow-headers" = "accept, accept-encoding, authorization, content-type, dnt, origin, user-agent, x-csrftoken, x-requested-with"
      "nginx.ingress.kubernetes.io/cors-allow-origin"  = "https://www.law-orga.de, https://law-orga.de"
      "nginx.ingress.kubernetes.io/proxy-body-size"    = "100m"
      "nginx.org/proxy-read-timeout"                   = "240"
      "nginx.org/proxy-send-timeout"                   = "240"
      "nginx.org/proxy-connect-timeout"                = "240"
      "nginx.org/proxy-next-upstream-timeout"          = "240"
      # this allows for too big files that the frontend shows the correct error and can read the 413 status code
      # "nginx.ingress.kubernetes.io/server-snippet" = <<-EOF
      #   error_page 413 /custom_413.html;
      #   location = /custom_413.html {
      #     add_header Access-Control-Allow-Origin "https://www.law-orga.de" always;
      #     add_header Access-Control-Allow-Credentials "true" always;
      #   }
      # EOF
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
