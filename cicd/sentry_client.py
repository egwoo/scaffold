import json
import requests


class SentryClient:
    def __init__(self, organization_slug, auth_token):
        self.base_url = 'https://sentry.io'
        self.base_api_url = f'{self.base_url}/api/0'
        self.organization_slug = organization_slug
        self.auth_token = auth_token
        self.headers = {
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json',
            }
    
    def create_project(self, team_slug, project_slug, project_name):
        payload = {
            'name': project_name,
            'slug': project_slug,
            }
        
        uri = f'{self.base_api_url}/teams/{self.organization_slug}/{team_slug}/projects/'
        response = requests.post(uri, headers=self.headers, json=payload)
        response.raise_for_status()
        return json.loads(response.text)
    
    def get_client_keys(self, project_slug):
        uri = f'{self.base_api_url}/projects/{self.organization_slug}/{project_slug}/keys/'
        response = requests.get(uri, headers=self.headers)
        response.raise_for_status()
        return json.loads(response.text)
