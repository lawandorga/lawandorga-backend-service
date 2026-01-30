variable "name" {
  default = "lawandorga-backend-service"
  type = string
}

variable "certificate_name" {
  type = string
  default = "lawandorga-backend-service-certificate"
}

variable "image_version" {
  type = string
}
