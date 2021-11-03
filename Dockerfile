FROM python:3.11.0a1-alpine3.14

RUN apk update
RUN apk upgrade
RUN apk --no-cache add curl

RUN pip3 install --upgrade pip

COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt

WORKDIR /app

COPY . .

# ENTRYPOINT [ "python3", "octopus.py" ]
# CMD []
