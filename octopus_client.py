import json
import requests

class OctopusClient:
    def __init__(self, base_url, api_key):
        # Define Octopus server variables
        self.base_api_url = f'{base_url}/api'
        self.headers = {'X-Octopus-ApiKey': api_key}

    def _get_octopus_resource(self, uri, skip_count = 0):
        items = []
        skip_querystring = ""

        if '?' in uri:
            skip_querystring = '&skip='
        else:
            skip_querystring = '?skip='

        response = requests.get((uri + skip_querystring + str(skip_count)), headers=self.headers)
        response.raise_for_status()

        # Get results of API call
        results = json.loads(response.content.decode('utf-8'))

        # Store results
        if isinstance(results, list):
            return results
        elif 'Items' in results.keys():
            items += results['Items']

            # Check to see if there are more results
            if (len(results['Items']) > 0) and (len(results['Items']) == results['ItemsPerPage']):
                skip_count += results['ItemsPerPage']
                items += self._get_octopus_resource(uri, skip_count)

        else:
            return results

        return items
    
    def _get_by_name(self, uri, name):
        resources = self._get_octopus_resource(uri)
        return next((x for x in resources if x['Name'] == name), None)

    def find_space(self, name):
        uri = f'{self.base_api_url}/spaces'
        space = self._get_by_name(uri, name)
        return space
    
    def create_library_variable_set(self, space_id, name):
        library_set = {
            'SpaceId': space_id,
            'Name': name,
            }

        uri = f'{self.base_api_url}/libraryvariablesets'
        response = requests.post(uri, headers=self.headers, json=library_set)
        response.raise_for_status()
        library_variable_set = json.loads(response.text)
        return library_variable_set
    
    def set_variable_set_variables(self, space_id, variable_set_id, variables):
        uri = f'{self.base_api_url}/{space_id}/variables/{variable_set_id}'
        library_variable_set = self._get_octopus_resource(uri)

        library_variable_set['Variables'] = variables
        response = requests.put(uri, headers=self.headers, json=library_variable_set)
        response.raise_for_status()

    def create_project_group(self, space_id, name):
        project_group = {
            'SpaceId': space_id,
            'Name': name,
            }

        uri = f'{self.base_api_url}/projectgroups'
        response = requests.post(uri, headers=self.headers, json=project_group)
        response.raise_for_status()
        project_group = json.loads(response.text)
        return project_group

    def create_project(self, space_id, name, description, project_group_id, lifecycle_id):
        project = {
            'Name': name,
            'Description': description,
            'ProjectGroupId': project_group_id,
            'LifeCycleId': lifecycle_id
        }

        uri = f'{self.base_api_url}/{space_id}/projects'
        response = requests.post(uri, headers=self.headers, json=project)
        response.raise_for_status()
        return json.loads(response.text)

    def update_project(self, space_id, project):
        uri = f'{self.base_api_url}/{space_id}/projects/{project["Id"]}'
        response = requests.put(uri, headers=self.headers, json=project)
        response.raise_for_status


    def find_project_group(self, name):
        uri = f'{self.base_api_url}/projectgroups'
        return self._get_by_name(uri, name)
    
    def find_lifecycle(self, name):
        uri = f'{self.base_api_url}/lifecycles'
        return self._get_by_name(uri, name)

    def get_deployment_process(self, space_id, deployment_process_id):
        uri = f'{self.base_api_url}/{space_id}/deploymentprocesses/{deployment_process_id}'
        return self._get_octopus_resource(uri)

    def set_deployment_process_steps(self, space_id, deployment_process_id, steps):
        uri = f'{self.base_api_url}/{space_id}/deploymentprocesses/{deployment_process_id}'
        deployment_process = self._get_octopus_resource(uri)

        deployment_process['Steps'] = steps
        response = requests.put(uri, headers=self.headers, json=deployment_process)
        response.raise_for_status()

    def create_channel(self, space_id, project_id, lifecycle_id, project_code, name, is_default):
        channel = {
            'ProjectId': project_id,
            'Name': name,
            'SpaceId': space_id,
            'IsDefault': is_default,
            'LifeCycleId': lifecycle_id,
            'Rules': [
                {
                    'Tag': '$^',
                    'ActionPackages': [
                        {
                            'DeploymentAction': f'EKS Install Package {project_code} webservice',
                            'PackageReference': ''
                        }
                    ],
                }
            ]
        }

        uri = f'{self.base_api_url}/{space_id}/channels'
        response = requests.post(uri, headers=self.headers, json=channel)
        response.raise_for_status()

    def get_project_channels(self, project_id):
        uri = f'{self.base_api_url}/projects/{project_id}/channels'
        return self._get_octopus_resource(uri)

    def delete_channel(self, space_id, project_id, channel_id):
        uri = f'{self.base_api_url}/{space_id}/projects/{project_id}/channels/{channel_id}'
        headers = self.headers.copy()
        headers['x-http-method-override'] = 'DELETE'
        response = requests.post(uri, headers=headers)
        response.raise_for_status()

    def find_library_variable_set(self, space_id, name):
        uri = f'{self.base_api_url}/{space_id}/libraryvariablesets'
        return self._get_by_name(uri, name)
