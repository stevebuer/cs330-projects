terraform {
  required_version = ">= 1.0"

  required_providers {
    vultr = {
      source  = "vultr/vultr"
      version = "~> 2.0"
    }
    libvirt = {
      source  = "dmacvicar/libvirt"
      version = "~> 0.7"
    }
  }
}
