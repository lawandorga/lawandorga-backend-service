resource "kubernetes_manifest" "backend_cors_policy" {
  manifest = {
    apiVersion = "gateway.envoyproxy.io/v1alpha1"
    kind       = "SecurityPolicy"
    metadata = {
      name      = "${var.name}-cors"
      namespace = "default"
    }
    spec = {
      targetRefs = [
        {
          group = "gateway.networking.k8s.io"
          kind  = "HTTPRoute"
          name  = var.name
        }
      ]
      cors = {
        allowOrigins = [
          "https://www.law-orga.de",
          "https://law-orga.de"
        ]
        allowMethods = [
          "GET",
          "POST",
          "PUT",
          "PATCH",
          "DELETE",
          "OPTIONS"
        ]
        allowHeaders = [
          "accept",
          "accept-encoding",
          "authorization",
          "content-type",
          "dnt",
          "origin",
          "user-agent",
          "x-csrftoken",
          "x-requested-with"
        ]
        allowCredentials = true
        maxAge           = "24h"
      }
    }
  }
}

resource "kubernetes_manifest" "backend_request_policy" {
  manifest = {
    apiVersion = "gateway.envoyproxy.io/v1alpha1"
    kind       = "BackendTrafficPolicy"
    metadata = {
      name      = "${var.name}-limits"
      namespace = "default"
    }
    spec = {
      targetRefs = [
        {
          group = "gateway.networking.k8s.io"
          kind  = "HTTPRoute"
          name  = var.name
        }
      ]
      connection = {
        bufferLimit = "100Mi" # Equivalent to proxy-body-size 100m
      }
    }
  }
}
