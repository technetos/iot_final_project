import json
import asyncio
import aiohttp
import argparse
import os
import sys

import RPi.GPIO as GPIO
import MFRC522
import signal

client_uuid = 'df5c9486-2b2b-4cc8-a7bf-3bba73772d2f'

parser = argparse.ArgumentParser(description='RFID CLIENT')
parser.add_argument('-host', required=True, help="url host of the resource server")
parser.add_argument('-port', required=True, help="the port the resource server is running on")
parser.add_argument('-action', required=True, type=str)
parser.add_argument('-fname', help="the file to fetch")

args = vars(parser.parse_args())
api_base_path = "/heatshield/v1/"
resource_server = "http://" + args['host'] + ":" + args['port']

class LoginResponse(object):
    def __init__(self, data):
        self.access_token = data['access_token']
        self.expires_in = data['expires_in']
        self.refresh_token = data['refresh_token']
        self.token_type = data['token_type']

# Logout function
async def logout(access_token):
    url = resource_server + api_base_path + "logout"
    headers = {"Authorization": "Bearer " + access_token}

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(url, json={}) as response:
            return await response.json()

# Login function
async def login(username, password, client_id):
    url = resource_server + api_base_path + "token"

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={
            'client_id': client_id,
            'grant_type': 'password',
            'credentials': { 'username': username, 'password': password }
        }) as response:
            return await response.json() 

# Retrieve a users file from the backend
async def get_file(access_token):
    url = resource_server + "/rfid/v1/request_file"
    headers = {"Authorization": "Bearer " + access_token}

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(url, json={
            'fname': args['fname']
        }) as response:
            return await response.json()

# Demonstrate that we can use the access token for anything
async def unlock_door(access_token):
    url = resource_server + "/rfid/v1/unlock_door"
    headers = {"Authorization": "Bearer " + access_token}

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(url, json={}) as response:
            return await response.json()

# Read credentials from the rfid card/token
async def read_credentials():
    result = []
    continue_reading = True

    # Create an object of the class MFRC522
    MIFAREReader = MFRC522.MFRC522()

    while continue_reading:
        # Scan for cards    
        (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        # Get the UID of the card
        (status,uid) = MIFAREReader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == MIFAREReader.MI_OK:

            # This is the default key for the authentication built into the
            # card, we are not making use of this in this PoC
            key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]

            # Select the scanned tag
            MIFAREReader.MFRC522_SelectTag(uid)

            # Authenticate
            status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

            # Check if authenticated
            if status == MIFAREReader.MI_OK:
                result = MIFAREReader.MFRC522_Read(8)
                MIFAREReader.MFRC522_StopCrypto1()
                if len(result) != 0:
                    continue_reading = False
            else:
                # Authentication Error
                print("Error Reading Card")

    creds = ""
    for x in result:
        creds += str(chr(x))

    return creds

# Parse the data from the card, the structure is username|password|garbage
def parse_credentials(card_data):
    parsed_creds = card_data.partition('|')
    username = parsed_creds[0]
    password = parsed_creds[2].rstrip('|')
    return (username, password)

async def main():
    current_user = None
    url = resource_server + api_base_path

    async with aiohttp.ClientSession() as session:
        # Read card for credentials
        card_data = await read_credentials()

        # Parse into username and password
        username, password = parse_credentials(card_data)
        
        # Login
        user_data = await login(username, password, client_uuid)

        # If we are logged in
        if 'access_token' in user_data:
            current_user = LoginResponse(user_data)

            # unlock the door
            if args['action'] == "door":
                await unlock_door(current_user.access_token)
                print("Door unlocked")

            # retrieve a file
            elif args['action'] == "file":
                response = await get_file(current_user.access_token)
                print(response)

            # invalid option
            else:
                print("Unsupported action")

            # Logout once we are done
            did_logout = await logout(current_user.access_token)

            # If the api sent us an error message print the message
        elif 'error_message' in user_data:
            print(user_data['error_message'])
        else:
            # Otherwise simply deny access
            print("Unauthorized")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
