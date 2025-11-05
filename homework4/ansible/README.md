# Ansible Deployment Guide - DX Cluster

## Overview

This Ansible setup automates the deployment of the complete DX Cluster infrastructure on Debian-based systems. It handles:

- **Base System Setup**: Package updates, user creation, system configuration
- **Docker Installation**: Docker Engine, Docker Compose, registry authentication
- **DX Cluster Packages**: Deployment of dxcluster-database and dxcluster-scraper deb files
- **Docker Containers**: Deployment of dxcluster-api and dx-analysis Docker images

## Prerequisites

### Control Machine (where you run Ansible)
- Ansible 2.10+: `pip install ansible`
- Python 3.8+
- SSH access to target machines
- Inventory configured

### Target Machines (Debian 12)
- SSH server running
- Sudo access (or root)
- Internet connectivity
- ~2GB free disk space (minimum)

## Installation

### 1. Install Ansible

```bash
# Using pip (recommended)
pip install ansible

# Using apt on Debian/Ubuntu
sudo apt-get install ansible

# Verify installation
ansible --version
```

### 2. Configure Inventory

Edit `inventory` to define your target hosts:

```ini
[all:children]
development
production

[development]
dev-server ansible_host=192.168.1.100 ansible_user=debian

[production]
prod-server ansible_host=vultr.example.com ansible_user=root

[dxcluster_database]
prod-server
dev-server

[dxcluster_scraper]
prod-server
dev-server

[docker_hosts]
prod-server
dev-server
```

### 3. Set Up SSH Access

```bash
# Copy SSH key to target
ssh-copy-id -i ~/.ssh/id_rsa debian@dev-server
ssh-copy-id -i ~/.ssh/id_rsa root@prod-server

# Test connectivity
ansible all -i inventory -m ping
```

## Configuration

### Variables

Edit `group_vars/all.yml` to customize deployment:

```yaml
deployment_user: dxcluster
deployment_home: /opt/dxcluster
db_host: localhost
db_port: 5432
api_port: 8080
dxcluster_database_version: 1.0.0-1
dxcluster_scraper_version: 1.1.0-1
```

### Secrets (Vault)

For sensitive data, use Ansible Vault:

```bash
# Create encrypted secrets
./deploy.sh vault-create secrets.yml

# Edit secrets
./deploy.sh vault-edit secrets.yml

# Use in playbook
ansible-playbook site.yml --ask-vault-pass
```

## Deployment

### Quick Start

```bash
# Initialize
./deploy.sh init

# Check connectivity
./deploy.sh ping

# List hosts/groups
./deploy.sh list-hosts
./deploy.sh list-groups

# Validate syntax
./deploy.sh syntax

# Deploy to dev
./deploy.sh full dev-server

# Deploy to prod
./deploy.sh full prod-server
```

### Selective Deployment

```bash
# Base system only
./deploy.sh base prod-server

# Packages only
./deploy.sh packages prod-server

# Docker only
./deploy.sh docker prod-server
```

### Manual Ansible Commands

```bash
# Full site deployment
ansible-playbook -i inventory site.yml -l prod-server

# With vault
ansible-playbook -i inventory site.yml -l prod-server --ask-vault-pass

# Verbose output
ansible-playbook -i inventory site.yml -l prod-server -vvv

# Dry run
ansible-playbook -i inventory site.yml -l prod-server --check

# Specific tags
ansible-playbook -i inventory site.yml -l prod-server -t docker
```

## Playbooks

### site.yml
Full deployment including all roles (base, docker, packages, containers)

```bash
./deploy.sh full [host]
```

### base.yml
System configuration only (packages, users, permissions)

```bash
./deploy.sh base [host]
```

### packages.yml
Deploy DX Cluster deb packages (database, scraper)

```bash
./deploy.sh packages [host]
```

### docker.yml
Deploy Docker and DX Cluster containers (API, Analysis)

```bash
./deploy.sh docker [host]
```

## Role Structure

```
roles/
├── base/                    # System setup
│   └── tasks/
│       └── main.yml        # Update system, create users
├── docker/                 # Docker installation
│   ├── tasks/
│   │   └── main.yml       # Install Docker
│   ├── templates/
│   │   ├── docker-daemon.json.j2
│   │   └── docker-config.json.j2
│   └── handlers/
│       └── main.yml       # Service handlers
├── dxcluster_packages/    # Package deployment
│   └── tasks/
│       └── main.yml       # Install deb packages
└── dxcluster_docker/      # Container deployment
    ├── tasks/
    │   └── main.yml       # Docker Compose setup
    └── templates/
        ├── docker-compose-dxcluster.yml.j2
        ├── docker-compose.env.j2
        └── logrotate-docker.j2
```

## Variables and Configuration

### Host Variables

Define per-host config in `host_vars/<hostname>.yml`:

```yaml
# host_vars/prod-server.yml
deployment_environment: production
db_host: prod-postgres.example.com
api_port: 80
dxcluster_api_version: v1.2.0
dx_analysis_version: v1.0.0
```

### Group Variables

Define per-group config in `group_vars/<groupname>.yml`:

```yaml
# group_vars/production.yml
deployment_environment: production
scraper_interval: 60
# Inherit from all.yml, override as needed
```

## Deployment Verification

### Check Deployment Status

```bash
# Show installed packages and versions
./deploy.sh status prod-server

# Check Docker containers
ansible prod-server -i inventory -m shell -a "docker ps"

# Check services
ansible prod-server -i inventory -m shell -a "systemctl status docker"
```

### View Logs

```bash
# Service logs
ansible prod-server -i inventory -m shell -a "journalctl -u docker -n 50"

# Container logs
ansible prod-server -i inventory -m shell -a "docker logs dxcluster-api"

# Application logs
ansible prod-server -i inventory -m shell -a "tail -f /opt/dxcluster/logs/*.log"
```

## Troubleshooting

### SSH Connection Issues

```bash
# Test SSH
ssh -v debian@dev-server

# Check SSH key permissions
ls -la ~/.ssh/
chmod 700 ~/.ssh/
chmod 600 ~/.ssh/id_rsa

# Update inventory if needed
./deploy.sh list-hosts
```

### Package Not Found

```bash
# Verify packages exist
ls -la ../../homework2/packages/*/

# Check package versions in group_vars
grep -i "version" group_vars/all.yml

# Update version if needed
```

### Docker Issues

```bash
# Check Docker status
ansible prod-server -i inventory -m systemd -a "name=docker state=started"

# Verify Docker permissions
ansible prod-server -i inventory -m shell -a "docker ps"

# Check logs
ansible prod-server -i inventory -m shell -a "journalctl -u docker"
```

### Idempotency

Run deployment twice to verify idempotency:

```bash
./deploy.sh full prod-server
./deploy.sh full prod-server  # Should show "ok" not "changed"
```

## Tagging

Use tags to run specific parts of playbooks:

```bash
# Base system only
ansible-playbook site.yml --tags base

# Docker only
ansible-playbook site.yml --tags docker

# Packages only
ansible-playbook site.yml --tags packages

# Skip a role
ansible-playbook site.yml --skip-tags docker

# Multiple tags
ansible-playbook site.yml --tags "base,docker"
```

## Best Practices

1. **Always run --check first**
   ```bash
   ansible-playbook site.yml --check
   ```

2. **Use vault for secrets**
   ```bash
   ansible-vault create secrets.yml
   ```

3. **Validate syntax**
   ```bash
   ./deploy.sh syntax
   ```

4. **Test on dev first**
   ```bash
   ./deploy.sh full dev-server
   ```

5. **Use specific inventory groups**
   ```bash
   ansible-playbook site.yml -l production
   ```

## File Locations

After deployment:

- **Config**: `/opt/dxcluster/config/`
- **Logs**: `/opt/dxcluster/logs/`
- **Docker**: `/opt/dxcluster/docker/docker-compose.yml`
- **Packages**: `/opt/dxcluster/packages/`
- **Volumes**: `/opt/dxcluster/volumes/`

## Updating Components

### Update Packages

```bash
# Edit version in group_vars/all.yml
dxcluster_database_version: 1.0.0-1
dxcluster_scraper_version: 1.1.0-1

# Redeploy
./deploy.sh packages prod-server
```

### Update Docker Images

```bash
# Edit version in group_vars/all.yml
dxcluster_api_version: v1.2.0
dx_analysis_version: v1.0.0

# Redeploy
./deploy.sh docker prod-server
```

## Next Steps

1. Configure inventory with your hosts
2. Test connectivity: `./deploy.sh ping`
3. Run syntax check: `./deploy.sh syntax`
4. Deploy to dev: `./deploy.sh full dev-server`
5. Deploy to prod: `./deploy.sh full prod-server`

## Support

For issues:
1. Check `./deploy.sh` output
2. Run with verbose: `ansible-playbook site.yml -vvv`
3. Check logs: `journalctl -u docker`
4. Review role tasks

## References

- [Ansible Documentation](https://docs.ansible.com/)
- [Ansible Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)
- [Ansible Vault](https://docs.ansible.com/ansible/latest/user_guide/vault.html)
