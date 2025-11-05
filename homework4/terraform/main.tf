# Vultr VM Deployment
resource "vultr_instance" "debian_vm" {
  count              = var.environment == "vultr" ? 1 : 0
  label              = var.vm_name
  plan               = var.vultr_compute_sizes[var.vm_size]
  region             = var.vultr_region
  os_id              = data.vultr_os.debian.id
  enable_ipv6        = true
  backups            = "disabled"
  ddos_protection    = false
  activation_email   = false

  tags = [var.tags.project, var.tags.managed]

  lifecycle {
    create_before_destroy = true
  }
}

# Data source for latest Debian OS
data "vultr_os" "debian" {
  filter {
    name   = "family"
    values = ["debian"]
  }

  filter {
    name   = "name"
    values = ["Debian 12 x64"]
  }
}

# LibVirt Storage Pool (for local deployment)
resource "libvirt_pool" "terraform_pool" {
  count = var.environment == "local" ? 1 : 0
  name  = "terraform-pool"
  type  = "dir"
  path  = var.libvirt_pool_path

  lifecycle {
    ignore_changes = [path]
  }
}

# LibVirt VM Deployment (VirtualBox via KVM/QEMU)
resource "libvirt_volume" "debian_disk" {
  count           = var.environment == "local" ? 1 : 0
  name            = "${var.vm_name}-disk.qcow2"
  pool            = libvirt_pool.terraform_pool[0].name
  size            = 20 * 1024 * 1024 * 1024  # 20GB
  format          = "qcow2"

  lifecycle {
    ignore_changes = [pool]
  }
}

resource "libvirt_domain" "debian_vm" {
  count   = var.environment == "local" ? 1 : 0
  name    = var.vm_name
  memory  = var.libvirt_compute_sizes[var.vm_size].memory
  vcpu    = var.libvirt_compute_sizes[var.vm_size].vcpu
  running = true

  boot {
    dev = ["hd"]
  }

  disk {
    volume_id = libvirt_volume.debian_disk[0].id
  }

  network_interface {
    network_name   = "default"
    wait_for_lease = true
  }

  # Increased timeout for first boot
  timeouts {
    create = "10m"
  }
}
