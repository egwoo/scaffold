import credentials
import json
import requests
from pprint import pprint


class TeamCityClient:
    def __init__(self, base_url, username, password):
        self.base_api_url = '{}/api'.format(base_url)
        self.auth = (username, password)
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            }

base_url = 'http://build.shipstation.com/app/rest'

response = requests.get(f'{base_url}/projects', auth=(credentials.teamcity_username, credentials.teamcity_password), headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
projects = json.loads(response.text)
