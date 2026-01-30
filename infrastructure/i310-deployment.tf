resource "kubernetes_deployment_v1" "deployment" {
  metadata {
    name = var.name
    labels = {
      app = var.name
    }
  }

  spec {
    replicas = 2

    selector {
      match_labels = {
        app = var.name
      }
    }

    template {
      metadata {
        labels = {
          app = var.name
        }
      }

      spec {
        image_pull_secrets {
          name = data.terraform_remote_state.cluster.outputs.image_pull_secret_name
        }

        container {
          image = "${data.terraform_remote_state.cluster.outputs.registry_endpoint}/${var.name}:${var.image_version}"
          name  = "${var.name}-container"

          env_from {
            secret_ref {
              name = kubernetes_manifest.secret.manifest["metadata"]["name"]
            }
          }
          env {
            name  = "PIPELINE_IMAGE"
            value = var.image_version
          }
          env {
            name  = "PIPELINE_SERVICE"
            value = var.name
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
