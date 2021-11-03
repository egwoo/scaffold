import credentials
import argparse
import logging

from octopus_client import OctopusClient
import octopus_service_config


parser = argparse.ArgumentParser(description='Add a service to Octopus')
parser.add_argument('--name', help="Name of your service. Enclose in quotes if you have spaces. e.g., 'My Platform Service'", required=True)
parser.add_argument('--space', help="Name of the space to add your service to. Defaults to 'Default'", default='Default')


logging.basicConfig(
    format="%(levelname)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

def add_service_to_octopus(service_name, space_name):
    service_code = service_name.replace(' ', '-').lower()
    try:
        octopus = OctopusClient(credentials.octopus_url, credentials.octopus_apikey)
        space = octopus.find_space(space_name)
        space_id = space['Id']
        logger.info(f"Starting Octopus Process on: {octopus.base_api_url} in Space: {space_name} SpaceID: {space_id}")
        
        library_variable_set = octopus.create_library_variable_set(space_id, service_name)
        octopus.set_variable_set_variables(space_id, library_variable_set['VariableSetId'], octopus_service_config.variables)
        logger.info(f"Library Variable Set created: {library_variable_set['Id']} successfully")
        
        project_group = octopus.create_project_group(space_id, service_name)
        logger.info(f"Project Group created: {project_group['Id']} successfully")

        api_project_code = f'{service_code}-api'
        lifecycle = octopus.find_lifecycle('Stage-Production')
        project = octopus.create_project(space_id, api_project_code, '', project_group['Id'], lifecycle['Id'])
        octopus.set_deployment_process_steps(space_id, project['DeploymentProcessId'], octopus_service_config.steps(api_project_code))
        logger.info(f"Project created: {api_project_code} Id: {project['Id']} successfully")

        default_channel = next(iter(octopus.get_project_channels(project['Id'])),None)

        api_lifecycle = octopus.find_lifecycle('Integration')
        octopus.create_channel(space_id, project['Id'], api_lifecycle['Id'], api_project_code, 'Integration', True)
        octopus.create_channel(space_id, project['Id'], lifecycle['Id'], api_project_code, 'Production', False)
        octopus.delete_channel(default_channel['SpaceId'], default_channel['ProjectId'], default_channel['Id'])
        logger.info(f"Channels created successfully")
        logger.info(f"'{service_name}' | {service_code} added to Octopus successfully")

    except requests.exceptions.HTTPError as err:
        logger.error(err, err.response.text)
        raise


if __name__ == "__main__":
    args = parser.parse_args()
    add_service_to_octopus(args.name, args.space)
