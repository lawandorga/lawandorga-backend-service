variable "certificate_name" {
  type = string
  default = "backend-certificate"
}

variable "image_version" {
  type = string
  default = "a241561509f92f42f583d438ee76277f4df8eb50"
}

variable "env_vars" {
  type = map(string)
  sensitive = true
}