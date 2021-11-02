# Development
Copy `credentials_example.py` to `credentials.py` and populate the appropriate values.

## Develop in docker
```
docker build . -t scaffold
docker run scaffold --name '{My Platform Service}'
```

If you need to clean up Octopus, these are the objects to clean up:
- Project
- Project Group
- Library - Variable Sets
