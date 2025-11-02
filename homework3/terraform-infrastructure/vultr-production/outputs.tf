output "instance_ids" {
  description = "IDs of the Vultr instances"
  value       = vultr_instance.main[*].id
}

output "instance_labels" {
  description = "Labels of the Vultr instances"
  value       = vultr_instance.main[*].label
}

output "instance_ips" {
  description = "IPv4 addresses of the Vultr instances"
  value       = vultr_instance.main[*].main_ip
}

output "instance_ipv6" {
  description = "IPv6 addresses of the Vultr instances"
  value       = vultr_instance.main[*].v6_main_ip
}

output "reserved_ips" {
  description = "Reserved IP addresses"
  value       = var.enable_reserved_ip ? vultr_reserved_ip.main[*].ip : []
}

output "ssh_connection_strings" {
  description = "SSH connection strings for instances"
  value = [
    for i, instance in vultr_instance.main : format("ssh root@%s", instance.main_ip)
  ]
}

output "firewall_id" {
  description = "ID of the main firewall"
  value       = vultr_firewall.main.id
}

output "vpc_id" {
  description = "ID of the VPC network"
  value       = vultr_vpc.main.id
}

output "ssh_key_id" {
  description = "ID of the SSH key"
  value       = vultr_ssh_key.main.id
}

output "region_id" {
  description = "ID of the Vultr region"
  value       = data.vultr_region.primary.id
}

output "os_id" {
  description = "ID of the Debian OS"
  value       = data.vultr_os.debian.id
}

output "instance_details" {
  description = "Detailed information about instances"
  value = {
    for i, instance in vultr_instance.main : instance.label => {
      id             = instance.id
      main_ip        = instance.main_ip
      ipv6_main_ip   = instance.v6_main_ip
      region         = instance.region
      status         = instance.status
      power_status   = instance.power_status
      date_created   = instance.date_created
    }
  }
}
