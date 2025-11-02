terraform {
  required_version = ">= 1.0"
  required_providers {
    vultr = {
      source  = "vultr/vultr"
      version = "~> 2.15"
    }
  }
}

provider "vultr" {
  api_key = var.vultr_api_key
  # Rate limiting configuration
  rate_limit = 600
  retry_rate_limit = 2
}

# Data source for Debian latest image
data "vultr_os" "debian" {
  filter {
    name   = "name"
    values = ["Debian ${var.debian_version}"]
  }
}

# Data source for instance type
data "vultr_plan" "instance" {
  filter {
    name   = "name"
    values = [var.instance_type]
  }
}

# Data source for region
data "vultr_region" "primary" {
  filter {
    name   = "code"
    values = [var.vultr_region]
  }
}

# SSH Key for VM access
resource "vultr_ssh_key" "main" {
  name    = "${var.environment_name}-ssh-key"
  ssh_key = file(var.ssh_key_path)

  tags = {
    Environment = var.environment_name
    Project     = "dx-predictor"
  }
}

# VPC Network for production environment
resource "vultr_vpc" "main" {
  description = "VPC for ${var.environment_name} environment"
  region      = var.vultr_region
  
  tags = {
    Environment = var.environment_name
    Project     = "dx-predictor"
  }
}

# Production VM Instance
resource "vultr_instance" "main" {
  count       = var.vm_count
  plan        = data.vultr_plan.instance.id
  region      = data.vultr_region.primary.id
  os_id       = data.vultr_os.debian.id
  label       = "${var.environment_name}-vm-${count.index + 1}"
  ssh_key_ids = [vultr_ssh_key.main.id]
  
  # Enable automatic backups
  backups = "enabled"
  
  # VPC attachment
  vpc_ids = [vultr_vpc.main.id]

  tags = {
    Environment = var.environment_name
    Project     = "dx-predictor"
    Index       = count.index + 1
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Firewall for production VMs
resource "vultr_firewall" "main" {
  description = "Firewall for ${var.environment_name} environment"

  # SSH access
  inbound_rule {
    protocol = "tcp"
    port     = "22"
    cidr     = var.allowed_ssh_cidr
  }

  # HTTP
  inbound_rule {
    protocol = "tcp"
    port     = "80"
    cidr     = "0.0.0.0/0"
  }

  # HTTPS
  inbound_rule {
    protocol = "tcp"
    port     = "443"
    cidr     = "0.0.0.0/0"
  }

  # API port (8080)
  inbound_rule {
    protocol = "tcp"
    port     = "8080"
    cidr     = "0.0.0.0/0"
  }

  # Streamlit port (8501)
  inbound_rule {
    protocol = "tcp"
    port     = "8501"
    cidr     = "0.0.0.0/0"
  }

  # Outbound - allow all
  outbound_rule {
    protocol = "tcp"
    cidr     = "0.0.0.0/0"
    port     = "1:65535"
  }

  outbound_rule {
    protocol = "udp"
    cidr     = "0.0.0.0/0"
    port     = "1:65535"
  }

  tags = {
    Environment = var.environment_name
    Project     = "dx-predictor"
  }
}

# Attach firewall to instances
resource "vultr_firewall_rule" "main" {
  count           = var.vm_count
  firewall_id     = vultr_firewall.main.id
  instance_ids    = [vultr_instance.main[count.index].id]
  group           = "vultr_instances"
}

# Reserved IP for production (optional but recommended)
resource "vultr_reserved_ip" "main" {
  count    = var.enable_reserved_ip ? var.vm_count : 0
  region   = var.vultr_region
  ip_type  = "v4"
  label    = "${var.environment_name}-reserved-ip-${count.index + 1}"

  tags = {
    Environment = var.environment_name
    Project     = "dx-predictor"
  }
}

# Attach reserved IP to instances
resource "vultr_reserved_ip_assignment" "main" {
  count           = var.enable_reserved_ip ? var.vm_count : 0
  reserved_ip     = vultr_reserved_ip.main[count.index].id
  instance_id     = vultr_instance.main[count.index].id
}
