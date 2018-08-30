# OGC SensorThings Faker
This application starts a [GOST](https://github.com/gost/server) OGC SensorThings server and populates it with dummy observations and location history.

## Usage

1. Download the docker-compose script and start all containers:
```
wget https://code.linksmart.eu/projects/OGC-ST/repos/sensorthings-datasource-demo/raw/docker-compose.yml
docker-compose up -d
```
2. Wait few minutes to have some data to work with. You should be able to fetch observations from: http://localhost:8095/v1.0/Observations
3. For Grafana [LinkSmart SensorThings](https://code.linksmart.eu/projects/OGC-ST/repos/grafana-sensorthings-datasource) plugin configuration; use `http://localhost:8095/v1.0` as URL.
