resource "kubernetes_deployment_v1" "deployment" {
  metadata {
    name = "lawandorga-backend-service"
    labels = {
      app = "lawandorga-backend-service"
    }
  }

  spec {
    replicas = 2

    selector {
      match_labels = {
        app = "lawandorga-backend-service"
      }
    }

    template {
      metadata {
        labels = {
          app = "lawandorga-backend-service"
        }
      }

      spec {
        image_pull_secrets {
          name = data.terraform_remote_state.cluster.outputs.image_pull_secret_name
        }

        container {
          image = "${data.terraform_remote_state.cluster.outputs.registry_endpoint}/lawandorga-backend-service:${var.image_version}"
          name  = "lawandorga-backend-service-container"

          dynamic "env" {
            for_each = nonsensitive(toset(keys(var.env_vars)))
            content {
              name  = env.key
              value = var.env_vars[env.key]
            }
          }

          port {
            container_port = 8080
          }

          readiness_probe {
            http_get {
              path = "/"
              port = 8080
              http_header {
                name  = "Host"
                value = "backend.law-orga.de"
              }
            }
          }
        }
      }
    }
  }
}
