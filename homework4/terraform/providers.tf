terraform {
  backend "local" {
    path = "terraform.tfstate"
  }
}

# Vultr Provider Configuration
provider "vultr" {
  api_key = var.vultr_api_key
  rate_limit = 100
  retry_limit = 3
}

# LibVirt Provider Configuration (for local VirtualBox deployment)
provider "libvirt" {
  uri = "qemu:///system"
}
