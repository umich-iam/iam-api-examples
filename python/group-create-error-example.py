"""
Example of an error returned from group creation
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

# Try to create a group with data errors (duplicate member value in this case)
group_uri = f"{api_uri}/groups/"
r = requests.post(group_uri, headers=auth_header,data={
            "cn": "api-test-1",
            "umichGroupEmail": "api-test-1",
            "owner": ["uid=ethierba,ou=People,dc=umich,dc=edu"],
            "member": ["uid=ethierba,ou=People,dc=umich,dc=edu", "uid=ethierba,ou=People,dc=umich,dc=edu"],
            "umichDescription": "endpoint test",
        })
print(f'{r.status_code} {r.text}')
