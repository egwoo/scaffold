import credentials
import argparse
from utilities import camel_to_kebab, camel_to_spaces
import logging
import requests

from teamcity_client import TeamCityClient
import teamcity_service_config
from sentry_client import SentryClient
import sentry_service_config
from octopus_client import OctopusClient
import octopus_service_config


parser = argparse.ArgumentParser(description='Add a C# platform service to TeamCity')
parser.add_argument('--solution_name', help="Name of your C# Solution - expected to by Pascal Case. e.g., 'MyPlatformService'", required=True)
parser.add_argument('--octopus_space', help="Name of the Octopus space to add your service to. Defaults to 'Default'", default='Default')


logging.basicConfig(
    format="%(levelname)s: %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


def add_service_to_teamcity(solution_name):
    solution_name_with_spaces = camel_to_spaces(solution_name)
    api_project_name = f'{solution_name}.API'
    api_project_path = f'Services/{solution_name}/src/{api_project_name}'
    kebab_case_api_project_name = camel_to_kebab(api_project_name)
    logger.info(f"{solution_name} | {solution_name_with_spaces} | {api_project_name} | {api_project_path} | {kebab_case_api_project_name}")

    logger.info(f"Connecting to {credentials.teamcity_url}")
    tc = TeamCityClient(credentials.teamcity_url, credentials.teamcity_username, credentials.teamcity_password)
    project = tc.create_project(solution_name_with_spaces)
    logger.info(f"Project {project['id']} successfully created")
    build_type = tc.create_build_type(kebab_case_api_project_name, project['id'], teamcity_service_config.template_build_type_id, api_project_path)
    logger.info(f"Build Type {build_type['id']} successfully created")
    tc.detach_buildtype_from_templates(build_type['id'])
    logger.info(f"{solution_name_with_spaces} successfully created")
    #tc.create_build('Services_ConnectionManager_CmWebApi', 'refs/heads/connection-manager-ci-cd')

def add_service_to_sentry(solution_name):
    solution_name_with_spaces = camel_to_spaces(solution_name)
    project_slug = camel_to_kebab(solution_name)

    sentry = SentryClient(sentry_service_config.organization_slug, credentials.sentry_token)
    project = sentry.create_project(sentry_service_config.team_slug, project_slug, solution_name_with_spaces)
    project_keys = sentry.get_client_keys(project['slug'])
    sentry_dsn = project_keys[0]['dsn']['public']
    return sentry_dsn

def add_service_to_octopus(solution_name, space_name, sentry_dsn):
    solution_name_with_spaces = camel_to_spaces(args.solution_name)
    kebab_case_solution_name = solution_name_with_spaces.replace(' ', '-').lower()

    octopus = OctopusClient(credentials.octopus_url, credentials.octopus_apikey)
    space = octopus.find_space(space_name)
    space_id = space['Id']
    logger.info(f"Connecting to Octopus on: {octopus.base_api_url} in Space: {space_name} SpaceID: {space_id}")
    
    library_variable_set = octopus.create_library_variable_set(space_id, solution_name_with_spaces)
    octopus.set_variable_set_variables(space_id, library_variable_set['VariableSetId'], octopus_service_config.variables)
    logger.info(f"Library Variable Set created: {library_variable_set['Id']} successfully")
    
    project_group = octopus.create_project_group(space_id, solution_name_with_spaces)
    logger.info(f"Project Group created: {project_group['Id']} successfully")

    kebab_case_api_project_name = f'{kebab_case_solution_name}-api'
    lifecycle = octopus.find_lifecycle('Stage-Production')
    project = octopus.create_project(space_id, kebab_case_api_project_name, '', project_group['Id'], lifecycle['Id'])
    octopus.set_deployment_process_steps(space_id, project['DeploymentProcessId'], octopus_service_config.steps(kebab_case_api_project_name, sentry_dsn))
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
    logger.info(f"'{solution_name}' | {solution_name_with_spaces} | {kebab_case_solution_name} added to Octopus successfully")


if __name__ == "__main__":
    try:
        args = parser.parse_args()
        add_service_to_teamcity(args.solution_name)
        sentry_dsn = add_service_to_sentry(args.solution_name)
        add_service_to_octopus(args.solution_name, args.octopus_space, sentry_dsn)
    except requests.exceptions.HTTPError as err:
        logger.error(err, err.response.text)
        raise
