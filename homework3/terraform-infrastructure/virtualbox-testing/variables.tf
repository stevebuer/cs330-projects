variable "environment_name" {
  description = "Name of the environment"
  type        = string
  default     = "testing"

  validation {
    condition     = length(var.environment_name) > 0 && length(var.environment_name) <= 30
    error_message = "Environment name must be between 1 and 30 characters."
  }
}

variable "debian_version" {
  description = "Debian version to use (e.g., bookworm for latest, bullseye for stable)"
  type        = string
  default     = "bookworm"

  validation {
    condition     = contains(["bookworm", "bullseye", "buster"], var.debian_version)
    error_message = "Debian version must be bookworm, bullseye, or buster."
  }
}

variable "vm_count" {
  description = "Number of VMs to create"
  type        = number
  default     = 1

  validation {
    condition     = var.vm_count > 0 && var.vm_count <= 5
    error_message = "VM count must be between 1 and 5 for testing environment."
  }
}

variable "vm_cpus" {
  description = "Number of CPU cores for each VM"
  type        = number
  default     = 2

  validation {
    condition     = var.vm_cpus > 0 && var.vm_cpus <= 16
    error_message = "CPU count must be between 1 and 16."
  }
}

variable "vm_memory_mb" {
  description = "Amount of memory in MB for each VM"
  type        = number
  default     = 2048

  validation {
    condition     = var.vm_memory_mb >= 512 && var.vm_memory_mb <= 65536
    error_message = "Memory must be between 512MB and 65536MB."
  }
}

variable "vm_image_path" {
  description = "Path to the directory containing Debian VM images"
  type        = string
  default     = "/opt/vms/images"

  validation {
    condition     = can(file(var.vm_image_path))
    error_message = "VM image path must be a valid directory."
  }
}

variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default = {
    Project     = "dx-predictor"
    ManagedBy   = "Terraform"
  }
}
