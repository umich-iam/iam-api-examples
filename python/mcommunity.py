import json
import requests

api_url = 'https://mcommunity-api-dev.dsc.umich.edu'  # TODO: update as needed


class People:
    base_url = api_url + '/people'
    uniqname = 'frnkwang'  # TODO: Will this need to be changed?

    def get_people(self):
        url = self.base_url + '/'
        r = requests.get(url=url)
        return json.dumps(r.json(), indent=4)


def main():
    pass


if __name__ == "__main__":
    main()