provider "scaleway" {
  access_key = var.scw_access_key
  secret_key = var.scw_secret_key
  project_id = var.scw_project_id
  zone       = "fr-par-1"
  region     = "fr-par"
}

data "terraform_remote_state" "cluster" {
  backend = "s3"
  config = {
    bucket                      = "lawandorga-main-infrastructure"
    key                         = "cluster.tfstate"
    region                      = "fr-par"
    endpoint                    = "https://s3.fr-par.scw.cloud"
    skip_region_validation      = true
    skip_credentials_validation = true
  }
}

data "terraform_remote_state" "cert_manager" {
  backend = "s3"
  config = {
    bucket                      = "lawandorga-main-infrastructure"
    key                         = "cert-manager.tfstate"
    region                      = "fr-par"
    endpoint                    = "https://s3.fr-par.scw.cloud"
    skip_region_validation      = true
    skip_credentials_validation = true
  }
}

data "scaleway_k8s_cluster" "cluster" {
  cluster_id = data.terraform_remote_state.cluster.outputs.cluster_id
}

provider "kubernetes" {
  host                   = data.scaleway_k8s_cluster.cluster.kubeconfig.0.host
  token                  = data.scaleway_k8s_cluster.cluster.kubeconfig.0.token
  cluster_ca_certificate = base64decode(data.scaleway_k8s_cluster.cluster.kubeconfig.0.cluster_ca_certificate)
}

provider "helm" {
  kubernetes {
    host                   = data.scaleway_k8s_cluster.cluster.kubeconfig.0.host
    token                  = data.scaleway_k8s_cluster.cluster.kubeconfig.0.token
    cluster_ca_certificate = base64decode(data.scaleway_k8s_cluster.cluster.kubeconfig.0.cluster_ca_certificate)
  }
}
