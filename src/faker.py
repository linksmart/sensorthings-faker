
# coding: utf-8

# In[ ]:


import requests
import json
import random
from time import sleep
from datetime import datetime


# In[ ]:


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
        print "init"

    def create_location(self,data):
        headers = {'Content-type': 'application/json; charset=utf-8'}
        response = requests.post('http://gost:8080/v1.0/Locations',headers=headers,json=data)

    def delete_location(self,location_id):
        response = requests.delete('http://gost:8080/v1.0/Locations('+location_id+')')

    def create_locations(self):
        print "creating locations started"

        with open('locations.json') as data_file:
            locations = json.load(data_file)
            for location in locations:
                if not self.has_location(location['name']):
                    headers = {'Content-type': 'application/json; charset=utf-8'}
                    response = requests.post('http://gost:8080/v1.0/Locations',headers=headers,json=location)
                    self.location_id = response.json()['@iot.id']
                    self.all_location_ids.append(self.location_id)

        print "creating locations finished"

    def has_location(self,location_name):
        response = requests.get("http://gost:8080/v1.0/Locations?$filter=name eq '" + location_name + "'")
        response_locations = response.json()['value']
        count = len(response_locations)
        if (count >= 1):
            self.location_id = response_locations[0]['@iot.id']
            self.all_location_ids.append(self.location_id)
            return True
        else:
            return False

    def has_thing(self,thing_name):
        response = requests.get("http://gost:8080/v1.0/Things?$filter=name eq '" + thing_name + "'")
        count = len(response.json()['value'])
        return True if (count >= 1) else False

    def create_thing(self):

        thing = {
          "name": "Vehicle " + self.random_string(),
          "description": "Local shuttle",
          "Locations": [
            {"@iot.id":self.location_id}
          ]
        }

        return requests.post('http://gost:8080/v1.0/Things',headers=self.headers,json=thing)

    def create_sensor(self,sensor):
        return requests.post('http://gost:8080/v1.0/Sensors',headers=self.headers,json=sensor)

    def create_observed_property(self):

        observed_property = {
          "name": "Demo observed property" + self.random_string(),
          "description": "Demo observed property",
          "definition": "Demo definition"
        }

        return requests.post('http://gost:8080/v1.0/ObservedProperties',headers=self.headers,json=observed_property)

    def create_datastream(self,datastream):
        return requests.post('http://gost:8080/v1.0/Datastreams',headers=self.headers,json=datastream)

    def random_string(self):
        return ('%06x' % random.randrange(16**6)).upper()

    def create_observation(self,datastream_id,result):
        timestamp = datetime.utcnow().isoformat()[:-3] + 'Z'
        observation = {
          "phenomenonTime": timestamp,
          "resultTime" : timestamp,
          "result" : result,
          "Datastream":{"@iot.id":datastream_id}
        }
        return requests.post('http://gost:8080/v1.0/Observations',headers=self.headers,json=observation)

    def update_thing(self,thing_id,location_id):
        thing = {
          "Locations": [
            {"@iot.id":location_id}
          ]
        }
        return requests.patch('http://gost:8080/v1.0/Things('+str(thing_id)+')',headers=self.headers,json=thing)


    def seed_observations(self):

        # create a thing
        thing =  self.create_thing()
        print thing.text
        thing_id = thing.json()['@iot.id']

        # create a temperature sensor
        temperature_sensor = {
          "name": "Temperature " + self.random_string(),
          "description": "Measures temperature inside vehicle",
          "encodingType": "application/pdf",
          "metadata": "demo"
        }
        temperature_sensor_id = self.create_sensor(temperature_sensor).json()['@iot.id']

        # create an observed property for temperature reading
        temperature_observed_property_id = self.create_observed_property().json()['@iot.id']

        #create datastream for temperature sensor
        temperature_datastream = {
          "name": "Air Temperature DS " + self.random_string(),
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

        temperature_datastream_id = self.create_datastream(temperature_datastream).json()['@iot.id']

        # create a Speedometer sensor
        speed_sensor = {
          "name": "Speed " + self.random_string(),
          "description": "Measures Speed of the vehicle",
          "encodingType": "application/pdf",
          "metadata": "demo"
        }
        speed_sensor_id = self.create_sensor(speed_sensor).json()['@iot.id']

        # create an observed property for speedometer reading
        speed_observed_property_id = self.create_observed_property().json()['@iot.id']

        #create datastream for speedometer sensor
        speed_datastream = {
          "name": "Speedometer DS " + self.random_string(),
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

        speedometer_datastream_id = self.create_datastream(speed_datastream).json()['@iot.id']

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
# In[ ]:


faker = Faker()
faker.create_locations()
faker.seed_observations()
