# Development
docker build . -t teamcity
docker run --rm -it -v $(pwd):/app --name teamcity teamcity sh
