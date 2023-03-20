variable "certificate_name" {
  type = string
  default = "backend-certificate"
}

variable "image_version" {
  type = string
}

variable "env_vars" {
  type = map(string)
  sensitive = true
}
