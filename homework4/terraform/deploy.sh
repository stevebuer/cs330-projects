#!/bin/bash

# Terraform Deployment Helper Script
# Supports both Vultr cloud and local VirtualBox deployments

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_help() {
    cat << EOF
${BLUE}Terraform Deployment Helper${NC}

Usage: $0 [COMMAND] [OPTIONS]

Commands:
  init               Initialize Terraform (run first)
  plan [ENV]         Plan deployment (vultr or local)
  apply [ENV]        Apply deployment
  destroy [ENV]      Destroy resources
  validate           Validate Terraform configuration
  fmt                Format Terraform files
  show               Show current state
  output [VAR]       Show output values

Environment Options:
  vultr              Deploy to Vultr cloud (default)
  local              Deploy to local VirtualBox

Examples:
  $0 init
  $0 plan vultr
  $0 apply local --var-file terraform.tfvars.local
  $0 destroy vultr
  $0 output

EOF
}

# Initialize Terraform
init_terraform() {
    echo -e "${BLUE}Initializing Terraform...${NC}"
    cd "$SCRIPT_DIR"
    terraform init
    echo -e "${GREEN}Terraform initialized${NC}"
}

# Validate configuration
validate_terraform() {
    echo -e "${BLUE}Validating Terraform configuration...${NC}"
    cd "$SCRIPT_DIR"
    terraform validate
    echo -e "${GREEN}Configuration is valid${NC}"
}

# Format files
format_terraform() {
    echo -e "${BLUE}Formatting Terraform files...${NC}"
    cd "$SCRIPT_DIR"
    terraform fmt -recursive
    echo -e "${GREEN}Files formatted${NC}"
}

# Plan deployment
plan_deployment() {
    local env="${1:-vultr}"
    local var_file=""
    
    if [ "$env" = "vultr" ]; then
        var_file="terraform.tfvars.vultr.example"
    elif [ "$env" = "local" ]; then
        var_file="terraform.tfvars.local.example"
    else
        echo -e "${RED}Invalid environment: $env${NC}"
        echo "Use 'vultr' or 'local'"
        exit 1
    fi

    echo -e "${BLUE}Planning $env deployment...${NC}"
    cd "$SCRIPT_DIR"
    
    if [ ! -f "$var_file" ]; then
        echo -e "${YELLOW}Warning: $var_file not found${NC}"
        echo "Using default variables"
        terraform plan -var="environment=$env"
    else
        terraform plan -var-file="$var_file"
    fi
}

# Apply deployment
apply_deployment() {
    local env="${1:-vultr}"
    local var_file=""
    
    if [ "$env" = "vultr" ]; then
        var_file="terraform.tfvars.vultr.example"
        echo -e "${YELLOW}Deploying to Vultr...${NC}"
        echo "Make sure you have set TF_VAR_vultr_api_key environment variable"
        read -p "Continue? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    elif [ "$env" = "local" ]; then
        var_file="terraform.tfvars.local.example"
        echo -e "${YELLOW}Deploying to local VirtualBox...${NC}"
        echo "Make sure libvirt/KVM is installed and running"
        read -p "Continue? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo -e "${RED}Invalid environment: $env${NC}"
        exit 1
    fi

    echo -e "${BLUE}Applying $env deployment...${NC}"
    cd "$SCRIPT_DIR"
    
    if [ ! -f "$var_file" ]; then
        terraform apply -var="environment=$env"
    else
        terraform apply -var-file="$var_file"
    fi
}

# Destroy deployment
destroy_deployment() {
    local env="${1:-vultr}"
    
    echo -e "${RED}WARNING: This will destroy all resources!${NC}"
    read -p "Are you sure you want to destroy the $env deployment? (yes/no) " confirm
    
    if [ "$confirm" != "yes" ]; then
        echo "Cancelled"
        exit 0
    fi

    echo -e "${BLUE}Destroying $env deployment...${NC}"
    cd "$SCRIPT_DIR"
    terraform destroy -var="environment=$env"
}

# Show state
show_state() {
    echo -e "${BLUE}Current Terraform State:${NC}"
    cd "$SCRIPT_DIR"
    terraform show
}

# Show outputs
show_outputs() {
    local var="${1:-}"
    echo -e "${BLUE}Terraform Outputs:${NC}"
    cd "$SCRIPT_DIR"
    if [ -z "$var" ]; then
        terraform output
    else
        terraform output "$var"
    fi
}

# Main script logic
if [ $# -eq 0 ]; then
    print_help
    exit 0
fi

COMMAND="$1"
shift || true

case "$COMMAND" in
    init)
        init_terraform
        ;;
    plan)
        plan_deployment "$@"
        ;;
    apply)
        apply_deployment "$@"
        ;;
    destroy)
        destroy_deployment "$@"
        ;;
    validate)
        validate_terraform
        ;;
    fmt)
        format_terraform
        ;;
    show)
        show_state
        ;;
    output)
        show_outputs "$@"
        ;;
    help)
        print_help
        ;;
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        print_help
        exit 1
        ;;
esac
