#! /bin/bash

. dotnet/auctane-dotnet.sh $1
python3 cicd/setup.py --solution_name $1
