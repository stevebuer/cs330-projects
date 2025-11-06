# Local KVM/VirtualBox Deployment - Quick Reference

## Prerequisites ✅

All verified:
- ✅ Terraform v1.13.4
- ✅ libvirt 9.0.0 / QEMU 7.2.19
- ✅ terraform.tfvars.local created
- ✅ Configuration validated

## 3-Step Deployment

### Step 1: Plan
```bash
cd homework4/terraform
terraform plan -var-file="terraform.tfvars.local" -out=tfplan
```

### Step 2: Review
```bash
terraform show tfplan
```

### Step 3: Apply
```bash
terraform apply tfplan
```

## Monitor

```bash
# Watch VM creation in separate terminal
watch -n 2 'virsh list --all'

# Get VM status
virsh domstate debian-cs330-local

# Get assigned IP
terraform output libvirt_vm_ip
```

## VM Details

| Setting | Value |
|---------|-------|
| Name | debian-cs330-local |
| OS | Debian 12 |
| vCPU | 1 |
| Memory | 1GB |
| Disk | 20GB QCOW2 |
| Network | default (NAT) |

## Verify Deployment

```bash
# VM running?
virsh list | grep debian-cs330-local

# Storage pool created?
virsh pool-list | grep terraform

# Get full details
terraform output

# Check disk size
virsh vol-info debian-cs330-local-disk.qcow2 --pool terraform-pool
```

## Cleanup

```bash
# Destroy all resources
terraform destroy -var-file="terraform.tfvars.local"

# Manual cleanup
virsh destroy debian-cs330-local
virsh undefine debian-cs330-local
virsh pool-destroy terraform-pool
```

## Troubleshooting

| Issue | Command |
|-------|---------|
| VM won't start | `virsh console debian-cs330-local` |
| No network | `virsh net-start default` |
| Check space | `df -h /var/lib/libvirt/images` |
| Full details | `virsh dumpxml debian-cs330-local` |
| Check libvirt group | `id` (should have libvirt) |

## Files

| File | Purpose |
|------|---------|
| terraform.tfvars.local | Configuration for local deployment |
| LOCAL_DEPLOYMENT_GUIDE.md | Full deployment guide |
| main.tf | Infrastructure definitions |
| deploy.sh | Helper script with all commands |

## Key Commands

```bash
# Validate
./deploy.sh validate

# Plan
terraform plan -var-file="terraform.tfvars.local"

# Deploy
terraform apply -var-file="terraform.tfvars.local"

# Status
virsh list --all

# Destroy
terraform destroy -var-file="terraform.tfvars.local"

# Get IP
terraform output libvirt_vm_ip

# SSH into VM (if supported)
ssh debian@$(terraform output -raw libvirt_vm_ip)
```

## Configuration

Current `terraform.tfvars.local`:
```hcl
environment = "local"
vm_size = "small"
vm_name = "debian-cs330-local"
libvirt_pool_path = "/var/lib/libvirt/images"
```

To use larger VM:
```hcl
vm_size = "medium"  # 2 vCPU, 2GB RAM
```

---

**Time to Deploy:** 5-10 minutes  
**Expected Outcome:** Running Debian 12 VM in KVM/libvirt  
**Next Steps:** See `LOCAL_DEPLOYMENT_GUIDE.md` for detailed guide
