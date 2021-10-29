import json
import requests

class OctopusClient:
    def __init__(self, base_url, api_key):
        # Define Octopus server variables
        self.base_api_url = '{}/api'.format(base_url)
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
        uri = '{}/spaces'.format(self.base_api_url)
        space = self._get_by_name(uri, name)
        return space
    
    def create_library_variable_set(self, space_id, name):
        library_set = {
            'SpaceId': space_id,
            'Name': name,
            }

        uri = '{0}/libraryvariablesets'.format(self.base_api_url)
        response = requests.post(uri, headers=self.headers, json=library_set)
        response.raise_for_status()
        library_variable_set = json.loads(response.text)
        return library_variable_set
    
    def set_variable_set_variables(self, space_id, variable_set_id, variables):
        uri = '{0}/{1}/variables/{2}'.format(self.base_api_url, space_id, variable_set_id)
        library_variable_set = self._get_octopus_resource(uri)

        library_variable_set['Variables'] = variables
        response = requests.put(uri, headers=self.headers, json=library_variable_set)
        response.raise_for_status()

    def create_project_group(self, space_id, name):
        project_group = {
            'SpaceId': space_id,
            'Name': name,
            }

        uri = '{0}/projectgroups'.format(self.base_api_url)
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

        uri = '{0}/{1}/projects'.format(self.base_api_url, space_id)
        response = requests.post(uri, headers=self.headers, json=project)
        response.raise_for_status()
        return json.loads(response.text)

    def find_project_group(self, name):
        uri = '{}/projectgroups'.format(self.base_api_url)
        return self._get_by_name(uri, name)
    
    def find_lifecycle(self, name):
        uri = '{}/lifecycles'.format(self.base_api_url)
        return self._get_by_name(uri, name)

    def get_deployment_process(self, space_id, deployment_process_id):
        uri = '{0}/{1}/deploymentprocesses/{2}'.format(self.base_api_url, space_id, deployment_process_id)
        return self._get_octopus_resource(uri)

    def set_deployment_process_steps(self, space_id, deployment_process_id, steps):
        uri = '{0}/{1}/deploymentprocesses/{2}'.format(self.base_api_url, space_id, deployment_process_id)
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
                            'DeploymentAction': 'EKS Install Package {} webservice'.format(project_code),
                            'PackageReference': ''
                        }
                    ],
                }
            ]
        }

        uri = '{0}/{1}/channels'.format(self.base_api_url, space_id)
        response = requests.post(uri, headers=self.headers, json=channel)
        response.raise_for_status()

    def get_project_channels(self, project_id):
        uri = '{0}/projects/{1}/channels'.format(self.base_api_url, project_id)
        return self._get_octopus_resource(uri)

    def delete_channel(self, space_id, project_id, channel_id):
        uri = '{0}/{1}/projects/{2}/channels/{3}'.format(self.base_api_url, space_id, project_id, channel_id)
        headers = self.headers.copy()
        headers['x-http-method-override'] = 'DELETE'
        response = requests.post(uri, headers=headers)
        response.raise_for_status()
