"""
Retrieve information about a specific group using the MCommunity API
This is a basic usage example; you should add appropriate error handling
"""

import configparser
import requests


# Read sensitive data from a configuration file that is not stored in git
config_file = configparser.ConfigParser()
config_file.read("example.ini")
config = config_file["apiexample"]

api_app_id_dn = config.get("APPID_DN")
api_app_id_password = config.get("APPID_PW")
group_name = config.get("GROUP_NAME")
api_uri = config.get("API_URI")

# Obtain an API access token and build the Authorization header
token_uri = f"{api_uri}/token/"
token_body = {
     "username": api_app_id_dn,
     "password": api_app_id_password
}
r = requests.post(token_uri, data=token_body)
response_dict = r.json()

access_token = response_dict["access"]
auth_header = {"Authorization": f"Bearer {access_token}"}

# Get information about a specific group. API token must be passed in the Authorization header
group_uri = f"{api_uri}/groups/{group_name}/"
r = requests.get(group_uri, headers=auth_header)
print(r.text)
