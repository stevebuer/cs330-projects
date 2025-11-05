#!/bin/bash

# Terraform to Ansible Bridge
# Converts Terraform outputs to Ansible inventory

set -e

TERRAFORM_DIR="../terraform"
ANSIBLE_DIR="."
OUTPUT_FILE="${ANSIBLE_DIR}/inventory.aws"

echo "Generating Ansible inventory from Terraform outputs..."

# Function to get Terraform output
get_tf_output() {
    cd "$TERRAFORM_DIR"
    terraform output -raw "$1" 2>/dev/null || echo ""
}

# Get VM details
VM_IP=$(get_tf_output "vultr_vm_ip")
VM_ID=$(get_tf_output "vultr_vm_id")
ENV=$(get_tf_output "deployment_info" | grep -o "vultr\|local")

if [ -z "$VM_IP" ]; then
    echo "Error: No Terraform outputs found"
    exit 1
fi

# Generate inventory
cat > "${ANSIBLE_DIR}/inventory.generated" << EOF
# Generated from Terraform outputs
# Generated on: $(date)

[all:children]
production

[production]
prod-server ansible_host=${VM_IP} ansible_user=root terraform_id=${VM_ID}

[dxcluster_database]
prod-server

[dxcluster_scraper]
prod-server

[docker_hosts]
prod-server

[web]
prod-server
EOF

echo "Inventory generated: ${ANSIBLE_DIR}/inventory.generated"
echo "VM IP: $VM_IP"
echo "VM ID: $VM_ID"
echo ""
echo "Next steps:"
echo "1. Review generated inventory"
echo "2. Test connectivity: ./deploy.sh check prod-server"
echo "3. Deploy: ./deploy.sh full prod-server"
