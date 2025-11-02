variable "vultr_api_key" {
  description = "Vultr API key for authentication"
  type        = string
  sensitive   = true
}

variable "environment_name" {
  description = "Name of the environment (e.g., production, staging)"
  type        = string
  default     = "production"

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

variable "vultr_region" {
  description = "Vultr region code (e.g., nrt, ewr, mia, sjc)"
  type        = string
  default     = "nrt"

  validation {
    condition     = can(regex("^[a-z]{3}$", var.vultr_region))
    error_message = "Region code must be 3 lowercase letters."
  }
}

variable "instance_type" {
  description = "Vultr instance type/plan (e.g., 'Regular Cloud Compute - 2GB - 1 vCPU')"
  type        = string
  default     = "Cloud Compute - 2GB - 1 vCPU"

  validation {
    condition     = length(var.instance_type) > 0
    error_message = "Instance type cannot be empty."
  }
}

variable "vm_count" {
  description = "Number of VM instances to create"
  type        = number
  default     = 1

  validation {
    condition     = var.vm_count > 0 && var.vm_count <= 10
    error_message = "VM count must be between 1 and 10."
  }
}

variable "ssh_key_path" {
  description = "Path to the SSH public key file"
  type        = string

  validation {
    condition     = can(file(var.ssh_key_path))
    error_message = "SSH key path must point to a valid file."
  }
}

variable "allowed_ssh_cidr" {
  description = "CIDR block allowed for SSH access (default: 0.0.0.0/0 for open access)"
  type        = string
  default     = "0.0.0.0/0"

  validation {
    condition     = can(cidrhost(var.allowed_ssh_cidr, 0))
    error_message = "SSH CIDR must be a valid CIDR block."
  }
}

variable "enable_reserved_ip" {
  description = "Enable reserved IP addresses for instances"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default = {
    Project     = "dx-predictor"
    ManagedBy   = "Terraform"
  }
}
