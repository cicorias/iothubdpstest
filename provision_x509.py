# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE at
# https://github.com/Azure/azure-iot-sdk-python/blob/main/LICENSE for
# license information.
# --------------------------------------------------------------------------
import os
import asyncio
from azure.iot.device import X509
from azure.iot.device.aio import ProvisioningDeviceClient
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message
import uuid
import sys


provisioning_host = os.getenv("PROVISIONING_HOST")
id_scope = os.getenv("PROVISIONING_IDSCOPE")
# registration_id = os.getenv("DPS_X509_REGISTRATION_ID")
messages_to_send = 10


async def main(registration_id):
    # x509 = X509(
    #     cert_file=os.getenv("X509_CERT_FILE"),
    #     key_file=os.getenv("X509_KEY_FILE"),
    #     pass_phrase=os.getenv("X509_PASS_PHRASE"),
    # )
    x509 = X509(
        cert_file=f'certificates/certs/{registration_id}-full-chain.cert.pem',
        key_file=f'certificates/private/{registration_id}.key.pem',
        # pass_phrase=os.getenv("X509_PASS_PHRASE"),
    )

    provisioning_device_client = ProvisioningDeviceClient.create_from_x509_certificate(
        provisioning_host=provisioning_host,
        registration_id=registration_id,
        id_scope=id_scope,
        x509=x509,
    )

    registration_result = await provisioning_device_client.register()

    print("The complete registration result is")
    print(registration_result.registration_state)

    if registration_result.status == "assigned":
        print("Will send telemetry from the provisioned device")
        device_client = IoTHubDeviceClient.create_from_x509_certificate(
            x509=x509,
            hostname=registration_result.registration_state.assigned_hub,
            device_id=registration_result.registration_state.device_id,
        )

        # Connect the client.
        await device_client.connect()

        async def send_test_message(i):
            print("sending message #" + str(i))
            msg = Message("test wind speed " + str(i))
            msg.message_id = uuid.uuid4()
            await device_client.send_message(msg)
            print("done sending message #" + str(i))

        # send `messages_to_send` messages in parallel
        await asyncio.gather(*[send_test_message(i) for i in range(1, messages_to_send + 1)])

        # finally, disconnect
        await device_client.disconnect()
    else:
        print("Can not send telemetry from the provisioned device")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("You must specify the Device ID")
        raise SystemExit(2)

    device_id = sys.argv[1]

    asyncio.run(main(device_id))

    # If using Python 3.6 use the following code instead of asyncio.run(main()):
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()