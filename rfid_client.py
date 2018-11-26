import json
import asyncio
import aiohttp
import argparse
import os

parser = argparse.ArgumentParser(description='RFID CLIENT')
parser.add_argument('-host', help="url host of the resource server")
parser.add_argument('-port', help="the port the resource server is running on")
parser.add_argument('-fname', help="the filename")

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

# Retrieve the encryption key for a file from the resource server
async def get_file_decryption_key(access_token):
    url = resource_server + "/rfid/v1/request_key"
    headers = {"Authorization": "Bearer " + access_token}

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(url, json={
            'fname': args['fname']
        }) as response:
            return await response.json()

async def main():
    current_user = None
    url = resource_server + api_base_path
    async with aiohttp.ClientSession() as session:
        user_data = await login('rfidpi', 'iotthing', 'df5c9486-2b2b-4cc8-a7bf-3bba73772d2f')
        current_user = LoginResponse(user_data)
        key = await get_file_decryption_key(current_user.access_token)
        print(key)
        did_logout = await logout(current_user.access_token)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
