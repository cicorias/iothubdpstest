output "azurerm_iothub_name" {
  value = azurerm_iothub.iothub.name
  description = "Name of the IoT Hub created to register devices against"
}

output "azurerm_iothub_dps_name" {
  value = azurerm_iothub_dps.dps.name
  description = "Name of the IoT Hub DPS instance created to register devices"
}

output "resource_group_name" {
  value = azurerm_resource_group.rg.name
  description = "Name of the resource group where all resources for this demo will live"
}

output "enrollment_group_create_command" {
  value = "az iot dps enrollment-group create -g ${azurerm_resource_group.rg.name} --dps-name ${azurerm_iothub_dps.dps.name} --enrollment-id x509-test-devices --certificate-path ./certificates/certs/azure-iot-test-only.intermediate.cert.pem"
  description = "Command that must be run to create an enrollment group with x509 cert attestation"
}

output "environment_variable_setup" {
  value = <<-COMMAND
        export PROVISIONING_HOST=global.azure-devices-provisioning.net
        export PROVISIONING_IDSCOPE=${azurerm_iothub_dps.dps.id_scope}
        COMMAND
  description = "Command to set environment variables needed to find the right DPS instance"
}