from decouple import config
import json
import requests

# api_url = 'https://mcommunity-api-dev.dsc.umich.edu'  # TODO: update as needed
api_url = 'http://localhost:8000'

class Authorize:
    _access_token = None
    _refresh_token = None

    @staticmethod
    def _obtain_access_token():
        url = f'{api_url}/api/token/'
        r = requests.post(url=url, json={"username": config("APP_ID"),
                                         "password": config("APP_ID_PW")})
        response_json = r.json()
        Authorize._access_token = response_json["access"]
        Authorize._refresh_token = response_json["refresh"]

    @staticmethod
    def _refresh_access_token():
        url = f'{api_url}/api/token/refresh/'
        r = requests.post(url=url, json={"refresh": Authorize._refresh_token})
        response_json = r.json()
        Authorize._access_token = response_json["access"]
        Authorize._refresh_token = None

    @staticmethod
    def _is_access_token_expired():
        # Test access token by trying to access an endpoint that requires authentication
        url = f'{api_url}/groups/'
        r = requests.get(url=url, headers={"Authorization": f"Bearer {Authorize._access_token}"})
        if r.status_code == 401:
            return True
        return False

    @staticmethod
    def get_auth_header():
        if Authorize._access_token is None:
            Authorize._obtain_access_token()
            return {"Authorization": f"Bearer {Authorize._access_token}"}
        if Authorize._is_access_token_expired():
            if Authorize._refresh_token is None:
                Authorize._obtain_access_token()
            else:
                Authorize._refresh_token()
            return {"Authorization": f"Bearer {Authorize._access_token}"}


class People:
    base_url = api_url + '/people'
    uniqname = 'frnkwang'  # TODO: Will this need to be changed?

    # GET /people/
    def get_people(self):
        url = f'{self.base_url}/'
        r = requests.get(url=url)
        return json.dumps(r.json(), indent=4)

    # POST /people/search/
    def post_people_search(self):
        url = f'{self.base_url}/search/'

        # searchType_options = ["start", "end", "contain", "exact"]'
        searchParts = [{"attribute": "ou",
                        "value": "Student",
                        "searchType": "contain"},
                       {"attribute": "givenName",
                        "value": "John",
                        "searchType": "start"}]

        attributes = ["displayName"]

        data = {"searchParts": searchParts,
                "numEntries": 3,
                "logicalOperator": "AND",  # AND or OR
                "attributes": attributes}

        r = requests.post(url=url, json=data)
        return json.dumps(r.json(), indent=4)

    # GET /people/{id}/
    def get_people_id(self):
        url = f'{self.base_url}/{self.uniqname}/'
        r = requests.get(url=url)
        return json.dumps(r.json(), indent=4)

    # PATCH /people/{id}/
    def patch_people_id(self):
        # TODO: do we need this example? Not sure if users could do this anyway
        pass

    # GET /people/{id}/name_coach/
    def get_people_id_name_coach(self):
        url = f'{self.base_url}/{self.uniqname}/name_coach/'
        r = requests.get(url=url)
        return json.dumps(r.json(), indent=4)

    # GET /people/{id}/vcard/
    # Requires authorization
    def get_people_id_vcard(self):
        # TODO: do we need this example? Current App ID auth token gives insufficient access rights
        url = f'{self.base_url}/{self.uniqname}/vcard/'
        auth_header = Authorize.get_auth_header()
        r = requests.get(url=url, headers=auth_header)
        return json.dumps(r.json(), indent=4)

class Groups:
    base_url = f'{api_url}/groups'
    uniqname = 'jbensen'
    user_dn = f'uid={uniqname},ou=People,dc=umich,dc=edu'
    group_cn = 'this is my fun-fun-fun group'

    # POST /groups/
    # Create a new Group
    def create_groups(self):
        url = f'{self.base_url}/'
        data = {
            "cn": "this is my fun-fun-fun group",
            "umichGroupEmail": "funfunfun",
            "owner": [
                "uid=jbensen,ou=People,dc=umich,dc=edu",
                "uid=bjensen,ou=People,dc=umich,dc=edu"
            ],
            "umichDescription": "This describes the fun of this group"
        }
        r = requests.post(url=url, json=data)
        return json.dumps(r.json(), indent=4)

    # GET /groups/{group_cn}/
    def get_groups_cn(self):
        url = f'{self.base_url}/{self.group_cn}/'
        r = requests.get(url=url)
        return json.dumps(r.json(), indent=4)

    # DELETE /groups/{group_cn}/
    def delete_group_cn(self):
        # TODO: owner?
        url = f'{self.base_url}/{self.group_cn}/'
        r = requests.delete(url=url)
        return json.dumps(r.json(), indent=4)

    # PATCH /groups/{group_cn}/
    def patch_group_cn(self):
        url = f'{self.base_url}/{self.group_cn}/'
        data = {
            "umichDescription": "This is a new description",
            "joinable": True
        }
        r = requests.patch(url=url, json=data)
        return json.dumps(r.json(), indent=4)

    # POST /groups/{group_cn}/renew/
    def renew_group_cn(self):
        url = f'{self.base_url}/{self.group_cn}/renew/'
        r = requests.post(url=url)
        return json.dumps(r.json(), indent=4)

    # POST /groups/{group_cn}/expire/
    def expire_group_cn(self):
        url = f'{self.base_url}/{self.group_cn}/expire/'
        # days' value from 7 to 365
        data = {"days": 7}
        r = requests.post(url=url, json=data)
        return json.dumps(r.json(), indent=4)

    # POST /groups/{group_cn}/<attribute>/
    def attr_group_cn(self):
        attribute = 'member'  # supporting attributes listed in google doc
        url = f'{self.base_url}/{self.group_cn}/{attribute}/'
        data = {
            "add": [
                "uid=bjensen,ou=People,dc=umich,dc=edu",
                "uid=vkg,ou=People,dc=umich,dc=edu"
            ],
            "delete": [
                "uid=hable,ou=People,dc=umich,dc=edu"
            ]}
        r = requests.post(url=url, json=data)
        return json.dumps(r.json(), indent=4)

def main():
    pass


if __name__ == "__main__":
    main()
