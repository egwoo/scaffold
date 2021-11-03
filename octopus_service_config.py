import credentials

def steps(project_code):
    return [
        {
        "Name": "Health Check",
        "PackageRequirement": "LetOctopusDecide",
        "Properties": {
            "Octopus.Action.TargetRoles": "kubernetes-eks"
        },
        "Condition": "Success",
        "StartTrigger": "StartAfterPrevious",
        "Actions": [
            {
            "Name": "Health Check",
            "ActionType": "Octopus.HealthCheck",
            "Environments": [],
            "Channels": [],
            "TenantTags": [],
            "Packages": [],
            "Condition": "Success",
            "Properties": {
                "Octopus.Action.HealthCheck.Type": "FullHealthCheck",
                "Octopus.Action.HealthCheck.ErrorHandling": "TreatExceptionsAsErrors",
                "Octopus.Action.HealthCheck.IncludeMachinesInDeployment": "DoNotAlterMachines"
            },
            }
        ]
        },
        {
        "Name": f"EKS Install Package {project_code} webservice",
        "PackageRequirement": "LetOctopusDecide",
        "Properties": {
            "Octopus.Action.TargetRoles": "kubernetes-eks"
        },
        "Condition": "Success",
        "StartTrigger": "StartAfterPrevious",
        "Actions": [
            {
            "Name": f"EKS Install Package {project_code} webservice",
            "ActionType": "Octopus.HelmChartUpgrade",
            "Environments": [],
            "Channels": [],
            "TenantTags": [],
            "Packages": [
                {
                "Name": "",
                "PackageId": "shipkube-webservice",
                "FeedId": "feeds-shipchart",
                "AcquisitionLocation": "Server",
                "Properties": {
                    "SelectionMode": "immediate"
                }
                },
                {
                "Name": "ValuesPack-2",
                "PackageId": f"{project_code}",
                "FeedId": "feeds-builtin",
                "AcquisitionLocation": "ExecutionTarget",
                "Properties": {
                    "ValuesFilePath": "values.common.yaml"
                }
                },
                {
                "Name": "ValuesPack-3",
                "PackageId": f"{project_code}",
                "FeedId": "feeds-builtin",
                "AcquisitionLocation": "ExecutionTarget",
                "Properties": {
                    "ValuesFilePath": "values.#{{HELM_ENVIRONMENT}}.yaml"
                }
                }
            ],
            "Condition": "Success",
            "Properties": {
                "Octopus.Action.Helm.ResetValues": "True",
                "Octopus.Action.Helm.ClientVersion": "V3",
                "Octopus.Action.Helm.ReleaseName": f"{project_code}-#{{HELM_ENVIRONMENT}}",
                "Octopus.Action.Helm.Namespace": f"{project_code}-#{{HELM_ENVIRONMENT}}",
                "Octopus.Action.Helm.AdditionalArgs": "--wait --create-namespace  --atomic --timeout 600s",
                "Octopus.Action.Helm.CustomHelmExecutable": "d:\\tools\\helm\\3.2.4\\helm.exe",
                "Octopus.Action.Package.PackageId": "shipkube-webservice",
                "Octopus.Action.Package.FeedId": "feeds-shipchart",
                "Octopus.Action.Package.DownloadOnTentacle": "False",
                "Octopus.Action.Helm.KeyValues": "{\"image.tag\":\"#{Octopus.Release.Number}\"}"
            },
            }
        ]
        },
        {
        "Name": "SentryMark",
        "PackageRequirement": "LetOctopusDecide",
        "Properties": {},
        "Condition": "Success",
        "StartTrigger": "StartAfterPrevious",
        "Actions": [
            {
            "Name": "SentryMark",
            "ActionType": "Octopus.Script",
            "WorkerPoolId": "WorkerPools-21",
            "Environments": [
                "Environments-41",
                "Environments-1",
                "Environments-21"
            ],
            "Channels": [],
            "TenantTags": [],
            "Packages": [],
            "Condition": "Success",
            "Properties": {
                "Octopus.Action.Script.ScriptSource": "Inline",
                "Octopus.Action.Script.Syntax": "Bash",
                "Octopus.Action.Script.ScriptBody": "#!/bin/bash\n\n# FUNCTIONS\nfunction create_deployment {\n  sentry-cli releases deploys \"$1\" new -e \"$2\" -n \"$3\"\n}\nfunction create_release {\n    sentry-cli releases new \"$1\"\n    sentry-cli releases set-commits \"$1\" --commit \"$2/$3\"\n    sentry-cli releases finalize \"$1\"\n}\n\n# MAIN\nechoerror() { echo \"$@\" 1>&2; }\necho \"SentryMarkOctopusStepTemplate.sh - START\"\n# GitHub: deployments/octopus/scripts/sentry/SentryMarkOctopusStepTemplate.sh. \n# Provides Sentry support for apps deployed by Octopus. See https://shipstation.atlassian.net/wiki/x/GIAmN\nset -e\nrelease=$(get_octopusvariable \"Octopus.Release.Number\")\ntenant=$(get_octopusvariable \"Octopus.Deployment.Tenant.Name\")\noctoEnv=$(get_octopusvariable \"Octopus.Environment.Name\")\nprojPrefix=$(get_octopusvariable \"SentryProjectPrefix\")\ngithubOrg=$(get_octopusvariable \"GITHUB_ORG\")\n\nif [[ $octoEnv == \"DynDev\" ]]; then\n  echo \"...octoEnv = DynDev, set sentryDeployEnv to: dyndev\"\n  sentryDeployEnv=\"dyndev\"\nelif [[ $octoEnv == \"Dev\" ]]; then\n  echo \"...octoEnv = Dev, set sentryDeployEnv to: dev\"\n  sentryDeployEnv=\"dev\"\nelif [[ $octoEnv == \"Integration\" ]]; then\n  echo \"...octoEnv = Integration, set sentryDeployEnv to: intg\"\n  sentryDeployEnv=\"intg\"\nelif [[ $octoEnv == \"Stage\" ]]; then\n  echo \"...octoEnv = Stage, set sentryDeployEnv to: stage\"\n  sentryDeployEnv=\"stage\"\nelif [[ $octoEnv == \"Production\" ]]; then\n  echo \"...octoEnv = Production, set sentryDeployEnv to: prod\"\n  sentryDeployEnv=\"prod\"\nelse\n  echo \"ERROR - octoEnv value, $octoEnv is invalid, abort...\"\n  exit 1\nfi\n\nif [ -z \"$tenant\" ] ; then\n  echo \"...this is not a tenanted deployment, use sentryDeployEnv for sentryDeploymentTarget\"\n  sentryDeploymentTarget=\"$sentryDeployEnv\"\nelse\n  echo \"...this is a tenanted deployment, use SS-(tenant) for sentryDeploymentTarget\"\n  sentryDeploymentTarget=\"SS-$tenant\"\nfi\n\nif [ -z \"$githubOrg\" ] ; then\n  githubOrg='shipstation'\n  echo \"...GITHUB_ORG octopus variable NOT specified, githubOrg=$githubOrg (default)\"\n  \nelse\n  echo \"...GITHUB_ORG octopus variable specified, githubOrg=$githubOrg\"\nfi\n\nreleaseNotes=$(get_octopusvariable \"Octopus.Release.Notes\")\nindex1=\"https://github.com/$githubOrg/\"\nremainder=${releaseNotes#*$index1}\n# get only the first line of the release notes\nNL='\n'\nremainder=${remainder%%\"$NL\"*}\nindex2=\"/commit/\"\nrepo=${remainder%$index2*}\nrepo=$(echo \"$repo\" | tr '[:upper:]' '[:lower:]')\necho \"    var repo = $repo\"\nremainder2=${remainder#*$index2}\nindex3=\", Configs\"\nsha=${remainder2%$index3*}\necho \"    var sha = $sha\"\nsentryCommit=\"$repo@$sha\"\nSENTRY_PROJECTS=$(get_octopusvariable \"SENTRY_PROJECTS\")\nSENTRY_AUTH_TOKEN=$(get_octopusvariable \"SENTRY_AUTH_TOKEN\")\nSENTRY_ORG=\"shipstation\"\n\necho \"    var release = $release\"\necho \"    var tenant = $tenant\"\necho \"    var octoEnv = $octoEnv\"\necho \"    var sentryDeployEnv = $sentryDeployEnv\"\necho \"    var sentryDeploymentTarget = $sentryDeploymentTarget\"\necho \"    var sentryCommit = $sentryCommit\"\necho \"    var SENTRY_PROJECTS = $SENTRY_PROJECTS\"\necho \"    var projPrefix = $projPrefix\"\n\n: \"${sentryCommit:?Need to set sentryCommit non-empty}\"\n: \"${SENTRY_PROJECTS:?Need to set SENTRY_PROJECTS non-empty}\"\n: \"${SENTRY_AUTH_TOKEN:?Need to set SENTRY_AUTH_TOKEN non-empty}\"\n\nexport SENTRY_PROJECTS\nexport SENTRY_AUTH_TOKEN\nexport SENTRY_ORG\n\nif [ -z \"$projPrefix\" ] ; then\n  echo \"...projPrefix variable value is empty, use SENTRY_PROJECTS for release prefixes\"\n  IFS=','\n  for i in ${SENTRY_PROJECTS}; do\n    sentryReleaseVersion=\"${i}@$release\"\n    echo \"Creating Sentry deployment for Sentry project ${i}, release $sentryReleaseVersion in $sentryDeploymentTarget\"\n    export SENTRY_PROJECT=${i}\n    list=`sentry-cli releases list`\n    if [[ $list = *$sentryReleaseVersion* ]] ; then\n      echo \"...release exist, create deployment\"\n      create_deployment \"$sentryReleaseVersion\" \"$sentryDeploymentTarget\" \"$release\"\n    else\n      echo \"...release doesn't exist, create release and then create deployment\"\n      create_release \"$sentryReleaseVersion\" \"$githubOrg\" \"$sentryCommit\"\n      create_deployment \"$sentryReleaseVersion\" \"$sentryDeploymentTarget\" \"$release\"\n    fi\n  done\nelse\n  echo \"...projPrefix variable value is: $projPrefix, use projPrefix for release prefix\"\n  IFS=','\n  for i in ${SENTRY_PROJECTS}; do\n    sentryReleaseVersion=\"$projPrefix@$release\"\n    echo \"Creating Sentry deployment for Sentry project ${i}, release $sentryReleaseVersion in $sentryDeploymentTarget\"\n    export SENTRY_PROJECT=${i}\n    list=`sentry-cli releases list`\n    sentryReleaseVersionString=\"$sentryReleaseVersion \"\n    if [[ $list = *$sentryReleaseVersionString* ]] ; then\n      echo \"...release exist, create deployment\"\n      create_deployment \"$sentryReleaseVersion\" \"$sentryDeploymentTarget\" \"$release\"\n    else\n      echo \"...release doesn't exist, create release and then create deployment\"\n      create_release \"$sentryReleaseVersion\" \"$githubOrg\" \"$sentryCommit\"\n      create_deployment \"$sentryReleaseVersion\" \"$sentryDeploymentTarget\" \"$release\"\n    fi\n  done\nfi\n\necho \"SentryMarkOctopusStepTemplate.sh - END\"",
                "Octopus.Action.Template.Version": "12",
                "Octopus.Action.Template.Id": "ActionTemplates-350",
                "Octopus.Action.RunOnServer": "true"
            },
            }
        ]
        }
    ]

variables = [
   {
       'Name': 'OctopusPrintEvaluatedVariables',
       'Value': 'false',
       'Type': 'String',
       'IsSensitive': False,
   },
   {
       'Name': 'SENTRY_DSN',
       'Value': f'{credentials.sentry_dsn}',
       'Type': 'String',
       'IsSensitive': False,
   },
   {
       'Name': 'SENTRY_PROJECTS',
       'Value': 'platform-service-template',
       'Type': 'String',
       'IsSensitive': False,
   },
   {
       'Name': 'SENTRY_RELEASE',
       'Value': r'#{Octopus.Project.Name}@#{Octopus.Release.Number}',
       'Type': 'String',
       'IsSensitive': False,
   },
   {
       'Name': 'SentryProjectPrefix',
       'Value': r'#{Octopus.Project.Name}',
       'Type': 'String',
       'IsSensitive': False,
   },
]
