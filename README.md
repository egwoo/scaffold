# Development
Copy `credentials_example.py` to `credentials.py` and populate the appropriate values.

## Usage
```
docker build . -t scaffold
docker run -v ${PATH_TO_C#_SERVICE}:/target scaffold {SERVICE_NAME}
```

## Clean Up
* Octopus
    * Project
    * Project Group
    * Library - Variable Sets
    * Library - Packages
* Sentry - Project
* TeamCity - Project
* EKS - ???
