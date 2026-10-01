terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
  }
}

provider "local" {}

resource "local_file" "hello_world" {
  filename = "${path.module}/output.txt"
  content  = "Hello World from Terraform!"
}
