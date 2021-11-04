import credentials
import argparse
import logging
import re
import requests

from teamcity_client import TeamCityClient
import teamcity_service_config


parser = argparse.ArgumentParser(description='Add a C# platform service to TeamCity')
parser.add_argument('--solution_name', help="Name of your C# Solution - expected to by Pascal Case. e.g., 'MyPlatformService'", required=True)


logging.basicConfig(
    format="%(levelname)s: %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

def camel_to_kebab(name):
  name = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
  name = re.sub('([a-z0-9])([A-Z])', r'\1-\2', name).lower()
  name = re.sub('\.', '-', name)
  return name

def add_service_to_teamcity(solution_name):
    try:
        solution_name_with_spaces = re.sub(r'(?<!^)(?=[A-Z])', ' ', solution_name)
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

    except requests.exceptions.HTTPError as err:
        logger.error(err, err.response.text)
        raise

if __name__ == "__main__":
    args = parser.parse_args()
    add_service_to_teamcity(args.solution_name)
