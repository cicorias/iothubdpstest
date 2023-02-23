#!python3

import json
import os
import sys
import time

import requests

PROVISIONING_HOST = os.environ.get('PROVISIONING_HOST')
PROVISIONING_IDSCOPE = os.environ.get('PROVISIONING_IDSCOPE')
dps_url = f'https://{PROVISIONING_HOST}/{PROVISIONING_IDSCOPE}'

def registration_url(registration_id,
                    api_version='2021-06-01'):
    return f'{dps_url}/registrations/{registration_id}/register?api-version={api_version}'

def operation_status_url(registration_id,
                    operation_id,
                    api_version='2021-06-01'):
    return f'{dps_url}/registrations/{registration_id}/operations/{operation_id}?api-version={api_version}'

def registration_request(device_id):
    payload = {'registrationId': device_id}
    headers = {'Content-Encoding':  'utf-8'}
    response = requests.put(registration_url(device_id),
                    json=payload,
                    headers=headers,
                    cert=f'certificates/private/{device_id}.store.pem')
    if response.status_code < 200 and response.status_code >= 300:
        return ''
    json_response = json.loads(response.text)
    print(json.dumps(json_response, indent=2))
    return json_response['operationId']

def operation_status_request(device_id, operation_id):
    headers = {
        'Content-Encoding':  'utf-8',
        'Content-Type': 'application/json',
        }
    response = requests.get(operation_status_url(device_id, operation_id),
                    headers=headers,
                    cert=f'certificates/private/{device_id}.store.pem')
    if response.status_code < 200 and response.status_code >= 300:
        print(f'Request failed with status {response.status_code}')
        print(f'Response: {response.text}')
        return ''
    json_response = json.loads(response.text)
    print(json.dumps(json_response, indent=2))
    registration_status = json_response['status']
    if registration_status != 'assigned':
        print(f'Waiting for device to be assigned. Current status: {registration_status}')
        return ''
    return json_response['registrationState']['assignedHub']


def main():
    if len(sys.argv) < 2:
        print("You must specify the Device ID")
        raise SystemExit(2)

    device_id = sys.argv[1]
    operation_id = registration_request(device_id)

    if operation_id == '':
        print("Registration failed")
        raise SystemExit(2)

    for attempt in range(4):
        time.sleep(pow(2, attempt))
        print(f'Checking registration status. Attempt {attempt+1} out of 5...')
        assignedHub = operation_status_request(device_id, operation_id)
        if assignedHub != '':
            print(f'Assigned endpoint: {assignedHub}')
            break

    if assignedHub == '':
        print("Registration checks timed out")
        raise SystemExit(2)


if __name__ == "__main__":
    main()