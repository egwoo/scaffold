import json
import requests

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
        requests.delete(f'{self.base_url}/buildTypes/{build_type_id}/templates?inlineSettings=true', auth=self.auth, headers=self.headers)
        
    def create_build(self, build_conf_id, branch):
        payload = {
                'branchName': branch,
                'buildType': {
                    'id': build_conf_id
                }
            }
        
        response = requests.post(f'{self.base_url}/buildQueue', auth=self.auth, headers=self.headers, json=payload)
        response.raise_for_status()
        return json.loads(response.text)
