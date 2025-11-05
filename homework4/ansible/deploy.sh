#!/bin/bash

# Ansible Deployment Helper Script
# Simplifies common Ansible deployment operations

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Functions
print_help() {
    cat << EOF
${BLUE}Ansible Deployment Helper${NC}

Usage: $0 [COMMAND] [OPTIONS]

Commands:
  init                   Initialize Ansible environment
  check [HOST]           Check connectivity to hosts
  facts [HOST]           Gather facts from hosts
  
  base [HOST]            Deploy base system only
  packages [HOST]        Deploy DX Cluster packages only
  docker [HOST]          Deploy Docker and containers
  full [HOST]            Full deployment (all)
  
  syntax                 Check playbook syntax
  validate [PLAY]        Validate playbook
  lint                   Run ansible-lint
  
  ping                   Test host connectivity
  list-hosts             List all inventory hosts
  list-groups            List all inventory groups
  
  vault-create           Create vault-encrypted file
  vault-edit FILE        Edit vault-encrypted file
  
  status [HOST]          Show deployment status
  logs [HOST] [SERVICE]  Show service logs
  
  help                   Show this help message

Examples:
  $0 init
  $0 check prod-server
  $0 full prod-server
  $0 packages dev-server
  $0 vault-create secrets.yml
  $0 status prod-server

EOF
}

# Initialize Ansible
init_ansible() {
    echo -e "${BLUE}Initializing Ansible environment...${NC}"
    
    # Check for inventory
    if [ ! -f "$SCRIPT_DIR/inventory" ]; then
        echo -e "${YELLOW}Warning: inventory file not found${NC}"
    fi
    
    # Check for group_vars
    if [ ! -d "$SCRIPT_DIR/group_vars" ]; then
        echo -e "${YELLOW}Warning: group_vars directory not found${NC}"
    fi
    
    # Check for roles
    if [ ! -d "$SCRIPT_DIR/roles" ]; then
        echo -e "${YELLOW}Warning: roles directory not found${NC}"
    fi
    
    echo -e "${GREEN}Ansible environment ready${NC}"
}

# Check connectivity
check_connectivity() {
    local host="${1:-all}"
    echo -e "${BLUE}Checking connectivity to ${host}...${NC}"
    cd "$SCRIPT_DIR"
    ansible "$host" -i inventory -m ping
}

# Gather facts
gather_facts() {
    local host="${1:-all}"
    echo -e "${BLUE}Gathering facts from ${host}...${NC}"
    cd "$SCRIPT_DIR"
    ansible "$host" -i inventory -m setup | head -50
}

# Deploy base system
deploy_base() {
    local host="${1:-all}"
    echo -e "${BLUE}Deploying base system to ${host}...${NC}"
    cd "$SCRIPT_DIR"
    ansible-playbook -i inventory base.yml -l "$host"
}

# Deploy packages
deploy_packages() {
    local host="${1:-all}"
    echo -e "${BLUE}Deploying DX Cluster packages to ${host}...${NC}"
    cd "$SCRIPT_DIR"
    ansible-playbook -i inventory packages.yml -l "$host"
}

# Deploy docker
deploy_docker() {
    local host="${1:-all}"
    echo -e "${BLUE}Deploying Docker to ${host}...${NC}"
    cd "$SCRIPT_DIR"
    ansible-playbook -i inventory docker.yml -l "$host"
}

# Full deployment
deploy_full() {
    local host="${1:-all}"
    echo -e "${BLUE}Full deployment to ${host}...${NC}"
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Cancelled"
        exit 0
    fi
    cd "$SCRIPT_DIR"
    ansible-playbook -i inventory site.yml -l "$host"
}

# Check syntax
check_syntax() {
    echo -e "${BLUE}Checking playbook syntax...${NC}"
    cd "$SCRIPT_DIR"
    ansible-playbook --syntax-check site.yml base.yml packages.yml docker.yml
    echo -e "${GREEN}All playbooks have valid syntax${NC}"
}

# Validate playbook
validate_playbook() {
    local playbook="${1:-site.yml}"
    echo -e "${BLUE}Validating ${playbook}...${NC}"
    cd "$SCRIPT_DIR"
    ansible-playbook -i inventory --list-tasks "$playbook"
}

# Run ansible-lint
run_lint() {
    if ! command -v ansible-lint &> /dev/null; then
        echo -e "${YELLOW}ansible-lint not installed. Installing...${NC}"
        pip install ansible-lint
    fi
    echo -e "${BLUE}Running ansible-lint...${NC}"
    cd "$SCRIPT_DIR"
    ansible-lint site.yml base.yml packages.yml docker.yml
}

# Ping hosts
ping_hosts() {
    echo -e "${BLUE}Pinging all hosts...${NC}"
    cd "$SCRIPT_DIR"
    ansible all -i inventory -m ping
}

# List hosts
list_hosts() {
    echo -e "${BLUE}Inventory Hosts:${NC}"
    cd "$SCRIPT_DIR"
    ansible-inventory -i inventory --list
}

# List groups
list_groups() {
    echo -e "${BLUE}Inventory Groups:${NC}"
    cd "$SCRIPT_DIR"
    ansible-inventory -i inventory --graph
}

# Show status
show_status() {
    local host="${1:-all}"
    echo -e "${BLUE}Deployment status on ${host}...${NC}"
    cd "$SCRIPT_DIR"
    ansible "$host" -i inventory -m shell -a "dpkg -l | grep dxcluster; docker-compose version"
}

# Main
if [ $# -eq 0 ]; then
    print_help
    exit 0
fi

COMMAND="$1"
shift || true

case "$COMMAND" in
    init)
        init_ansible
        ;;
    check)
        check_connectivity "$@"
        ;;
    facts)
        gather_facts "$@"
        ;;
    base)
        deploy_base "$@"
        ;;
    packages)
        deploy_packages "$@"
        ;;
    docker)
        deploy_docker "$@"
        ;;
    full)
        deploy_full "$@"
        ;;
    syntax)
        check_syntax
        ;;
    validate)
        validate_playbook "$@"
        ;;
    lint)
        run_lint
        ;;
    ping)
        ping_hosts
        ;;
    list-hosts)
        list_hosts
        ;;
    list-groups)
        list_groups
        ;;
    vault-create)
        ansible-vault create "${1:-secrets.yml}"
        ;;
    vault-edit)
        ansible-vault edit "$1"
        ;;
    status)
        show_status "$@"
        ;;
    logs)
        show_status "$@"
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
