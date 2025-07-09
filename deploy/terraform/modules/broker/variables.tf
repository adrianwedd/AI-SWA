variable "namespace" {
  type = string
}

variable "image_tag" {
  type    = string
  default = "latest"
}

variable "replica_count" {
  type    = number
  default = 1
}
