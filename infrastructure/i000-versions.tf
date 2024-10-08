terraform {
  required_providers {
    scaleway = {
      source  = "scaleway/scaleway"
      version = "~> 2.13"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.18"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.9"
    }
  }
  backend "s3" {
    bucket                      = "lawandorga-main-infrastructure"
    key                         = "lawandorga-backend-service.tfstate"
    region                      = "fr-par"
    skip_region_validation      = true
    skip_credentials_validation = true
    skip_requesting_account_id  = true
    skip_metadata_api_check     = true

    # to get this working you need to set the keys as environment variables
    # export AWS_ACCESS_KEY_ID="..."
    # export AWS_SECRET_ACCESS_KEY="..."

    endpoints = {
      s3 = "https://s3.fr-par.scw.cloud"
    }
  }
  required_version = ">= 1.0.0"
}
