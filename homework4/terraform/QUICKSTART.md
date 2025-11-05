# Terraform Deployment Quick Reference

## One-Time Setup

```bash
# Install Terraform (if needed)
# Ubuntu/Debian
sudo apt-get install terraform

# For VirtualBox local deployment, install libvirt
sudo apt-get install libvirt-daemon libvirt-daemon-system qemu qemu-kvm

# Start libvirt
sudo systemctl start libvirtd
sudo systemctl enable libvirtd

# Initialize Terraform
cd terraform
./deploy.sh init
```

## Deploy to Vultr

```bash
# 1. Set your Vultr API key
export TF_VAR_vultr_api_key="your-api-key-here"

# 2. Copy and customize config
cp terraform.tfvars.vultr.example terraform.tfvars
# Edit terraform.tfvars as needed (region, vm_size, etc.)

# 3. Plan the deployment
./deploy.sh plan vultr

# 4. Review the output and apply
./deploy.sh apply vultr

# 5. Get connection details
./deploy.sh output vultr_vm_ip

# 6. SSH into your VM
ssh root@<ip-from-step-5>
```

## Deploy to Local VirtualBox

```bash
# 1. Copy and customize config
cp terraform.tfvars.local.example terraform.tfvars

# 2. Plan the deployment
./deploy.sh plan local

# 3. Apply
./deploy.sh apply local

# 4. Get the IP address
./deploy.sh output libvirt_vm_ip

# 5. SSH into VM
ssh debian@<ip-from-step-4>
# or use virsh console
virsh console debian-vm
```

## Change VM Size

```bash
# 1. Edit terraform.tfvars
# Change: vm_size = "medium"  # from "small"

# 2. Apply changes
./deploy.sh apply vultr   # or "local"

# VM will be recreated with new size
```

## Destroy Resources

```bash
# Vultr
./deploy.sh destroy vultr

# Local
./deploy.sh destroy local
```

## Troubleshooting

```bash
# Validate configuration
./deploy.sh validate

# Format files
./deploy.sh fmt

# Show current state
./deploy.sh show

# Enable debug logging
TF_LOG=DEBUG ./deploy.sh plan vultr

# Check specific resource
terraform state show 'vultr_instance.debian_vm[0]'
```

## File Reference

- **main.tf**: Core infrastructure (VM resources)
- **variables.tf**: All configuration variables
- **outputs.tf**: What Terraform outputs after deployment
- **providers.tf**: Cloud provider settings
- **versions.tf**: Terraform and provider versions
- **deploy.sh**: Helper script for all operations
- **README.md**: Full documentation
- **TESTING.md**: Testing and debugging guide

## Environment Variables

```bash
# Required for Vultr
export TF_VAR_vultr_api_key="your-key"

# Optional
export TF_LOG=DEBUG           # Enable debug logging
export TF_LOG_PATH=tf.log     # Save logs to file
```

## Common Issues

| Problem | Solution |
|---------|----------|
| API key not recognized | Set `TF_VAR_vultr_api_key` environment variable |
| libvirt permission denied | Add user to libvirt group: `sudo usermod -a -G libvirt $USER` |
| State file conflicts | `rm terraform.tfstate*` and reinit |
| Resource creation timeout | Check provider credentials and network connectivity |

## Next Steps After Deployment

1. SSH into the VM
2. Update packages: `sudo apt-get update && apt-get upgrade -y`
3. Install your application software
4. Consider using Ansible for automated configuration
5. Set up monitoring and backups
