# Local KVM/VirtualBox Deployment Testing Guide

**Date:** November 5, 2025  
**Purpose:** Test Terraform deployment to local KVM/libvirt environment

## ✅ Prerequisites Check

All systems verified:
- ✅ Terraform v1.13.4 installed
- ✅ libvirt 9.0.0 running (QEMU 7.2.19)
- ✅ Configuration files created
- ✅ Terraform validated successfully

## 🚀 Deployment Steps

### Step 1: Review the Plan

The plan shows it will create:
- **libvirt_pool.terraform_pool** - Storage pool at `/var/lib/libvirt/images`
- **libvirt_volume.debian_disk** - 20GB QCOW2 disk image
- **libvirt_domain.debian_vm** - Debian 12 VM with 1 vCPU, 1GB RAM

### Step 2: Apply the Configuration

Run the deployment:

```bash
cd /home/steve/GITHUB/cs330-projects/homework4/terraform

# Apply using the local configuration
terraform apply -var-file="terraform.tfvars.local"
```

When prompted for `vultr_api_key`, just press Enter (it's not used for local deployment).

Expected output:
```
Terraform will perform the following actions:
  + libvirt_pool.terraform_pool[0] will be created
  + libvirt_volume.debian_disk[0] will be created
  + libvirt_domain.debian_vm[0] will be created

Do you want to perform these actions?
```

Type `yes` and press Enter to proceed.

### Step 3: Monitor the Deployment

The deployment will:
1. Create the libvirt storage pool (~5 seconds)
2. Create the 20GB QCOW2 disk image (~30-60 seconds)
3. Create and start the VM (~10-20 seconds)
4. Wait for the VM to get an IP address (~2-5 minutes)

Total time: **5-10 minutes**

### Step 4: Verify the Deployment

After successful apply, you should see output like:

```
Apply complete! Resources have been created.

Outputs:

deployment_info = {
  "debian_version" = "12"
  "environment" = "local"
  "vm_name" = "debian-cs330-local"
  "vm_size" = "small"
}
libvirt_vm_details = {
  "id" = "..."
  "name" = "debian-cs330-local"
  "running" = true
}
libvirt_vm_ip = "192.168.122.XXX"
```

Check the VM is running:

```bash
# List running VMs
virsh list

# Expected output:
# Id   Name                    State
# 1    debian-cs330-local      running

# Get VM details
virsh dominfo debian-cs330-local

# Get VM IP address
virsh domifaddr debian-cs330-local
```

## 🔍 Testing the VM

Once deployed, test connectivity:

```bash
# Get the IP address from outputs
IP=$(terraform output -raw libvirt_vm_ip)
echo "VM IP: $IP"

# SSH into the VM (default Debian has root but no password, needs cloud-init)
# For this test environment, we're just verifying it started

# Check from libvirt
virsh console debian-cs330-local
# Press Ctrl+] to exit console
```

## 📊 Viewing Resources

List all resources created by Terraform:

```bash
# Show all managed resources
terraform state list

# Show detailed state
terraform state show 'libvirt_pool.terraform_pool[0]'
terraform state show 'libvirt_volume.debian_disk[0]'
terraform state show 'libvirt_domain.debian_vm[0]'

# Show all outputs
terraform output

# Show specific output
terraform output libvirt_vm_ip
```

View via libvirt commands:

```bash
# List storage pools
virsh pool-list --all

# Show pool details
virsh pool-info terraform-pool

# List volumes
virsh vol-list terraform-pool

# List domains
virsh list --all

# Get domain details
virsh dominfo debian-cs330-local
virsh dumpxml debian-cs330-local  # Full XML config
```

## 🧹 Cleanup

To remove everything and start fresh:

```bash
# Destroy via Terraform (recommended)
terraform destroy -var-file="terraform.tfvars.local"

# Or manually via libvirt
virsh destroy debian-cs330-local
virsh undefine debian-cs330-local
virsh pool-destroy terraform-pool
virsh pool-delete terraform-pool
```

## 🐛 Troubleshooting

### VM fails to start

**Problem:** `libvirt_domain.debian_vm creation timeout`

**Solution:**
```bash
# Check VM status
virsh domstate debian-cs330-local

# Check VM logs
virsh ttyconsole debian-cs330-local
virsh console debian-cs330-local

# Get more details
virsh dumpxml debian-cs330-local | grep -A5 "boot"

# Try to start manually
virsh start debian-cs330-local

# Enable debug logging
TF_LOG=DEBUG terraform apply -var-file="terraform.tfvars.local"
```

### Network issues

**Problem:** VM doesn't get IP address

**Solution:**
```bash
# Check if default network is running
virsh net-list

# If not running, start it
virsh net-start default

# Check DHCP is enabled
virsh net-dumpxml default | grep -i dhcp

# Restart VM
virsh reboot debian-cs330-local
```

### Disk space issues

**Problem:** "No space left on device"

**Solution:**
```bash
# Check available space
df -h /var/lib/libvirt/images

# Check disk size
virsh vol-info debian-cs330-local-disk.qcow2 --pool terraform-pool

# If space is low, clean up or expand
# Note: 20GB disk may be large depending on available space
```

### Permission issues

**Problem:** "Permission denied" errors

**Solution:**
```bash
# Check libvirt group membership
id

# If missing 'libvirt' group, add user:
sudo usermod -aG libvirt $USER

# Then log out and back in, or use:
newgrp libvirt

# Check socket permissions
ls -la /var/run/libvirt/libvirt-sock
```

## 📈 Performance Tips

### Speed up deployment:

```bash
# Use medium size VM for faster testing
terraform apply -var="vm_size=medium" -var-file="terraform.tfvars.local"

# Or create new tfvars file with medium size
cp terraform.tfvars.local terraform.tfvars.local.medium
# Edit and change: vm_size = "medium"
terraform apply -var-file="terraform.tfvars.local.medium"
```

### Monitor during deployment:

```bash
# In another terminal, watch the VM creation:
watch -n 2 'virsh list --all; echo "---"; virsh vol-list terraform-pool'

# Or continuously check status:
watch -n 5 'terraform show | grep -i running'
```

## 📋 Complete Testing Workflow

Here's a complete end-to-end workflow:

```bash
#!/bin/bash
set -e

cd /home/steve/GITHUB/cs330-projects/homework4/terraform

echo "🔍 Step 1: Validate configuration"
./deploy.sh validate

echo "📋 Step 2: Review plan"
terraform plan -var-file="terraform.tfvars.local" -out=tfplan
terraform show tfplan

echo "❓ Ready to deploy? (Ctrl+C to cancel, or press Enter to continue)"
read

echo "🚀 Step 3: Apply configuration"
terraform apply tfplan

echo "✅ Step 4: Verify deployment"
terraform output

echo "🔍 Step 5: Check VM status"
virsh list --all

echo "📍 Step 6: Get VM details"
IP=$(terraform output -raw libvirt_vm_ip)
echo "VM is running at: $IP"

echo "✅ Deployment complete!"
```

## 🔄 Making Changes

If you want to modify the deployment:

```bash
# Edit the local config
nano terraform.tfvars.local

# Or change variables via command line
terraform apply \
  -var-file="terraform.tfvars.local" \
  -var="vm_size=medium" \
  -var="vm_name=debian-test-2"

# To update existing VM with new config
terraform apply -var-file="terraform.tfvars.local"

# To destroy and recreate
terraform destroy -var-file="terraform.tfvars.local"
terraform apply -var-file="terraform.tfvars.local"
```

## 📊 State Management

Current deployment uses local state file:

```bash
# Backup state before making changes
cp terraform.tfstate terraform.tfstate.backup

# View state file location
ls -la terraform.tfstate*

# Manually inspect state (use with caution)
terraform state show

# List resources
terraform state list

# Show specific resource
terraform state show 'libvirt_domain.debian_vm[0]'

# WARNING: Never directly edit terraform.tfstate!
```

## 🎓 Learning Resources

For more information:

- **Local Terraform Testing:** See `TESTING.md`
- **Terraform Providers:** See `providers.tf`
- **Variables:** See `variables.tf`
- **Outputs:** See `outputs.tf`
- **Deployment Helper:** See `deploy.sh` (run `./deploy.sh help`)

## ✅ Next Steps

1. ✅ Review plan output
2. ✅ Run `terraform apply -var-file="terraform.tfvars.local"`
3. ✅ Verify VM is running
4. ✅ Test connectivity if possible
5. ✅ Document any issues
6. ✅ Clean up with `terraform destroy` when done testing

## 📞 Quick Commands

```bash
# Deploy
terraform apply -var-file="terraform.tfvars.local"

# Check status
virsh list --all
terraform output

# Get IP
terraform output -raw libvirt_vm_ip

# SSH (if image supports it)
ssh debian@$(terraform output -raw libvirt_vm_ip)

# Destroy
terraform destroy -var-file="terraform.tfvars.local"

# Cleanup everything
rm -rf .terraform terraform.tfstate* && terraform init
```

---

**Status:** Ready to deploy! 🚀
