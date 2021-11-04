# Development
Copy `credentials_example.py` to `credentials.py` and populate the appropriate values.

## Develop in Docker
```
docker build . -t scaffold
# *nix
docker run --rm -it -v $(pwd):/app --name scaffold scaffold sh
# Powershell
docker run --rm -it -v ${PWD}:/app --name scaffold scaffold sh
```

## Run script
```
docker build . -t scaffold
docker run scaffold --name '{My Platform Service}'
```

If you need to clean up Octopus, these are the objects to clean up:
- Project
- Project Group
- Library - Variable Sets
