import credentials
from dohq_teamcity import TeamCity, ApiException, NewProjectDescription
from pprint import pprint


class TeamCityClient:
    def __init__(self, base_url, username, password):
        self.tc = TeamCity(base_url, auth=(username, password))
        self.tc.default_headers["Origin"] = credentials.teamcity_url

    def create_new_project_from_existing(self):
        body = NewProjectDescription(copy_all_associated_settings=True) # NewProjectDescription |  (optional)
        body.name = 'Edwin Test'
        body.source_project_locator = 'id:Services_DeliveryOptionsService'
        try:
            api_response = self.tc.project_api.create_project(body=body)
        except ApiException as e:
            print("Exception when calling ProjectApi->create_project: %s\n" % e)
