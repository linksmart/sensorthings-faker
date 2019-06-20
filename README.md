# OGC SensorThings Faker
[![Build Status](https://travis-ci.com/linksmart/sensorthings-faker.svg?branch=master)](https://travis-ci.com/linksmart/sensorthings-faker)

This application starts a [GOST](https://github.com/gost/server) OGC SensorThings server and populates it with dummy observations and location history.

## Usage

1. Download the docker-compose script and start all containers:
```
wget https://github.com/linksmart/sensorthings-faker/blob/master/docker-compose.yml
docker-compose up -d
```
2. Wait several minutes to have some data to work with. You should be able to fetch observations from: http://localhost:8095/v1.0/Observations

The server root URL is: http://localhost:8095/v1.0

#### Visualize in Grafana using the latest [SensorThings](https://github.com/linksmart/grafana-sensorthings-datasource) plugin
1. Clone the plugin source code
```
git clone https://github.com/linksmart/sensorthings-faker/blob/master/docker-compose-grafana.yml linksmart-sensorthings-datasource
```
2. Start Grafana with Worldmap Panel
```
docker-compose -f docker-compose-grafana.yml up -d
```
3. Configure SensorThings plugin with:
   - URL: `http://gost:8080/v1.0`
   - Access: server
4. Continue with the [plugin](https://github.com/linksmart/grafana-sensorthings-datasource/blob/master/README.md)