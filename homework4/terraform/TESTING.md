# Terraform Local Testing & Development Guide

## Quick Reference

### Test Terraform Configuration Locally Before Deployment

```bash
# 1. Validate syntax
cd terraform
terraform validate

# 2. Format code consistently
terraform fmt -recursive

# 3. Check for security issues (requires tfsec)
tfsec .

# 4. Plan the deployment (dry-run)
terraform plan -out=tfplan

# 5. Review the plan
terraform show tfplan

# 6. Apply if satisfied
terraform apply tfplan
```

### Environment Variables

For Vultr deployment, always set:
```bash
export TF_VAR_vultr_api_key="your-api-key-here"
```

Or use a `.env` file:
```bash
# .env (add to .gitignore!)
TF_VAR_vultr_api_key=your-api-key-here

# Load it
source .env
terraform apply
```

### Managing Multiple Environments

Keep separate variable files for each environment:

```bash
# Vultr production
terraform apply -var-file="terraform.tfvars.vultr"

# Local development
terraform apply -var-file="terraform.tfvars.local"

# Staging
terraform apply -var-file="terraform.tfvars.staging"
```

### State Management

Current setup uses local state (`terraform.tfstate`). For team collaboration:

```bash
# Switch to remote state (AWS S3 example)
# Add to providers.tf:
# backend "s3" {
#   bucket = "my-terraform-state"
#   key    = "homework4/terraform.tfstate"
#   region = "us-east-1"
# }

terraform init  # Will ask to migrate state
```

### Monitoring Deployments

```bash
# Show current infrastructure
terraform show

# Show specific output
terraform output vultr_vm_ip

# Refresh state (sync with actual resources)
terraform refresh

# Show resource details
terraform state list
terraform state show 'vultr_instance.debian_vm[0]'
```

### Troubleshooting

```bash
# Enable debug logging
TF_LOG=DEBUG terraform apply

# Trace level logging
TF_LOG=TRACE terraform apply

# Save logs to file
TF_LOG_PATH=terraform.log terraform apply

# Validate specific resources
terraform validate -json | jq
```

### Cleanup

```bash
# Destroy all resources in current workspace
terraform destroy

# Destroy specific environment
terraform destroy -var="environment=local"

# Remove state and init files (full reset)
rm -rf .terraform terraform.tfstate* .terraform.lock.hcl
terraform init
```
