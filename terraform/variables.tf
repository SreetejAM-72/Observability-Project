variable "region" {
  default = "us-east-1"
}

variable "new_relic_api_key" {
  type      = string
  sensitive = true
}

variable "new_relic_account_id" {
  type = string
}