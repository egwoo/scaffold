#! /bin/bash

if [[ $# -eq 0 ]] ; then
    echo 'Missing argument - ServiceName should be in PascalCase - example usage: . auctane-dotnet.sh ServiceName'
    exit 1
fi
WORKING_DIR=$(pwd)
SCRIPT_PATH=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "${SCRIPT_PATH}"

SOLUTION=$1
dotnet new sln -o ${SOLUTION}

CLASS_PROJECT_PATH=${SOLUTION}/src/${SOLUTION}
dotnet new classlib -o ${CLASS_PROJECT_PATH}

API_PROJECT_PATH=$SOLUTION/src/$SOLUTION.API
dotnet new webapi -o ${API_PROJECT_PATH}
dotnet add ${API_PROJECT_PATH} package Serilog.AspNetCore
dotnet add ${API_PROJECT_PATH} package Sentry.AspNetCore
dotnet add ${API_PROJECT_PATH} package Swashbuckle.AspNetCore.Swagger
dotnet add ${API_PROJECT_PATH} package Swashbuckle.AspNetCore.SwaggerGen
dotnet add ${API_PROJECT_PATH} package Swashbuckle.AspNetCore.SwaggerUI
dotnet sln ${SOLUTION} add ${SOLUTION}/src/*

# Infra set up
KEBAB_CASE_SOLUTION="$(echo ${SOLUTION} | sed 's/\([A-Z]\)/\-\1/g;s/^-//' | tr '[:upper:]' '[:lower:]')"
KEBAB_CASE_API_PROJECT=${KEBAB_CASE_SOLUTION}-api

# Copy api
cp -R ./template/api/. ${API_PROJECT_PATH}
# Copy infra
mkdir -p ${SOLUTION}/infra/terraform/
cp -R ./template/infra/terraform/{{KEBAB_CASE_SOLUTION}} ${SOLUTION}/infra/terraform/${KEBAB_CASE_SOLUTION}

# Replace template variables
for f in $(find ./${SOLUTION} -iname "*.template")
do
  echo "Processing $f"
  sed -e "s/{{SOLUTION}}/${SOLUTION}/g" -e "s/{{KEBAB_CASE_SOLUTION}}/${KEBAB_CASE_SOLUTION}/g" -e "s/{{KEBAB_CASE_API_PROJECT}}/${KEBAB_CASE_API_PROJECT}/g" $f > ${f/\.template/ }
  rm $f 
done

cd "${WORKING_DIR}"
mv "${SCRIPT_PATH}/${SOLUTION}" .
