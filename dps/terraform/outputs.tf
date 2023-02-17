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