output "vm_names" {
  description = "Names of the created VMs"
  value       = virtualbox_vm.node[*].name
}

output "vm_ips" {
  description = "IP addresses of the VMs"
  value = [
    for vm in virtualbox_vm.node : try(vm.network_adapter[0].ipv4_address, "pending")
  ]
}

output "vm_cpus" {
  description = "CPU count for each VM"
  value       = virtualbox_vm.node[*].cpus
}

output "vm_memory" {
  description = "Memory allocation for each VM in MB"
  value       = virtualbox_vm.node[*].memory
}

output "ssh_connection_strings" {
  description = "SSH connection strings for VMs"
  value = [
    for i, vm in virtualbox_vm.node : format("ssh -p 2222%d debian@127.0.0.1", 20 + i)
  ]
}

output "vm_details" {
  description = "Detailed information about VMs"
  value = {
    for i, vm in virtualbox_vm.node : vm.name => {
      cpus        = vm.cpus
      memory_mb   = vm.memory
      image       = vm.image
      status      = "created"
    }
  }
}

output "environment_info" {
  description = "Environment configuration summary"
  value = {
    environment = var.environment_name
    debian_version = var.debian_version
    vm_count = var.vm_count
    cpus_per_vm = var.vm_cpus
    memory_per_vm = var.vm_memory_mb
  }
}
