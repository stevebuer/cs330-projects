# Terraform Quick Reference Card

## One-Time Setup

```bash
# Install Terraform
sudo apt-get install terraform

# For local VirtualBox deployment
sudo apt-get install libvirt-daemon libvirt-daemon-system qemu qemu-kvm
sudo systemctl start libvirtd
sudo systemctl enable libvirtd

# Initialize
cd homework4/terraform
./deploy.sh init
```

## Vultr Cloud Deployment

```bash
# 1. Set API key
export TF_VAR_vultr_api_key="your-api-key"

# 2. Configure
cp terraform.tfvars.vultr.example terraform.tfvars
# Edit terraform.tfvars as needed

# 3. Deploy
./deploy.sh plan vultr     # Review changes
./deploy.sh apply vultr    # Deploy

# 4. Connect
SSH_IP=$(terraform output -raw vultr_vm_ip)
ssh root@$SSH_IP
```

## Local VirtualBox Deployment

```bash
# 1. Configure
cp terraform.tfvars.local.example terraform.tfvars
# Edit terraform.tfvars if needed

# 2. Deploy
./deploy.sh plan local     # Review changes
./deploy.sh apply local    # Deploy

# 3. Connect
VM_IP=$(terraform output -raw libvirt_vm_ip)
ssh debian@$VM_IP
# OR: virsh console debian-vm
```

## Common Commands

| Command | Purpose |
|---------|---------|
| `./deploy.sh init` | Initialize Terraform (run first!) |
| `./deploy.sh validate` | Validate configuration |
| `./deploy.sh fmt` | Format Terraform code |
| `./deploy.sh plan [env]` | Plan deployment (dry-run) |
| `./deploy.sh apply [env]` | Deploy to cloud/local |
| `./deploy.sh destroy [env]` | Destroy resources |
| `./deploy.sh show` | Show current state |
| `./deploy.sh output` | Show all outputs |
| `./deploy.sh output [var]` | Show specific output |

## Change VM Size

```bash
# Edit terraform.tfvars
vm_size = "medium"  # or "small"

# Apply changes
./deploy.sh apply [vultr|local]
```

## Troubleshooting

### API Key Issues
```bash
# Verify key is set
echo $TF_VAR_vultr_api_key

# Check it's valid in Vultr dashboard
# Confirm no extra spaces
```

### LibVirt Permission Issues
```bash
# Add user to libvirt group
sudo usermod -a -G libvirt $USER
# Log out and back in
```

### State Issues
```bash
# Reset state (careful!)
rm terraform.tfstate*
./deploy.sh init
```

### Debug
```bash
# Enable debug logging
TF_LOG=DEBUG ./deploy.sh apply [env]

# Save to file
TF_LOG_PATH=debug.log ./deploy.sh apply [env]
```

## File Quick Reference

| File | Contains |
|------|----------|
| `versions.tf` | Provider versions |
| `providers.tf` | Provider setup |
| `variables.tf` | All configuration variables |
| `main.tf` | Infrastructure resources |
| `outputs.tf` | What to display after deploy |
| `deploy.sh` | Helper commands |
| `terraform.tfvars` | Your settings (created from example) |
| `terraform.tfstate` | Current state (auto-generated) |

## Variable Reference

| Variable | Default | Options |
|----------|---------|---------|
| `environment` | - | `vultr` or `local` |
| `vm_size` | `small` | `small`, `medium` |
| `vm_name` | `debian-vm` | Any string |
| `debian_version` | `12` | `12` (latest) |
| `vultr_region` | `ewr` | `ewr`, `lax`, `ord`, `ams`, `lon`, etc. |

## Post-Deployment

```bash
# Get VM IP
terraform output vultr_vm_ip    # or libvirt_vm_ip

# SSH to VM
ssh root@<ip>                   # For Vultr
ssh debian@<ip>                 # For local

# Check VM details
terraform output                # Show all info

# Monitor VM (local)
virsh list                      # List all VMs
virsh console debian-vm         # VM console
```

## Best Practices

✓ Always run `plan` before `apply`
✓ Keep `terraform.tfvars` out of git (in .gitignore)
✓ Store API keys in environment variables
✓ Test locally before cloud deployment
✓ Use descriptive names for resources
✓ Review plan output carefully
✓ Save state files securely

## Documentation Files

- **QUICKSTART.md** - This card (extended)
- **CHECKLIST.md** - Step-by-step setup
- **README.md** - Full documentation
- **SETUP_SUMMARY.md** - Overview & workflows
- **TESTING.md** - Debugging & testing

## Get Help

```bash
./deploy.sh help                # Show all commands
cat README.md                   # Full documentation
cat CHECKLIST.md                # Step-by-step setup
cat TESTING.md                  # Debugging
```

---

**Quick Start**: `cd homework4/terraform && ./deploy.sh init`

**Deployment Time**: ~3-5 minutes
**Terraform Version**: 1.0+
**Status**: ✅ Ready to deploy
