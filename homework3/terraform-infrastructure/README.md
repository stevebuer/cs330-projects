# Terraform Infrastructure as Code

Infrastructure management for CS 330 DX Predictor Project using Terraform.

## Overview

This project manages two environments:
- **Vultr Production**: Cloud-based production deployment
- **Virtualbox Testing**: Local testing environment

Both environments use the latest Debian OS for consistency.

## Prerequisites

- Terraform >= 1.0
- Vultr API token (for production)
- Virtualbox installed (for testing)
- Ansible (for configuration management)

## Directory Structure

```
terraform-infrastructure/
├── vultr-production/       # Production environment on Vultr
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── terraform.tfvars.example
├── virtualbox-testing/     # Local testing in Virtualbox
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── terraform.tfvars.example
├── modules/                # Reusable Terraform modules
│   ├── debian-vm/         # Base Debian VM module
│   ├── networking/        # Network configuration
│   └── docker-host/       # Docker host setup
└── README.md
```

## Getting Started

### Production Environment (Vultr)

1. Set up Vultr credentials:
   ```bash
   export VULTR_API_KEY="your-api-key"
   ```

2. Configure variables:
   ```bash
   cd vultr-production
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your settings
   ```

3. Plan and apply:
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

### Testing Environment (Virtualbox)

1. Install Virtualbox and Packer:
   ```bash
   sudo apt-get install virtualbox
   ```

2. Configure variables:
   ```bash
   cd virtualbox-testing
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your settings
   ```

3. Plan and apply:
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

## Variables

Both environments use similar variables:
- `environment_name`: Environment identifier (e.g., "production", "testing")
- `debian_version`: Debian release version (default: "bookworm" - latest)
- `vm_count`: Number of VMs to create
- `instance_type`: Instance type/size
- `ssh_key_path`: Path to SSH public key

## Outputs

Both configurations output:
- VM IP addresses
- SSH connection strings
- DNS names (if applicable)

## State Management

Terraform state files are local by default. For team environments, configure remote state:

```bash
# Example: Use Vultr Object Storage
terraform {
  backend "s3" {
    bucket         = "your-bucket"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    endpoint       = "https://vultrobjectstorage.com"
    skip_region_validation = true
  }
}
```

## Deployment Steps

### First Time Setup

1. Initialize Terraform:
   ```bash
   cd <environment>
   terraform init
   ```

2. Create terraform.tfvars from template:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

3. Review plan:
   ```bash
   terraform plan
   ```

4. Apply configuration:
   ```bash
   terraform apply
   ```

### Updates and Changes

1. Modify `.tf` files as needed
2. Review changes:
   ```bash
   terraform plan
   ```
3. Apply updates:
   ```bash
   terraform apply
   ```

### Destroying Infrastructure

```bash
terraform destroy
```

## Best Practices

- Always run `terraform plan` before `apply`
- Keep `terraform.tfvars` in `.gitignore`
- Use variable validation where possible
- Tag all resources for organization
- Document any custom configurations
- Use consistent naming conventions

## Troubleshooting

### Vultr-specific Issues
- Verify API key permissions
- Check rate limiting (429 errors)
- Ensure correct region is specified

### Virtualbox-specific Issues
- Ensure sufficient disk space
- Check Virtualbox VM resource limits
- Verify network bridge configuration

## Contributing

When adding new infrastructure:
1. Create reusable modules in `modules/`
2. Update documentation
3. Test in testing environment first
4. Deploy to production

## References

- [Terraform Documentation](https://www.terraform.io/docs)
- [Vultr Terraform Provider](https://registry.terraform.io/providers/vultr/vultr/latest/docs)
- [Virtualbox Terraform Provider](https://registry.terraform.io/providers/terra-farm/virtualbox/latest/docs)
- [Debian Latest Release](https://www.debian.org/releases/stable/)
