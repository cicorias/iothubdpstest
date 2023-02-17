# iothubdpstest
Learn how to provision devices with DPS for IoT Hub without an SDK (because cURL is our friend).

## Prerequisites
Install Azure CLI and run the following commands:
```sh
az login
az account set -n YOUR_SUBSCRIPTION_NAME_OR_ID
```

Now go into the [dps/terraform](./dps/terraform/) folder and run `terraform apply -auto-approve`

You created a resource group, IoT Hub, DPS instance, and mapped the IoT Hub to your DPS instance.
