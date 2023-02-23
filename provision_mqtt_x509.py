import time
from dotenv import load_dotenv

load_dotenv()

import asyncio
import os
import ssl
import paho.mqtt.client as mqtt

class MqttSubscriber:
    def __init__(self, broker_url, broker_port, subscribe_topic, publish_topic, message_to_wait):
        self.env = {}
        self.load_env_dict()
        self.broker_url = broker_url
        self.broker_port = broker_port
        self.subscribe_topic = subscribe_topic
        self.publish_topic = publish_topic
        self.message_to_wait = message_to_wait

        self.mqtt_client = mqtt.Client(client_id=self.env['AZ_IOT_PROVISIONING_REGISTRATION_ID'],
                                       clean_session=True,
                                       protocol=mqtt.MQTTv311,
                                       transport="tcp")
        
        # self.loop = asyncio.get_running_loop()

        # Set up the MQTT client
        self.mqtt_client.tls_set(ca_certs=self.env['AZ_IOT_DEVICE_X509_TRUST_PEM_FILE_PATH'],
                    certfile=self.env['AZ_IOT_DEVICE_X509_CERT_PEM_FILE_PATH'], 
                    keyfile=self.env['AC_IOT_DEVICE_X509_KEY_PEM_FILE_PATH'],
                    cert_reqs=ssl.CERT_REQUIRED,
                    # keyfile_password=AC_IOT_DEVICE_X509_KEY_PEM_FILE_PATH_password, 
                    tls_version=ssl.PROTOCOL_TLSv1_2)
        
        username = f"{self.env['AZ_IOT_PROVISIONING_ID_SCOPE']}/registrations/{self.env['AZ_IOT_PROVISIONING_REGISTRATION_ID']}/api-version=2019-03-31"
        print("username: " + username)
        self.mqtt_client.username_pw_set(username, password=None)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.on_subscribe = self.on_subscribe
        self.mqtt_client.on_unsubscribe = self.on_unsubscribe
        self.mqtt_client.connect(self.broker_url, self.broker_port)


    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        print("Connected to MQTT broker")
        client.subscribe(self.subscribe_topic, qos=1)

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print("Subscribed to topic: " + self.subscribe_topic)
        time.sleep(5)
        client.publish(self.publish_topic, payload=None, qos=1)
        print("Published to topic: " + self.publish_topic)

    def on_unsubscribe(self, client, userdata, mid):
        print("Unsubscribed from topic: " + self.subscribe_topic)

    def on_disconnect(self, client, userdata, rc):
        print("Disconnected from MQTT broker with result code: " + str(rc))
        self.mqtt_client.loop_stop()

    def on_message(self, client, userdata, message):
        print("Received message: " + message.payload.decode())
        if message.payload.decode() == self.message_to_wait:
            print("Exit message received: " + message.payload.decode())
            self.mqtt_client.disconnect()
            self.mqtt_client.loop_stop()
            # self.loop.stop()

    def start(self):
        print("Starting MQTT subscriber")
        # t = self.loop.create_task(self.start_mqtt_loop())
        self.start_mqtt_loop()
        # t.env = self.env
        # self.loop.run_forever()

    def start_mqtt_loop(self):
        self.mqtt_client.loop_forever() #.loop_start()
        print("MQTT loop started")


    def load_env_dict(self):
        print("Loading environment variables")
        env_keys = ['AZ_IOT_DEVICE_X509_CERT_PEM_FILE_PATH',
                    'AZ_IOT_PROVISIONING_ID_SCOPE', 
                    'AZ_IOT_PROVISIONING_REGISTRATION_ID',
                    'AZ_IOT_DEVICE_X509_CERT_PEM_FILE_PATH',
                    'AC_IOT_DEVICE_X509_KEY_PEM_FILE_PATH',
                    'AZ_IOT_DEVICE_X509_TRUST_PEM_FILE_PATH',
                    'AZ_IOT_PROVISIONING_ENDPOINT']

        for key in env_keys:
            print("key: " + key)
            if key in os.environ:
                self.env[key] = os.environ.get(key)
            else:
                print("Environment variable " + key + " not found")
                exit(1)


if __name__ == "__main__":
    sub_topic = "$dps/registrations/res/#"
    pub_topic = "$dps/registrations/PUT/iotdps-register/?$rid=1"

    dps_url = "global.azure-devices-provisioning.net"
    dps_port = 8883


    subscriber = MqttSubscriber(dps_url , 8883, sub_topic, pub_topic, None)
    subscriber.start()
