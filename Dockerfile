FROM mcr.microsoft.com/dotnet/core/sdk:3.1

RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install --upgrade pip

COPY cicd/requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt

WORKDIR /app

COPY . .

RUN chmod +x /app/dotnet/auctane-dotnet.sh
RUN chmod +x /app/scaffold.sh

ENTRYPOINT [ "/app/scaffold.sh" ]
CMD []
