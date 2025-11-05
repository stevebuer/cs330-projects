output "vultr_vm_id" {
  description = "Vultr instance ID"
  value       = try(vultr_instance.debian_vm[0].id, null)
}

output "vultr_vm_ip" {
  description = "Vultr instance public IPv4 address"
  value       = try(vultr_instance.debian_vm[0].main_ip, null)
}

output "vultr_vm_ipv6" {
  description = "Vultr instance public IPv6 address"
  value       = try(vultr_instance.debian_vm[0].v6_main_ip, null)
}

output "vultr_vm_details" {
  description = "Vultr instance details"
  value = try({
    id           = vultr_instance.debian_vm[0].id
    hostname     = vultr_instance.debian_vm[0].hostname
    region       = vultr_instance.debian_vm[0].region
    label        = vultr_instance.debian_vm[0].label
    main_ip      = vultr_instance.debian_vm[0].main_ip
    v6_main_ip   = vultr_instance.debian_vm[0].v6_main_ip
    status       = vultr_instance.debian_vm[0].status
  }, null)
}

output "libvirt_vm_id" {
  description = "LibVirt domain ID"
  value       = try(libvirt_domain.debian_vm[0].id, null)
}

output "libvirt_vm_ip" {
  description = "LibVirt VM IP address"
  value       = try(libvirt_domain.debian_vm[0].network_interface[0].addresses[0], null)
}

output "libvirt_vm_details" {
  description = "LibVirt VM details"
  value = try({
    id       = libvirt_domain.debian_vm[0].id
    name     = libvirt_domain.debian_vm[0].name
    vcpu     = libvirt_domain.debian_vm[0].vcpu
    memory   = libvirt_domain.debian_vm[0].memory
  }, null)
}

output "deployment_info" {
  description = "General deployment information"
  value = {
    environment = var.environment
    vm_name     = var.vm_name
    vm_size     = var.vm_size
    debian_version = var.debian_version
  }
}
