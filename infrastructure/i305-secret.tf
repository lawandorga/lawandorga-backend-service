resource "kubernetes_manifest" "secret" {
  manifest = {
    apiVersion = "external-secrets.io/v1"
    kind       = "ExternalSecret"
    metadata = {
      name      = var.name
      namespace = "default"
    }
    spec = {
      refreshInterval = "1h0m0s"
      secretStoreRef = {
        name = data.terraform_remote_state.secrets.outputs.scaleway_cluster_secret_store_name
        kind = "ClusterSecretStore"
      }
      target = {
        name           = var.name
        creationPolicy = "Owner"
      }
      dataFrom = [
        {
          extract = {
            key = "id:5bbadfac-8fb9-47e5-855b-41397c621b56"
          }
        }
      ]
    }
  }
}
