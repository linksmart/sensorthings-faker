
# coding: utf-8

import requests
import json
import random
from time import sleep
from datetime import datetime

class Faker:
    def __init__(self):
        self.headers = {'Content-type': 'application/json; charset=utf-8'}
        self.location_id = 0
        self.min_temp = 10
        self.max_temp = 30
        self.min_speed = 10
        self.max_speed = 60
        self.all_location_ids = []
        self.delay = 10
        self.rooturl = "http://gost:8080/v1.0"
        print "init"

    def create_location(self,data):
        headers = {'Content-type': 'application/json; charset=utf-8'}
        response = requests.post(self.rooturl+'/Locations',headers=headers,json=data)

    def delete_location(self,location_id):
        response = requests.delete(self.rooturl+'/Locations('+location_id+')')

    def create_locations(self):
        print "creating locations started"

        with open('locations.json') as data_file:
            locations = json.load(data_file)
            for location in locations:
                if not self.has_location(location['name']):
                    headers = {'Content-type': 'application/json; charset=utf-8'}
                    response = requests.post(self.rooturl+'/Locations',headers=headers,json=location)
                    self.location_id = response.json()['@iot.id']
                    self.all_location_ids.append(self.location_id)

        print "creating locations finished"

    def has_location(self,location_name):
        response = requests.get(self.rooturl+"/Locations?$filter=name eq '" + location_name + "'")
        response_locations = response.json()['value']
        count = len(response_locations)
        if (count >= 1):
            self.location_id = response_locations[0]['@iot.id']
            self.all_location_ids.append(self.location_id)
            return True
        else:
            return False

    def has_thing(self,thing_name):
        response = requests.get(self.rooturl+"/Things?$filter=name eq '" + thing_name + "'")
        response_things = response.json()['value']
        count = len(response_things)
        return response_things[0] if (count >= 1) else None

    def create_thing(self):

        thing_data = {
          "name": "new vehicle",
          "description": "Local shuttle",
          "Locations": [
            {"@iot.id":self.location_id}
          ]
        }

        thing = self.has_thing(thing_data['name'])

        if thing is not None:
            return thing

        thing = requests.post(self.rooturl+'/Things',headers=self.headers,json=thing_data).json()

        return thing

    def has_sensor(self,sensor_name):

        response = requests.get(self.rooturl+"/Sensors?$filter=name eq '" + sensor_name + "'")
        response_sensors = response.json()['value']
        count = len(response_sensors)
        return response_sensors[0] if (count >= 1) else None

    def create_sensor(self,sensor_data):

        sensor = self.has_sensor(sensor_data['name'])

        if sensor is not None:
            return sensor

        sensor = requests.post(self.rooturl+'/Sensors',headers=self.headers,json=sensor_data).json()

        return sensor

    def has_observed_property(self,observed_property_name):

        response = requests.get(self.rooturl+"/ObservedProperties?$filter=name eq '" + observed_property_name + "'")
        response_observed_properties = response.json()['value']
        count = len(response_observed_properties)
        return response_observed_properties[0] if (count >= 1) else None

    def create_observed_property(self,observed_property_data):

        observed_property = self.has_observed_property(observed_property_data['name'])

        if observed_property is not None:
            return observed_property

        observed_property = requests.post(self.rooturl+'/ObservedProperties',headers=self.headers,json=observed_property_data).json()

        return observed_property

    def has_datastream(self,thing_id,datastream_name):

        response = requests.get(self.rooturl+"/Things("+str(thing_id)+")/Datastreams?$filter=name eq '" + datastream_name + "'")

        response_datastreams = response.json()['value']

        count = len(response_datastreams)

        return response_datastreams[0] if (count >= 1) else None

    def create_datastream(self,datastream_data):

        datastream = self.has_datastream(datastream_data["Thing"]['@iot.id'],datastream_data["name"])

        if datastream is not None:
            return datastream

        datastream = requests.post(self.rooturl+'/Datastreams',headers=self.headers,json=datastream_data).json()

        return datastream

    def random_string(self):
        return ('%06x' % random.randrange(16**6)).upper()

    def create_observation(self,datastream_id,result):
        timestamp = datetime.now().isoformat()[:-3] + 'Z'
        observation = {
          "phenomenonTime": timestamp,
          "resultTime" : timestamp,
          "result" : result,
          "Datastream":{"@iot.id":datastream_id}
        }
        return requests.post(self.rooturl+'/Observations',headers=self.headers,json=observation)

    def update_thing(self,thing_id,location_id):
        thing = {
          "Locations": [
            {"@iot.id":location_id}
          ]
        }
        return requests.patch(self.rooturl+'/Things('+str(thing_id)+')',headers=self.headers,json=thing)


    def seed_observations(self):

        # create a thing
        thing =  self.create_thing()
        thing_id = thing['@iot.id']

        # create a temperature sensor
        temperature_sensor = {
          "name": "Temperature",
          "description": "Measures temperature inside vehicle",
          "encodingType": "application/pdf",
          "metadata": "demo"
        }
        temperature_sensor_id = self.create_sensor(temperature_sensor)['@iot.id']

        # create an observed property for temperature reading
        temperature_observed_property = {
          "name": "Temperature DS observed property",
          "description": "Temperature DS observed property",
          "definition": "Demo definition"
        }

        temperature_observed_property_id = self.create_observed_property(temperature_observed_property)['@iot.id']

        #create datastream for temperature sensor
        temperature_datastream = {
          "name": "Air Temperature DS",
          "description": "Datastream for recording temperature",
          "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement",
          "unitOfMeasurement": {
            "name": "Degree Celsius",
            "symbol": "degC",
            "definition": "http://www.qudt.org/qudt/owl/1.0.0/unit/Instances.html#DegreeCelsius"
          },
          "Thing":{"@iot.id":thing_id},
          "ObservedProperty":{"@iot.id":temperature_observed_property_id},
          "Sensor":{"@iot.id":temperature_sensor_id}
        }

        temperature_datastream_id = self.create_datastream(temperature_datastream)['@iot.id']

        # create a Speedometer sensor
        speed_sensor = {
          "name": "Speed",
          "description": "Measures Speed of the vehicle",
          "encodingType": "application/pdf",
          "metadata": "demo"
        }
        speed_sensor_id = self.create_sensor(speed_sensor)['@iot.id']

        # create an observed property for speedometer reading
        speed_observed_property = {
          "name": "Speed DS observed property",
          "description": "Speed DS observed property",
          "definition": "Demo definition"
        }
        speed_observed_property_id = self.create_observed_property(speed_observed_property)['@iot.id']

        #create datastream for speedometer sensor
        speed_datastream = {
          "name": "Speedometer DS",
          "description": "Measures speed of vehicle",
          "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement",
          "unitOfMeasurement": {
            "name": "Km",
            "symbol": "Km",
            "definition": "Demo definition"
          },
          "Thing":{"@iot.id":thing_id},
          "ObservedProperty":{"@iot.id":speed_observed_property_id},
          "Sensor":{"@iot.id":speed_sensor_id}
        }

        speedometer_datastream_id = self.create_datastream(speed_datastream)['@iot.id']

        sensor_flag = True
        location_count = len(self.all_location_ids)
        forward_direction = True
        current_location = 0

        while True:
            if sensor_flag is True:
                temperature_value = round(random.uniform(self.min_temp,self.max_temp),2)
                self.create_observation(temperature_datastream_id,temperature_value)
                sensor_flag = False
            else:
                speed_value = random.randint(self.min_speed,self.max_speed)
                self.create_observation(speedometer_datastream_id,speed_value)
                sensor_flag = True

            if forward_direction is True:
                self.update_thing(thing_id,self.all_location_ids[current_location])
                current_location += 1
                if current_location == location_count:
                    forward_direction = False
                    current_location -= 2
            else:
                self.update_thing(thing_id,self.all_location_ids[current_location])
                current_location -= 1
                if current_location == -1:
                    forward_direction = True
                    current_location += 2
            sleep(self.delay)

# Infinite loop
while True:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(("gost-db", 5432))
    if result == 0:
        print("gost-db port is open! Bye!")
        break
    else:
        print("gost-db port is not open! I'll check it soon!")
        time.sleep(3)
        
faker = Faker()
faker.create_locations()
faker.seed_observations()
