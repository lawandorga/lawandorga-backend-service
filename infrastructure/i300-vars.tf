variable "name" {
  default = "lawandorga-backend-service"
  type = string
}

variable "certificate_name" {
  type = string
  default = "backend-certificate"
}

variable "image_version" {
  type = string
}
