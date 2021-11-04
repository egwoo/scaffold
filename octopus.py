import credentials
import argparse
from utilities import camel_to_spaces
import logging
import requests

from octopus_client import OctopusClient
import octopus_service_config


parser = argparse.ArgumentParser(description='Add a service to Octopus')
parser.add_argument('--solution_name', help="Name of your C# Solution - expected to by Pascal Case. e.g., 'MyPlatformService'", required=True)
parser.add_argument('--space', help="Name of the space to add your service to. Defaults to 'Default'", default='Default')


logging.basicConfig(
    format="%(levelname)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

def add_service_to_octopus(solution_name, space_name):
    kebab_case_solution_name = solution_name.replace(' ', '-').lower()
    try:
        octopus = OctopusClient(credentials.octopus_url, credentials.octopus_apikey)
        space = octopus.find_space(space_name)
        space_id = space['Id']
        logger.info(f"Connecting to Octopus on: {octopus.base_api_url} in Space: {space_name} SpaceID: {space_id}")
        
        library_variable_set = octopus.create_library_variable_set(space_id, solution_name)
        octopus.set_variable_set_variables(space_id, library_variable_set['VariableSetId'], octopus_service_config.variables)
        logger.info(f"Library Variable Set created: {library_variable_set['Id']} successfully")
        
        project_group = octopus.create_project_group(space_id, solution_name)
        logger.info(f"Project Group created: {project_group['Id']} successfully")

        kebab_case_api_project_name = f'{kebab_case_solution_name}-api'
        lifecycle = octopus.find_lifecycle('Stage-Production')
        project = octopus.create_project(space_id, kebab_case_api_project_name, '', project_group['Id'], lifecycle['Id'])
        octopus.set_deployment_process_steps(space_id, project['DeploymentProcessId'], octopus_service_config.steps(kebab_case_api_project_name))
        for name in octopus_service_config.library_variable_set_names:
            id = octopus.find_library_variable_set(space_id, name)['Id']
            project['IncludedLibraryVariableSetIds'].append(id)
        project['IncludedLibraryVariableSetIds'].append(library_variable_set['Id'])
        octopus.update_project(space_id, project)

        logger.info(f"Project created: {kebab_case_api_project_name} Id: {project['Id']} successfully")

        default_channel = next(iter(octopus.get_project_channels(project['Id'])),None)

        intg_lifecycle = octopus.find_lifecycle('Integration')
        octopus.create_channel(space_id, project['Id'], intg_lifecycle['Id'], kebab_case_api_project_name, 'Integration', 'intg', True)
        octopus.create_channel(space_id, project['Id'], lifecycle['Id'], kebab_case_api_project_name, 'Production', '$^', False)
        octopus.delete_channel(default_channel['SpaceId'], default_channel['ProjectId'], default_channel['Id'])
        logger.info(f"Channels created successfully")
        logger.info(f"'{solution_name}' | {kebab_case_solution_name} added to Octopus successfully")

    except requests.exceptions.HTTPError as err:
        logger.error(err, err.response.text)
        raise


if __name__ == "__main__":
    args = parser.parse_args()
    solution_name_with_spaces = camel_to_spaces(args.solution_name)
    add_service_to_octopus(solution_name_with_spaces, args.space)
