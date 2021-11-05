# Overview
This set of scripts should allow you to scaffold a .NET C# Core Platform Service with one command and deploy a dev Hello World instance in minutes.

This is a highly opinionated script that relies on the following conventions:
* Your Solution is in the [Services folder of the ShipStation Repo](https://github.com/shipstation/shipstation/tree/master/Services)
* Your Solution Name is in Pascal Case
    * Your API Project will be {Solution Name}.API
* Project Names created in the various systems follow prior precedents which is a mix of Pascal Case, Kebab Case, and Title Case.

This set of scripts will create the following:
* .NET Code C# API Solution
* TeamCity Project
* Sentry Project
* Octopus Project, Variable Sets, and Channels

## Usage
Copy `cicd/credentials_example.py` to `cicd/credentials.py` and populate the appropriate values.

For now, invoke this script in Docker.
The C# Solution will be created wherever you specify `{PATH_TO_C#_SERVICE}`
`{SERVICE_NAME}` should be in Pascal Case and will be the name of the created solution.
```
docker build . -t scaffold
docker run -v {PATH_TO_C#_SERVICE}:/target scaffold {SERVICE_NAME}
```
e.g.
```
docker run -v ~/source/shipstation/shipstation/Services:/target scaffold MyPlatformService
```

## As of 11/5, if you need to clean up CI/CD artifacts from testing, here are the current items to clean up:
* Octopus
    * Project
    * Project Group
    * Library - Variable Sets
    * Library - Packages
* Sentry - Project
* TeamCity - Project
* EKS - ???

## TODO
### dotnet
* Ensure bash script is run in a .Net Core 3.1 context

* Need to add dependency between Class Library and API Project
* Need to add healthcheck and repoint healthcheck in `dotnet/template/api/infra/helm-values/values.common.yaml.template`

### cicd
* Some code reorganization is probably a good idea. Rethink `*_service_config.py` pattern.
* Introduce dotenv and refactor `credentials.py`. This could be in conjunction with rethinking `*_service_config.py` pattern.
* `octopus.py` seems like it could be cleaned up.
    * `get_steps` and `get_variables` are weird.
    * Injecting `intg` and `$^` as prerelease tags feels bad man.

### Other
* Add support for Dynamo and Postgres
* Automatically create a solution in a GitHub branch, build and deploy to intg and provide a link to the new service?
