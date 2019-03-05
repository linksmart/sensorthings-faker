# OGC SensorThings Faker
This application starts a [GOST](https://github.com/gost/server) OGC SensorThings server and populates it with dummy observations and location history.

## Usage

1. Download the docker-compose script and start all containers:
```
wget https://code.linksmart.eu/projects/OGC-ST/repos/sensorthings-datasource-demo/raw/docker-compose.yml
docker-compose up -d
```
2. Wait several minutes to have some data to work with. You should be able to fetch observations from: http://localhost:8095/v1.0/Observations

#### Visualize in Grafana using the latest [SensorThings](https://code.linksmart.eu/projects/OGC-ST/repos/grafana-sensorthings-datasource) plugin
1. Clone the plugin source code
```
git clone https://code.linksmart.eu/scm/ogc-st/grafana-sensorthings-datasource.git linksmart-sensorthings-datasource
```
2. Start Grafana with Worldmap Panel
```
docker-compose -f docker-compose-grafana.yml up -d
```
3. Configure SensorThings plugin with:
   - URL: `http://gost:8080/v1.0`
   - Access: server
4. Continue with the [plugin](https://code.linksmart.eu/projects/OGC-ST/repos/grafana-sensorthings-datasource/browse/README.md)