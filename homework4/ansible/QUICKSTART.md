# Ansible Quick Start

## One-Minute Setup

```bash
# 1. Install Ansible
pip install ansible

# 2. Configure your hosts in inventory
# Edit inventory file with your server IPs

# 3. Test connectivity
cd ansible
./deploy.sh ping

# 4. Deploy to dev
./deploy.sh full dev-server

# 5. Deploy to prod
./deploy.sh full prod-server
```

## Common Commands

```bash
# Check connectivity
./deploy.sh check prod-server

# Base system only
./deploy.sh base prod-server

# Deploy packages (deb)
./deploy.sh packages prod-server

# Deploy Docker containers
./deploy.sh docker prod-server

# Full deployment
./deploy.sh full prod-server

# Check syntax
./deploy.sh syntax

# View deployment status
./deploy.sh status prod-server

# List all hosts
./deploy.sh list-hosts

# List all groups
./deploy.sh list-groups

# Show help
./deploy.sh help
```

## Configuration Files

1. **inventory** - Define your hosts
   - Add your server IPs and names

2. **group_vars/all.yml** - Global settings
   - Deployment path, database config, versions
   - Customize as needed

3. **host_vars/[hostname].yml** - Per-host settings
   - Create for host-specific overrides

## Playbooks

- **site.yml** - Full deployment (all roles)
- **base.yml** - System setup only
- **packages.yml** - DX packages only
- **docker.yml** - Docker and containers only

## Roles

- **base** - System packages, users, directories
- **docker** - Docker Engine and Compose
- **dxcluster_packages** - dxcluster-database and dxcluster-scraper
- **dxcluster_docker** - dxcluster-api and dx-analysis containers

## Deployment Workflow

1. **Prepare**
   - Install Ansible: `pip install ansible`
   - Configure inventory with your hosts
   - Verify SSH access: `./deploy.sh ping`

2. **Validate**
   - Check syntax: `./deploy.sh syntax`
   - List tasks: `./deploy.sh validate site.yml`

3. **Test**
   - Deploy to dev: `./deploy.sh full dev-server`
   - Verify all components working

4. **Deploy**
   - Deploy to prod: `./deploy.sh full prod-server`
   - Check status: `./deploy.sh status prod-server`

## Troubleshooting

### Can't connect to host
```bash
# Check SSH
ssh debian@dev-server

# Check inventory
./deploy.sh list-hosts

# Test ping
./deploy.sh ping
```

### Package not found
```bash
# List available packages
ls -la ../../homework2/packages/*/

# Update versions in group_vars/all.yml
```

### Docker issues
```bash
# Check Docker status
ansible prod-server -i inventory -m shell -a "systemctl status docker"

# View Docker logs
ansible prod-server -i inventory -m shell -a "journalctl -u docker"
```

## File Locations (after deployment)

- **Deployment**: `/opt/dxcluster/`
- **Config**: `/opt/dxcluster/config/`
- **Logs**: `/opt/dxcluster/logs/`
- **Docker Compose**: `/opt/dxcluster/docker/docker-compose.yml`
- **Packages**: `/opt/dxcluster/packages/`
- **Docker Volumes**: `/opt/dxcluster/volumes/`

## Environment Variables

Set in `group_vars/all.yml`:

```yaml
deployment_user: dxcluster              # Deployment user
deployment_home: /opt/dxcluster         # Installation path
api_port: 8080                          # API port
db_host: localhost                      # Database host
dxcluster_database_version: 1.0.0-1    # Database version
dxcluster_scraper_version: 1.1.0-1     # Scraper version
```

## Next Steps

1. Configure `inventory` with your hosts
2. Update `group_vars/all.yml` if needed
3. Run: `./deploy.sh ping`
4. Run: `./deploy.sh full prod-server`
5. Check: `./deploy.sh status prod-server`

For detailed guide, see `README.md`
