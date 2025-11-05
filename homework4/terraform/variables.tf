variable "environment" {
  description = "Deployment environment (vultr or local)"
  type        = string
  validation {
    condition     = contains(["vultr", "local"], var.environment)
    error_message = "Environment must be 'vultr' or 'local'."
  }
}

variable "vm_size" {
  description = "Size of the compute instance (small or medium)"
  type        = string
  default     = "small"
  validation {
    condition     = contains(["small", "medium"], var.vm_size)
    error_message = "VM size must be 'small' or 'medium'."
  }
}

variable "vm_name" {
  description = "Name of the virtual machine"
  type        = string
  default     = "debian-vm"
}

variable "debian_version" {
  description = "Debian version (use latest)"
  type        = string
  default     = "12"
}

variable "vultr_api_key" {
  description = "Vultr API key"
  type        = string
  sensitive   = true
}

variable "vultr_region" {
  description = "Vultr region for deployment"
  type        = string
  default     = "ewr"
}

# Vultr compute sizes mapping
variable "vultr_compute_sizes" {
  description = "Vultr compute plan IDs for different sizes"
  type        = map(string)
  default = {
    small  = "vc2-1c-1gb"   # 1 vCPU, 1GB RAM
    medium = "vc2-2c-2gb"   # 2 vCPU, 2GB RAM
  }
}

# Local VirtualBox VM sizing
variable "libvirt_compute_sizes" {
  description = "LibVirt compute sizes for different VM sizes"
  type        = map(object({
    vcpu   = number
    memory = number
  }))
  default = {
    small  = { vcpu = 1, memory = 1024 }
    medium = { vcpu = 2, memory = 2048 }
  }
}

variable "libvirt_pool_path" {
  description = "Path for libvirt storage pool"
  type        = string
  default     = "/var/lib/libvirt/images"
}

variable "debian_iso_path" {
  description = "Path to Debian ISO for local VirtualBox deployment"
  type        = string
  default     = "/tmp/debian-12-generic-amd64.iso"
}

variable "tags" {
  description = "Tags for resources"
  type        = map(string)
  default = {
    project = "cs330"
    managed = "terraform"
  }
}
