# Terraform IaC for CS330 Homework4 - Deployment Guide

## Overview

This Terraform configuration allows you to deploy Debian VMs to either:
1. **Vultr Cloud** - Public cloud deployment
2. **Local VirtualBox** - Local development/testing via libvirt/KVM

## Prerequisites

### For Vultr Deployment
```bash
# Install Terraform
# On Ubuntu/Debian
sudo apt-get install terraform

# Install Vultr CLI (optional but helpful)
pip install vultr-cli
```

You'll need:
- Vultr account with API key
- API key set via environment variable: `export TF_VAR_vultr_api_key="your-key"`

### For Local VirtualBox Deployment
```bash
# Install libvirt and QEMU
sudo apt-get install libvirt-daemon libvirt-daemon-system qemu qemu-kvm

# Start libvirt service
sudo systemctl start libvirtd
sudo systemctl enable libvirtd

# Give your user permission to use libvirt (optional)
sudo usermod -a -G libvirt $USER
# You may need to log out and back in for this to take effect
```

## Directory Structure

```
terraform/
├── versions.tf              # Provider versions and requirements
├── providers.tf             # Provider configurations
├── variables.tf             # Input variables
├── main.tf                  # Main infrastructure resources
├── outputs.tf               # Output values
├── terraform.tfvars.vultr.example    # Example Vultr config
├── terraform.tfvars.local.example    # Example local config
├── deploy.sh                # Helper script for deployment
└── README.md                # This file
```

## Configuration Variables

### Available Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `environment` | string | - | Deployment target: `vultr` or `local` |
| `vm_size` | string | `small` | VM size: `small` (1vCPU/1GB) or `medium` (2vCPU/2GB) |
| `vm_name` | string | `debian-vm` | Name for the VM |
| `debian_version` | string | `12` | Debian version to deploy |
| `vultr_api_key` | string (sensitive) | - | Vultr API key (set via env var) |
| `vultr_region` | string | `ewr` | Vultr region (ewr, lax, ord, ams, lon, sjc, syd, sgp, etc.) |

## Quick Start

### 1. Initialize Terraform

```bash
cd terraform
./deploy.sh init
```

Or manually:
```bash
terraform init
```

### 2. Deploy to Vultr

Create your configuration file:
```bash
cp terraform.tfvars.vultr.example terraform.tfvars
# Edit terraform.tfvars to customize
```

Set your API key:
```bash
export TF_VAR_vultr_api_key="your-vultr-api-key"
```

Plan and apply:
```bash
./deploy.sh plan vultr
./deploy.sh apply vultr
```

Or manually:
```bash
terraform plan -var="environment=vultr" -var-file="terraform.tfvars"
terraform apply -var="environment=vultr" -var-file="terraform.tfvars"
```

### 3. Deploy to Local VirtualBox

Create your configuration file:
```bash
cp terraform.tfvars.local.example terraform.tfvars
# Edit terraform.tfvars to customize
```

Plan and apply:
```bash
./deploy.sh plan local
./deploy.sh apply local
```

Or manually:
```bash
terraform plan -var="environment=local" -var-file="terraform.tfvars"
terraform apply -var="environment=local" -var-file="terraform.tfvars"
```

## Helper Script Usage

The `deploy.sh` script simplifies common operations:

```bash
# Initialize Terraform
./deploy.sh init

# Validate configuration
./deploy.sh validate

# Format files
./deploy.sh fmt

# Plan deployment
./deploy.sh plan vultr
./deploy.sh plan local

# Apply deployment
./deploy.sh apply vultr
./deploy.sh apply local

# Show current state
./deploy.sh show

# Show outputs
./deploy.sh output
./deploy.sh output vultr_vm_ip

# Destroy deployment
./deploy.sh destroy vultr
./deploy.sh destroy local

# Show help
./deploy.sh help
```

## Accessing Deployed VMs

### Vultr VM

After deployment, retrieve connection details:
```bash
terraform output vultr_vm_details
# Or via the helper script
./deploy.sh output vultr_vm_ip
```

SSH into your VM:
```bash
ssh root@<vultr_vm_ip>
```

### Local VirtualBox VM

Retrieve the IP address:
```bash
terraform output libvirt_vm_ip
# Or via the helper script
./deploy.sh output libvirt_vm_ip
```

SSH into your VM:
```bash
ssh -u debian@<local_vm_ip>  # or check VM console for credentials
```

View VM console via libvirt:
```bash
virsh console debian-vm
```

## VM Size Reference

### Small Instance
- **Vultr**: vc2-1c-1gb (1 vCPU, 1GB RAM)
- **Local**: 1 vCPU, 1024MB RAM

### Medium Instance
- **Vultr**: vc2-2c-2gb (2 vCPU, 2GB RAM)
- **Local**: 2 vCPU, 2048MB RAM

## Common Workflows

### Development on Local, Test on Vultr

1. Start local development:
   ```bash
   ./deploy.sh apply local
   ```

2. Test changes, verify configuration works

3. Deploy to production Vultr:
   ```bash
   ./deploy.sh apply vultr
   ```

4. Verify in production

5. Clean up local resources when done:
   ```bash
   ./deploy.sh destroy local
   ```

### Scaling

To change VM size in production:

1. Update `terraform.tfvars`:
   ```
   vm_size = "medium"
   ```

2. Plan and apply:
   ```bash
   terraform plan
   terraform apply
   ```

## Troubleshooting

### Vultr API Authentication Error
- Verify API key is set: `echo $TF_VAR_vultr_api_key`
- Check key is valid in Vultr dashboard

### LibVirt/KVM Not Running
```bash
sudo systemctl start libvirtd
sudo systemctl status libvirtd
```

### Permission Denied on libvirt
```bash
# Add user to libvirt group
sudo usermod -a -G libvirt $USER
# Log out and back in
```

### Terraform State Issues
If you need to reset:
```bash
rm -rf .terraform terraform.tfstate*
./deploy.sh init
```

## Next Steps

After deployment:
1. Configure SSH access and security groups
2. Install your application software
3. Set up monitoring and backups
4. Consider using Ansible for configuration management
5. Integrate with CI/CD pipeline

## References

- [Terraform Docs](https://www.terraform.io/docs)
- [Vultr Provider](https://registry.terraform.io/providers/vultr/vultr/latest/docs)
- [LibVirt Provider](https://registry.terraform.io/providers/dmacvicar/libvirt/latest/docs)
- [Vultr Pricing & Plans](https://www.vultr.com/pricing/)
