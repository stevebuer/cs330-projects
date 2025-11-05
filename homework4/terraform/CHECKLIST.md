# Getting Started Checklist

Use this checklist to set up and deploy your infrastructure.

## Pre-Deployment Setup

### Installation & Prerequisites

- [ ] **Terraform Installed**
  ```bash
  terraform version  # Should show v1.0 or later
  ```

- [ ] **Vultr Deployment** (if deploying to cloud):
  - [ ] Vultr account created
  - [ ] API key obtained from Vultr dashboard
  - [ ] API key stored securely (not in git!)

- [ ] **Local Deployment** (if deploying to VirtualBox):
  - [ ] libvirt installed: `sudo apt-get install libvirt-daemon libvirt-daemon-system qemu qemu-kvm`
  - [ ] libvirtd service running: `sudo systemctl status libvirtd`
  - [ ] User added to libvirt group: `sudo usermod -a -G libvirt $USER`

### Environment Setup

- [ ] Navigate to terraform directory:
  ```bash
  cd homework4/terraform
  ```

- [ ] Run setup index to verify all files:
  ```bash
  ./index.sh
  ```

- [ ] Review documentation:
  - [ ] `README.md` - Full setup guide
  - [ ] `QUICKSTART.md` - Quick reference
  - [ ] `SETUP_SUMMARY.md` - Overview

## Deployment Configuration

### For Vultr Cloud

- [ ] Set API key environment variable:
  ```bash
  export TF_VAR_vultr_api_key="your-vultr-api-key-here"
  ```

- [ ] Copy configuration template:
  ```bash
  cp terraform.tfvars.vultr.example terraform.tfvars
  ```

- [ ] Edit `terraform.tfvars` to customize:
  - [ ] Change `vm_name` if desired (default: `debian-server-prod`)
  - [ ] Change `vm_size` if needed (default: `small`)
  - [ ] Change `vultr_region` if needed (default: `ewr` - New Jersey)
  - [ ] Review `tags` for your project

### For Local VirtualBox

- [ ] Copy configuration template:
  ```bash
  cp terraform.tfvars.local.example terraform.tfvars
  ```

- [ ] Edit `terraform.tfvars` to customize:
  - [ ] Change `vm_name` if desired (default: `debian-vm`)
  - [ ] Change `vm_size` if needed (default: `small`)
  - [ ] Verify `libvirt_pool_path` (default: `/var/lib/libvirt/images`)

## Terraform Initialization

- [ ] Initialize Terraform:
  ```bash
  ./deploy.sh init
  ```
  
  Or manually:
  ```bash
  terraform init
  ```

- [ ] Verify initialization:
  ```bash
  ls -la .terraform/
  ```
  Should see provider plugins downloaded

## Planning & Validation

- [ ] Validate configuration:
  ```bash
  ./deploy.sh validate
  ```

- [ ] Plan the deployment:
  ```bash
  ./deploy.sh plan vultr    # For cloud
  # OR
  ./deploy.sh plan local    # For local
  ```

- [ ] Review the plan output:
  - [ ] Check VM specifications
  - [ ] Verify resource names
  - [ ] Confirm sizing is correct

## Deployment

- [ ] Apply the configuration:
  ```bash
  ./deploy.sh apply vultr   # For cloud
  # OR
  ./deploy.sh apply local   # For local
  ```

- [ ] Wait for deployment to complete (may take 2-5 minutes)

- [ ] Note the deployment output:
  - [ ] VM ID
  - [ ] IP address
  - [ ] Other connection details

## Post-Deployment

### Verify Deployment

- [ ] Check outputs:
  ```bash
  terraform output
  ```

- [ ] Get VM IP address:
  ```bash
  terraform output [vultr_vm_ip|libvirt_vm_ip]
  ```

### Connect to VM

**For Vultr:**
```bash
ssh root@<ip-address>
```

**For Local VirtualBox:**
```bash
ssh debian@<ip-address>
# or
virsh console debian-vm
```

### System Configuration

- [ ] Update packages:
  ```bash
  sudo apt-get update
  sudo apt-get upgrade -y
  ```

- [ ] Install required software:
  ```bash
  # Add your software installation commands here
  ```

- [ ] Configure firewall (if needed):
  ```bash
  # Add firewall rules here
  ```

## Maintenance

### Regular Operations

- [ ] View current state:
  ```bash
  ./deploy.sh show
  ```

- [ ] List all resources:
  ```bash
  terraform state list
  ```

- [ ] Check specific resource:
  ```bash
  terraform state show 'vultr_instance.debian_vm[0]'
  ```

### Scaling or Changes

- [ ] Change VM size:
  - [ ] Edit `terraform.tfvars`: change `vm_size = "medium"`
  - [ ] Plan changes: `./deploy.sh plan [env]`
  - [ ] Apply changes: `./deploy.sh apply [env]`

- [ ] Destroy resources (when done):
  ```bash
  ./deploy.sh destroy vultr    # For cloud
  # OR
  ./deploy.sh destroy local    # For local
  ```

## Troubleshooting

### Common Issues

**API Key Not Recognized**
- [ ] Verify env var set: `echo $TF_VAR_vultr_api_key`
- [ ] Check key validity in Vultr dashboard
- [ ] Ensure no extra spaces in key

**LibVirt Permission Denied**
- [ ] Add user to group: `sudo usermod -a -G libvirt $USER`
- [ ] Log out and back in
- [ ] Verify: `virsh list`

**Terraform State Issues**
- [ ] Reset state: `rm terraform.tfstate*`
- [ ] Reinitialize: `./deploy.sh init`
- [ ] Redeploy: `./deploy.sh apply [env]`

**Provider Not Found**
- [ ] Ensure init was run: `terraform init`
- [ ] Check internet connection
- [ ] Try again: `terraform init -upgrade`

### Getting Help

- [ ] Check `TESTING.md` for debugging tips
- [ ] Enable debug logging: `TF_LOG=DEBUG ./deploy.sh apply [env]`
- [ ] Review Terraform logs: `terraform console`
- [ ] Check Vultr/libvirt status:
  - Vultr: Check Vultr dashboard
  - Local: `virsh list`

## Progress Tracking

- [ ] Infrastructure created ✓
- [ ] Configuration tested
- [ ] Deployment successful
- [ ] Application installed
- [ ] System tested end-to-end
- [ ] Ready for production

---

**Notes:**
- Keep `terraform.tfvars` out of git (it's in `.gitignore`)
- Store API keys safely, use environment variables
- Test locally before deploying to cloud
- Consider using version control for `.tfvars` files (or encrypted versions)
