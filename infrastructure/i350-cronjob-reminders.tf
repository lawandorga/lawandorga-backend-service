# Runs the send_calendar_reminders management command frequently so reminders
# go out close to their lead time. manage.py defaults to config.settings.local,
# so DJANGO_SETTINGS_MODULE is set below to avoid running against local SQLite.
resource "kubernetes_cron_job_v1" "reminders" {
  metadata {
    name = "${var.name}-reminders"
    labels = {
      app = var.name
    }
  }

  spec {
    schedule                      = "*/5 * * * *"
    concurrency_policy            = "Forbid"
    starting_deadline_seconds     = 300
    successful_jobs_history_limit = 3
    failed_jobs_history_limit     = 3

    job_template {
      metadata {}
      spec {
        backoff_limit = 2

        template {
          metadata {}
          spec {
            image_pull_secrets {
              name = data.terraform_remote_state.cluster.outputs.image_pull_secret_name
            }

            container {
              name    = "${var.name}-reminders"
              image   = "${data.terraform_remote_state.cluster.outputs.registry_endpoint}/${var.name}:${var.image_version}"
              command = ["python", "manage.py", "send_calendar_reminders"]

              env_from {
                secret_ref {
                  name = kubernetes_manifest.secret.manifest["metadata"]["name"]
                }
              }
              env {
                name  = "DJANGO_SETTINGS_MODULE"
                value = "config.settings.production"
              }
            }

            restart_policy = "Never"
          }
        }
      }
    }
  }
}
