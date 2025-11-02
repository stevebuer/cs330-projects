# Reusable Debian VM Module

This module provides a base Debian VM configuration that can be used across different environments.

## Usage

```hcl
module "debian_vm" {
  source = "../../modules/debian-vm"

  environment_name = var.environment_name
  instance_name    = "my-vm"
  debian_version   = "bookworm"
  
  # Provider-specific configuration
  providers = {
    vultr = vultr
  }
}
```

## Variables

- `environment_name`: Name of the environment
- `instance_name`: Name for the VM instance
- `debian_version`: Debian release version
- `tags`: Additional resource tags

## Outputs

- `instance_id`: ID of the created instance
- `instance_ip`: IP address of the instance
- `instance_details`: Full instance information
