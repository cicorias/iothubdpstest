# IoT Hub Device Provisioning Service Test
Learn how to provision devices with DPS for IoT Hub and testing connectivity.

## Quickstart
If you haven't used this repo before, I recommend you follow through with the next sections; however, if you've been here before and just want the commands to get started, simply fulfill the [prerequisites](#prerequisites) and run the [TL;DR](#tldr).

## Context and References
- [Python 3.7](https://www.python.org/) or newer and [pip3](https://pip.pypa.io/en/stable/) in your machine (test with `python3 --version`)
- [IoT Hub documentation](https://learn.microsoft.com/en-us/azure/iot-hub/)
- [IoT Hub Device Provisioning Services (DPS) documentation](https://learn.microsoft.com/en-us/azure/iot-dps/)
- This repo is pretty much a simplification of a few [learn.microsoft.com](https://learn.microsoft.com) guides put together:
  - [Quickstart: Use Terraform to create an Azure IoT Device Provisioning Service](https://learn.microsoft.com/en-us/azure/iot-dps/quick-setup-auto-provision-terraform?tabs=bash)
  - [Tutorial: Use Microsoft-supplied scripts to create test certificates](https://learn.microsoft.com/en-us/azure/iot-hub/tutorial-x509-scripts)
  - [Tutorial: Provision multiple X.509 devices using enrollment groups](https://learn.microsoft.com/en-us/azure/iot-dps/tutorial-custom-hsm-enrollment-group-x509?tabs=linux&pivots=programming-language-python)
- The guides above will make use of [these **demo** scripts from Microsoft](https://github.com/Azure/azure-iot-sdk-c/tree/main/tools/CACertificates)


## Prerequisites
Follow all sections below.

### Repo
First clone this repo and go into the repo's root directory to get started.

### OpenSSL
Make sure that you have [openssl](https://www.openssl.org/) installed. Run `openssl version` to confirm.

### Azure Subscription and CLI tool
Install Azure CLI and run the following commands:
```sh
az login
# Run the commented command below if you don't know your subscription name/ID and want to see your subscriptions to select one
# az account list -o table
az account set -n YOUR_SUBSCRIPTION_NAME_OR_ID
```

### Azure IoT Extension
Run the following command:
```sh
az extension add --name azure-iot
```

## Creating Certificates

This repo ignores certificate files, keys and other magical constructs you'll need to generate, so go into the [certificates](/certificates/) directory and run the following commands to generate them:
```sh
chmod 700 certGen.sh
./certGen.sh create_root_and_intermediate
```

The commands above generate root and intermediate certificates and keys in the same chain. You can also use Microsoft demo scripts to generate leaf (device) certificates and keys. Simply run the same script with the `create_device_certificate_from_intermediate` subcommand and **one argument that provides the device ID**. That part isn't bolded by accident: The device ID must match the Common Name (CN) in the device certificate! The device ID will be used when registering the device to an IoT Hub using DPS.

Let's create 2 certificates from the intermediate cert for our tests:
```sh
./certGen.sh create_device_certificate_from_intermediate testdevice1
./certGen.sh create_device_certificate_from_intermediate testdevice2
```

You must be wondering, why 2 devices? I don't know, why not 3? Or 1? Do as you wish.

## Setting up Infrastructure
We need to create all the Azure resources and configuration needed to connect devices. This repo has scripts to set that up for you.

### Terraform
Now, go to the root of this repo and run:
```sh
terraform init
terraform apply -auto-approve
```

You created a resource group, IoT Hub, DPS instance, and mapped the IoT Hub to your DPS instance. To make things simpler, terraform also [uploaded and verified your generated root certificate automatically](https://learn.microsoft.com/en-us/azure/iot-dps/how-to-verify-certificates#automatic-verification-of-intermediate-or-root-ca-through-self-attestation).

### Creating an Enrollment Group
Because Enrollment Groups are part of an IoT Hub DPS extension and not the main ARM APIs, we need to create the enrollment group using az cli instead of terraform (sadness). There are terraform workarounds, but I don't like them. Here's the command that you need to run for the enrollment group creation:
```sh
# The command looks something like the commented one below, but we will grab resource_group_name and dps_name from Terraform, so terraform will give us the command ready to execute as one of its outputs.
# az iot dps enrollment-group create -g {resource_group_name} --dps-name {dps_name} --enrollment-id x509-test-devices --certificate-path "./certificates/certs/azure-iot-test-only.intermediate.cert.pem"
$(terraform output -raw enrollment_group_create_command)
```

## Provisioning and Testing Devices
Now that you have set everything up, you can run a python script that will simulate device provisioning and messages.

### Monitor IoT Hub Messages (Optional)
Before starting connections and sending messages, you may want to view the messages received by IoT Hub. If you do, simply run the following command in a separate terminal session that will start listening to messages sent to the IoT Hub created by previous steps:
```sh
az iot hub monitor-events --hub-name $(terraform output -raw azurerm_iothub_name) --output json
```

### Export Environment Variables for Infrastructure
This repo includes a nice terraform output that exports the environment variables identifying your DPS location (host) and its ID Scope. Simply run the command below and your backend environment variables will be set:
```sh
$(terraform output -raw environment_variable_setup)
```

### Run Simulated Connection
Install python requirements first
```sh
pip3 install -r requirements.txt
```

Now simulate our two devices being provisioned and sending 10 messages each:
```sh
python3 provision_x509.py testdevice1
python3 provision_x509.py testdevice2
```

You're free to run that command with other device IDs based on the certs that you create. Fun fact: The Python SDK uses MQTT to provision devices.

## TL;DR
All the commands that you need without too much context.

```sh
az extension add --name azure-iot
# CERTS
cd certificates
chmod 700 certGen.sh
./certGen.sh create_root_and_intermediate
./certGen.sh create_device_certificate_from_intermediate testdevice1
./certGen.sh create_device_certificate_from_intermediate testdevice2
cd ..

# INFRA
terraform init -upgrade
terraform apply -auto-approve
$(terraform output -raw enrollment_group_create_command)

# DEVICES
# Optional line commented below to monitor events to the created IoT Hub (use a separate terminal session for this)
# az iot hub monitor-events --hub-name $(terraform output -raw azurerm_iothub_name) --output json
$(terraform output -raw environment_variable_setup)
pip3 install -r requirements.txt
python3 provision_x509.py testdevice1
python3 provision_x509.py testdevice2
```

Happy IoTying!
