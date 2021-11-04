import credentials
import argparse
import requests
import logging
from utilities import camel_to_kebab, camel_to_spaces
from sentry_client import SentryClient
import sentry_service_config


parser = argparse.ArgumentParser(description='Add a service to Sentry')
parser.add_argument('--solution_name', help="Name of your C# Solution - expected to by Pascal Case. e.g., 'MyPlatformService'", required=True)


logging.basicConfig(
    format="%(levelname)s: %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

def add_service_to_sentry(solution_name):
    solution_name_with_spaces = camel_to_spaces(solution_name)
    project_slug = camel_to_kebab(solution_name)
    try:
        sentry = SentryClient(sentry_service_config.organization_slug, credentials.sentry_token)
        project = sentry.create_project(sentry_service_config.team_slug, project_slug, solution_name_with_spaces)
        project_keys = sentry.get_client_keys(project['slug'])
        sentry_dsn = project_keys[0]['dsn']['public']
        return sentry_dsn
    except requests.exceptions.HTTPError as err:
        logger.error(err, err.response.text)
        raise

if __name__ == "__main__":
    args = parser.parse_args()
    print(add_service_to_sentry(args.solution_name))
