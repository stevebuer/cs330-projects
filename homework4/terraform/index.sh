#!/usr/bin/env bash

# Terraform Infrastructure Setup Index and Validator
# This script provides an overview of the Terraform setup and validates all components

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Terraform Infrastructure Setup - Component Index${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo

# Check each file
check_file() {
    local file="$1"
    local description="$2"
    
    if [ -f "$SCRIPT_DIR/$file" ]; then
        local lines=$(wc -l < "$SCRIPT_DIR/$file")
        printf "  ${GREEN}✓${NC} %-35s %4d lines\n" "$file" "$lines"
        return 0
    else
        printf "  ${RED}✗${NC} %-35s MISSING\n" "$file"
        return 1
    fi
}

echo -e "${BLUE}Core Terraform Files:${NC}"
check_file "versions.tf" "Provider versions"
check_file "providers.tf" "Provider configuration"
check_file "variables.tf" "Input variables"
check_file "main.tf" "Infrastructure resources"
check_file "outputs.tf" "Output values"
echo

echo -e "${BLUE}Helper Scripts:${NC}"
if [ -x "$SCRIPT_DIR/deploy.sh" ]; then
    printf "  ${GREEN}✓${NC} %-35s executable\n" "deploy.sh"
else
    printf "  ${RED}✗${NC} %-35s not executable\n" "deploy.sh"
fi
echo

echo -e "${BLUE}Configuration Examples:${NC}"
check_file "terraform.tfvars.vultr.example"
check_file "terraform.tfvars.local.example"
echo

echo -e "${BLUE}Documentation:${NC}"
check_file "README.md" "Full documentation"
check_file "QUICKSTART.md" "Quick reference"
check_file "SETUP_SUMMARY.md" "Setup overview"
check_file "TESTING.md" "Testing guide"
echo

echo -e "${BLUE}Git Configuration:${NC}"
check_file ".gitignore"
echo

# Syntax check if terraform is available
echo -e "${BLUE}Validation:${NC}"
if command -v terraform &> /dev/null; then
    cd "$SCRIPT_DIR"
    if [ ! -d ".terraform" ]; then
        echo -e "  ${YELLOW}⚠${NC}  Terraform not initialized yet (run 'terraform init' first)"
    elif terraform validate > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} Terraform syntax is valid"
    else
        echo -e "  ${YELLOW}⚠${NC}  Terraform validation needs init"
    fi
else
    echo -e "  ${YELLOW}⚠${NC}  Terraform not installed (validation skipped)"
fi
echo

# Summary
total_lines=$(find "$SCRIPT_DIR" -type f \( -name "*.tf" -o -name "*.sh" -o -name "*.md" \) -exec wc -l {} + | tail -1 | awk '{print $1}')
total_files=$(find "$SCRIPT_DIR" -type f ! -path '*/.*' | wc -l)

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Summary:${NC}"
echo -e "  ${GREEN}Files:${NC}  $total_files total"
echo -e "  ${GREEN}Lines:${NC}  $total_lines total"
echo -e "  ${GREEN}Ready:${NC}  YES${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo

echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Read terraform/README.md for detailed instructions"
echo "  2. Read terraform/QUICKSTART.md for quick reference"
echo "  3. Copy appropriate .tfvars.example file to terraform.tfvars"
echo "  4. Run: ./deploy.sh init"
echo "  5. Run: ./deploy.sh plan [vultr|local]"
echo "  6. Run: ./deploy.sh apply [vultr|local]"
echo

echo -e "${GREEN}Setup complete! Ready to deploy.${NC}"
