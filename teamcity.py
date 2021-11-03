import credentials
import json
import logging
import requests

import teamcity_service_config


logging.basicConfig(
    format="%(levelname)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

class TeamCityClient:
    def __init__(self, base_url, username, password):
        self.base_url = f'{base_url}/app/rest'
        self.auth = (username, password)
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            }

    def create_project(self, name):
        payload = {
            'name': name,
            'parentProject': {
                'locator': 'id:Services'
            }
        }
        response = requests.post(f'{self.base_url}/projects', auth=self.auth, headers=self.headers, json=payload)
        response.raise_for_status()
        return json.loads(response.text)

    def create_build_type(self, name, project_id, template_build_type_id, project_path):
        payload = {
                'name': name,
                'projectId': project_id,
                'templates': {
                    'buildType':
                    [
                        {
                        'id': template_build_type_id
                        }
                    ]
                },
                'parameters': {
                    'property': [
                        {
                            'name': 'HelmPackageName',
                            'value': name
                        },
                        {
                            'name': 'OctopusProjectName',
                            'value': name
                        },
                        {
                            'name': 'system.ProjPath',
                            'value': project_path
                        },
                    ]
                }
            }

        response = requests.post(f'{self.base_url}/buildTypes', auth=self.auth, headers=self.headers, json=payload)
        response.raise_for_status()
        return json.loads(response.text)
    
    def detach_buildtype_from_templates(self, build_type_id):
        requests.delete(f'{tc.base_url}/buildTypes/{build_type_id}/templates?inlineSettings=true', auth=tc.auth, headers=tc.headers)

try:
    projPathIdunno = 'Services/1234'
    project_name = 'Edwin Test Service'
    project_code = 'edwin-test-service'

    tc = TeamCityClient(credentials.teamcity_url, credentials.teamcity_username, credentials.teamcity_password)
    project = tc.create_project(project_name)
    build_type = tc.create_build_type(project_code, project['id'], teamcity_service_config.template_build_type_id, projPathIdunno)
    tc.detach_buildtype_from_templates(build_type['id'])

except requests.exceptions.HTTPError as err:
    logger.error(err, err.response.text)
    raise
