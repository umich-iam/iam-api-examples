import argparse
import configparser
import requests
import json


# Read sensitive data from a configuration file that is not stored in git
config_file = configparser.ConfigParser()
config_file.read("example.ini")
config = config_file["apiexample"]
api_url = config.get("API_URI")


def public_people_find(uid):
    """
    Example API call against the /people/find/ endpoint
    This example searches for an exact match uid (uniqname)
    """
    payload = {
        'searchParts': [
            {
                'attribute': 'uid',
                'value': uid,
                'searchType': 'exact',
            }
        ],
        'logicalOperator': None,
        'attributes': ['uid', 'mail'],
    }
    headers = {
        'Content-type': 'application/json',
        'Accept': 'application/json',
    }


    response = requests.post(
        f'{api_url}/people/find/',
        data=json.dumps(payload),
        headers=headers,
    )
    print(f'Printing response for method={response.request.method} url={response.request.url} body={response.request.body}')
    print(f'status_code={response.status_code} json={response.json()}')


if __name__ == '__main__':
    # Read arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--uniqname', '-u', help='Enter the uniqname', required=True)
    args = parser.parse_args()
    uid = args.uniqname

    public_people_find(uid)
