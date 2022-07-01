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
        """
        Get the authorization header needed for the app ID defined in a separate config file.
        Note that the authorization header should look like {"Authorize": "Bearer {access_token}"}.
        :return: The authorization header as a Python dictionary
        """
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

    def get_people(self):
        """
        Sends a GET request to /people/. This fetches a list of a few people.
        :return: a list of people. Each person is represented by a dictionary of attributes and values.
        """
        url = f'{self.base_url}/'
        r = requests.get(url=url)
        return r.json()

    def search(self):
        """
        Sends a POST request to /people/search/. This searches the directory according to criteria in the POST body.
        See the body for an example of search criteria.
        :return: a list of people matching the criteria.
                 Each person is represented by a dictionary of attributes and values.
        """
        url = f'{self.base_url}/search/'

        # searchType_options = ["start", "end", "contain", "exact"]'
        searchParts = [{"attribute": "ou",
                        "value": "Student",
                        "searchType": "contain"},
                       {"attribute": "givenName",
                        "value": "John",
                        "searchType": "start"}]

        attributes = ["displayName"]

        body = {"searchParts": searchParts,
                "numEntries": 3,
                "logicalOperator": "AND",  # AND or OR
                "attributes": attributes}

        r = requests.post(url=url, json=body)
        return r.json()

    def get_uniqname_details(self):
        """
        Sends a GET request to /people/<uniqname>/. This gets the details for <uniqname>.
        :return: A dictionary of attributes for <uniqname>
        """
        url = f'{self.base_url}/{self.uniqname}/'
        r = requests.get(url=url)
        return r.json()

    def get_uniqname_vcard(self):
        """
        Requires authorization.
        Sends a GET request to /people/<uniqname>/vcard/. This gets the vCard for <uniqname>, or 404 if unavailable.
        :return: A dictionary containing vCard information for <uniqname>
        """
        url = f'{self.base_url}/{self.uniqname}/vcard/'
        auth_header = Authorize.get_auth_header()
        r = requests.get(url=url, headers=auth_header)
        return r.json()

    # GET /people/<uniqname>/name_coach/
    def get_uniqname_name_coach(self):
        """
        Sends a GET request to /people/<uniqname>/name_coach/.
        This gets the name coach information for <uniqname>, or 404 if unavailable.
        :return: A dictionary containing name coach information for <uniqname>
        """
        url = f'{self.base_url}/{self.uniqname}/name_coach/'
        r = requests.get(url=url)
        return r.json()


class Groups:
    base_url = f'{api_url}/groups'
    group_name = 'api-examples-group'

    def get_group_details(self):
        """
        Sends a GET request to /groups/<groupname>/. This gets the details for the group <groupname>.
        :return: A dictionary of attributes for <groupname>
        """
        url = f'{self.base_url}/{self.group_name}/'
        auth_header = Authorize.get_auth_header()
        r = requests.get(url=url, headers=auth_header)
        return r.json()

    def renew_group(self):
        """
        Sends a POST request to /groups/<groupname>/renew/.
        This extends its expiration date to a year from today's date. It also un-expires the group if it is expired.
        :return: None. The response is empty.
        """
        url = f'{self.base_url}/{self.group_name}/renew/'
        auth_header = Authorize.get_auth_header()
        r = requests.post(url=url, headers=auth_header)
        assert (r.status_code == 200)
        return None

    def expire_group(self):
        """
        NOT CURRENTLY IMPLEMENTED # TODO: update this when released
        Sends a POST request to /groups/<groupname>/expire/.
        This expires ("soft deletes") a group. This is equivalent to trashing a group in the MCommunity web app.
        The amount of days until permanent deletion can be specified in the post body. See below for example.
        :return: None. The response is empty.
        """
        url = f'{self.base_url}/{self.group_name}/expire/'
        auth_header = Authorize.get_auth_header()
        r = requests.post(url=url, headers=auth_header,
                          json={"days": 7})  # Number of days until permanent deletion
        assert (r.status_code == 200)
        return None

    def create_group(self):
        """
        Sends a POST request to /groups/.
        This creates a new group with details specified in the POST body. See below for example.
        See documentation for full details on group attributes.
        Note that the group name must not already exist. If it does exist, a 409 will be returned.
        :return: None. The response is empty.
        """
        url = f'{self.base_url}/'
        auth_header = Authorize.get_auth_header()

        # These attributes are required; all others are optional
        body = {
            "cn": self.group_name,              # If this group cn already exists, a 409 will be returned
            "umichGroupEmail": "this-is-fake",  # do not include @umich.edu. Also will return 409 if email exists
            "owner": [  # TODO: Currently, app ids can't be the initial owner. Do we want to change this?
                'uid=frnkwang,ou=people,dc=umich,dc=edu'
            ],
            "umichDescription": "My description"
        }

        r = requests.post(url=url, headers=auth_header, json=body)
        assert(r.status_code == 201)
        return None

    def delete_group(self):
        """
        Sends a DELETE request to /groups/<groupname>/.
        This deletes <groupname> PERMANENTLY. The app id must be an owner to delete the group.
        :return: None. The response is empty.
        """
        url = f'{self.base_url}/{self.group_name}/'
        auth_header = Authorize.get_auth_header()
        r = requests.delete(url=url, headers=auth_header)
        assert (r.status_code == 204)
        return None

    def replace_attributes(self):
        """
        Sends a PATCH request to /groups/<groupname>/.
        This replaces the group's attributes with values in the PATCH body. The app id must be an owner.
        Attributes can be removed by replacing it with a null value.
        To modify multi-value attributes, use the multi-valued attribute endpoint instead.
        :return: None. The response is empty.
        """
        url = f'{self.base_url}/{self.group_name}/'
        auth_header = Authorize.get_auth_header()

        body = {
            "umichDescription": "This is a new description",
            "umichAutoReply": None,
        }

        r = requests.patch(url=url, headers=auth_header, json=body)
        assert(r.status_code == 200)
        return None

    def add_remove_multi_valued_attributes(self):
        """
        Sends a POST request to /groups/<groupname>/<attribute>/.
        This will add or remove values from <attribute> in <groupname> according to the request body.
        :return: None. The response is empty.
        """
        attribute = "owner"
        url = f'{self.base_url}/{self.group_name}/{attribute}/'

        body = {
            "add": [
                "uid=ethierba,ou=People,dc=umich,dc=edu"
            ],
            "delete": [
                "uid=frnkwang,ou=People,dc=umich,dc=edu"
            ],
        }

        auth_header = Authorize.get_auth_header()
        r = requests.post(url=url, headers=auth_header, json=body)
        assert(r.status_code == 200)
        return None

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
