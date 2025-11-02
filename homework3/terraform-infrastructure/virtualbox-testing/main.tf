terraform {
  required_version = ">= 1.0"
  required_providers {
    virtualbox = {
      source  = "terra-farm/virtualbox"
      version = "~> 0.2"
    }
  }
}

provider "virtualbox" {
  delay      = 60
  mintimeout = 2
}

# Local variables
locals {
  vm_name_prefix = "${var.environment_name}-vm"
  debian_image   = "debian-${var.debian_version}-generic-amd64.qcow2"
}

# Create base network interface
resource "virtualbox_vm" "node" {
  count  = var.vm_count
  name   = "${local.vm_name_prefix}-${count.index + 1}"
  image  = "file://${var.vm_image_path}/${local.debian_image}"
  cpus   = var.vm_cpus
  memory = var.vm_memory_mb

  network_adapter {
    type           = "nat"
    host_interface = "vboxnet0"
  }

  # Storage configuration
  storage = [
    {
      name = "SATA"
      type = "SATA"
    }
  ]

  # VirtualBox specific settings
  boot_order = ["disk"]

  tags = {
    Environment = var.environment_name
    Project     = "dx-predictor"
    Index       = count.index + 1
  }
}

# Output VM details
resource "null_resource" "vm_info" {
  count = var.vm_count

  provisioner "local-exec" {
    command = "echo 'VM ${virtualbox_vm.node[count.index].name} created with IP: ${virtualbox_vm.node[count.index].network_adapter[0].ipv4_address}'"
  }
}
