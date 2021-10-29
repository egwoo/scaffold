# Development
Copy `credentials_example.py` to `credentials.py` and populate the appropriate values.

## Develop in docker
```
docker build . -t scaffold
docker run --rm -it -v $(pwd):/app --name scaffold scaffold sh
```
### In Docker (for now)
```
python3 octopus.py
```
