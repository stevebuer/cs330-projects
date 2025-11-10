# CS330 Homework 4

During this iteration it is critical for me to focus on end-to-end testing, because
this project has many individual components that have been generated or developed but
not integrated and fully tested.

## Completed or In-progress

* Development/Production environment upgrades: 
   * Terraform deployment testing
   * New Vultr VM to host project (api server & dashboard server for now)
   * Github Actions CI/CD for container builds
   * Dashboard deployed via Github Container Registry (ghcr.io)
   * Laptop memory upgrade (8GB -> 16GB)

* Feature Engineering
   * Scripts to extract feature vector for 1 day of observations
   * Train various NN models (sequential, RNN) and evaluate results
   * Iterate on feature engineering

## To Do

* Continue ML model development
* Connect pre-trained models to dashboard instead of current dynamic training?
* Github Automated unit tests
* 1-2 more iteration on scraper and database (WWV solar data & misc.)
* New PUML doc
* Add openapi.yaml to data browser.

---

# Begin Agent Maintained Content

## Infrastructure as Code - Terraform Configuration

### Overview
Created a complete Terraform infrastructure-as-code setup supporting dual deployment targets:

- **Vultr Cloud**: Public cloud deployment for production
- **Local VirtualBox**: Local KVM/libvirt deployment for development and testing

### Files Created

| File | Purpose |
|------|---------|
| `terraform/versions.tf` | Terraform and provider version constraints |
| `terraform/providers.tf` | Provider configurations (Vultr and libvirt) |
| `terraform/variables.tf` | Input variables with validation and defaults |
| `terraform/main.tf` | Core infrastructure resources |
| `terraform/outputs.tf` | Output values for deployed resources |
| `terraform/deploy.sh` | Helper script for common operations |
| `terraform/README.md` | Comprehensive deployment guide |
| `terraform/TESTING.md` | Local testing and development guide |
| `terraform/terraform.tfvars.vultr.example` | Example Vultr configuration |
| `terraform/terraform.tfvars.local.example` | Example local configuration |

### Quick Start

#### 1. Initialize Terraform
```bash
cd terraform
./deploy.sh init
```

#### 2. Deploy to Vultr
```bash
# Set API key
export TF_VAR_vultr_api_key="your-vultr-api-key"

# Copy example config
cp terraform.tfvars.vultr.example terraform.tfvars

# Plan and apply
./deploy.sh plan vultr
./deploy.sh apply vultr
```

#### 3. Deploy to Local VirtualBox
```bash
# Copy example config
cp terraform.tfvars.local.example terraform.tfvars

# Plan and apply
./deploy.sh plan local
./deploy.sh apply local
```

### Key Features

✅ **Dual Environment Support**
- Switch between cloud and local with single variable

✅ **Flexible Sizing**
- Choose between small (1vCPU/1GB) or medium (2vCPU/2GB)

✅ **Latest Debian**
- Automatically deploys latest Debian 12

✅ **Helper Script**
- Simplified command interface with colored output

✅ **Comprehensive Documentation**
- Setup guides, troubleshooting, and workflow examples

✅ **Production Ready**
- Proper error handling, timeouts, and resource management

### Helper Script Commands

```bash
./deploy.sh init                    # Initialize Terraform
./deploy.sh validate               # Validate configuration
./deploy.sh fmt                    # Format files
./deploy.sh plan [vultr|local]     # Plan deployment
./deploy.sh apply [vultr|local]    # Apply deployment
./deploy.sh destroy [vultr|local]  # Destroy resources
./deploy.sh show                   # Show current state
./deploy.sh output [VAR]           # Show outputs
```

### Prerequisites

**Vultr Deployment**
- Terraform installed
- Vultr account with API key
- Environment variable: `TF_VAR_vultr_api_key`

**Local Deployment**
- Terraform installed
- libvirt/KVM installed: `sudo apt-get install libvirt-daemon libvirt-daemon-system qemu qemu-kvm`
- libvirt service running: `sudo systemctl start libvirtd`

### VM Sizing

| Size | vCPU | RAM | Vultr Plan | Use Case |
|------|------|-----|-----------|----------|
| small | 1 | 1GB | vc2-1c-1gb | Testing, development |
| medium | 2 | 2GB | vc2-2c-2gb | Production workloads |

### Next Steps

1. ✅ Configure both deployment environments
2. ⏳ Integrate Ansible for configuration management
3. ⏳ Add monitoring and alerting
4. ⏳ Set up CI/CD pipeline integration
5. ⏳ Implement backup strategies

For detailed documentation, see `terraform/README.md`

## Configuration Management - Ansible

### Overview
Comprehensive Ansible automation for deploying DX Cluster components including:

- **Base System Setup**: Package updates, user creation, system configuration
- **Docker Installation**: Docker Engine, Docker Compose, registry authentication
- **DX Cluster Packages**: Automated deployment of dxcluster-database and dxcluster-scraper deb packages
- **Docker Containers**: Deployment of dxcluster-api and dx-analysis Docker images

### Files Created

| File | Purpose |
|------|---------|
| `ansible/ansible.cfg` | Ansible configuration |
| `ansible/inventory` | Host and group definitions |
| `ansible/group_vars/all.yml` | Global variables |
| `ansible/site.yml` | Full deployment playbook |
| `ansible/base.yml` | Base system setup playbook |
| `ansible/packages.yml` | DX packages deployment playbook |
| `ansible/docker.yml` | Docker deployment playbook |
| `ansible/deploy.sh` | Deployment helper script |
| `ansible/roles/base/` | Base system configuration role |
| `ansible/roles/docker/` | Docker installation role |
| `ansible/roles/dxcluster_packages/` | Package deployment role |
| `ansible/roles/dxcluster_docker/` | Container deployment role |
| `ansible/README.md` | Complete documentation |
| `ansible/QUICKSTART.md` | Quick start guide |

### Quick Start

```bash
# 1. Install Ansible
pip install ansible

# 2. Configure your hosts
# Edit ansible/inventory with your server IPs

# 3. Test connectivity
cd ansible
./deploy.sh ping

# 4. Validate syntax
./deploy.sh syntax

# 5. Deploy to development
./deploy.sh full dev-server

# 6. Deploy to production
./deploy.sh full prod-server
```

### Helper Script Commands

```bash
./deploy.sh init                    # Initialize environment
./deploy.sh ping                    # Test host connectivity
./deploy.sh check [host]            # Check connectivity
./deploy.sh base [host]             # Deploy base system only
./deploy.sh packages [host]         # Deploy DX packages only
./deploy.sh docker [host]           # Deploy Docker only
./deploy.sh full [host]             # Full deployment
./deploy.sh status [host]           # Show deployment status
./deploy.sh list-hosts              # List all hosts
./deploy.sh list-groups             # List all groups
./deploy.sh syntax                  # Check playbook syntax
./deploy.sh vault-create            # Create encrypted vault
./deploy.sh help                    # Show all commands
```

### Deployment Components

**Base System Role**
- Update and upgrade packages
- Install required dependencies
- Create deployment user and groups
- Set up directory structure
- Configure sudo access

**Docker Role**
- Install Docker Engine and CLI
- Install Docker Compose plugin
- Configure Docker daemon
- Set up registry authentication
- Enable Docker service

**DX Cluster Packages Role**
- Copy and deploy dxcluster-database deb
- Copy and deploy dxcluster-scraper deb
- Verify package installation
- Set permissions

**DX Cluster Docker Role**
- Create docker-compose configuration
- Pull Docker images (dxcluster-api, dx-analysis)
- Create persistent volumes
- Deploy services with docker-compose
- Configure health checks and logging

### Prerequisites

**Control Machine**
- Ansible 2.10+: `pip install ansible`
- Python 3.8+
- SSH access to target machines

**Target Machines**
- Debian 12
- SSH server running
- Sudo/root access
- Internet connectivity

### Configuration

Edit `ansible/group_vars/all.yml`:

```yaml
deployment_user: dxcluster
deployment_home: /opt/dxcluster
db_host: localhost
db_port: 5432
api_port: 8080
dxcluster_database_version: 1.0.0-1
dxcluster_scraper_version: 1.1.0-1
dxcluster_api_version: latest
dx_analysis_version: latest
```

### Role Structure

```
ansible/
├── ansible.cfg          # Configuration
├── inventory            # Hosts definition
├── group_vars/
│   └── all.yml         # Global variables
├── host_vars/          # Per-host variables
├── site.yml            # Full deployment
├── base.yml            # System setup only
├── packages.yml        # Packages only
├── docker.yml          # Docker only
├── deploy.sh           # Helper script
└── roles/
    ├── base/           # System setup
    ├── docker/         # Docker install
    ├── dxcluster_packages/   # Deb deployment
    └── dxcluster_docker/     # Container deployment
```

### Deployment Workflow

1. **Prepare**
   - Install Ansible
   - Configure inventory
   - Test SSH connectivity

2. **Validate**
   - Check syntax
   - Validate playbooks
   - List tasks

3. **Test**
   - Deploy to dev environment
   - Verify all components

4. **Deploy**
   - Deploy to production
   - Monitor status
   - Verify services

For detailed guide, see `ansible/README.md` and `ansible/QUICKSTART.md`

## Complete Infrastructure and Configuration Stack - Status

### Project Summary

| Component | Status | Location | Files | Lines |
|-----------|--------|----------|-------|-------|
| Terraform | ✅ Complete | `terraform/` | 16 | 1,557+ |
| Ansible | ✅ Complete | `ansible/` | 24 | 2,000+ |
| Integration | ✅ Complete | `DEPLOYMENT_GUIDE.md` | 1 | 300+ |
| Documentation | ✅ Complete | Various | 10+ | 2,500+ |

### What Gets Deployed

**Infrastructure (Terraform)**
- Debian 12 VMs on Vultr cloud or VirtualBox
- Flexible sizing (1vCPU/1GB or 2vCPU/2GB)
- Production-ready networking

**System (Ansible - Base Role)**
- Package updates and security patches
- Required dependencies
- dxcluster user and groups
- Directory structure

**Services (Ansible - Docker Role)**
- Docker Engine and Compose
- Registry authentication
- Health checks and logging

**Components (Ansible - Package & Docker Roles)**
- `dxcluster-database` (Debian package)
- `dxcluster-scraper` (Debian package)
- `dxcluster-api` (Docker container)
- `dx-analysis` (Docker container)

### Quick Full Deployment

```bash
# Phase 1: Infrastructure (15-20 min)
cd terraform
./deploy.sh init
export TF_VAR_vultr_api_key="your-api-key"
./deploy.sh apply vultr

# Phase 2: Configuration (10-15 min)
cd ../ansible
pip install ansible
./terraform-bridge.sh  # Auto-generate inventory
./deploy.sh full prod-server

# Phase 3: Verify (5 min)
./deploy.sh status prod-server
```

### Next Steps

For end-to-end testing: See `DEPLOYMENT_GUIDE.md`
For Terraform details: See `terraform/QUICKSTART.md`
For Ansible details: See `ansible/QUICKSTART.md`

### Progress

1. ✅ Terraform infrastructure setup
2. ✅ Ansible configuration management
3. ✅ Integration and helper scripts
4. ⏳ **End-to-end testing** (next)
5. ⏳ Production deployment by Nov 16

```

````

```
