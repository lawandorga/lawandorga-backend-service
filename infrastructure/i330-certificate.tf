resource "kubernetes_manifest" "certificate" {
  manifest = yamldecode(templatefile(
    "${path.module}/i331-certificate.yml",
    {
      issuer_name = "${data.terraform_remote_state.cert_manager.outputs.cluster_issuer_name}"
      name        = "${var.certificate_name}"
    }
  ))
}
