
# coding: utf-8

# In[71]:


import requests
import json
import random


# In[102]:


class Faker:
    def __init__(self):
        self.headers = {'Content-type': 'application/json; charset=utf-8'}
        print "init"
        
    def create_location(self,data):
        headers = {'Content-type': 'application/json; charset=utf-8'}
        response = requests.post('http://localhost:8080/v1.0/Locations',headers=headers,json=data)
        
    def delete_location(self,location_id):
        response = requests.delete('http://localhost:8080/v1.0/Locations('+location_id+')')   
    
    def create_locations(self):
        print "creating locations started"
        
        with open('locations.json') as data_file:    
            locations = json.load(data_file)
            for location in locations:
                if not self.has_location(location['name']):
                    headers = {'Content-type': 'application/json; charset=utf-8'}
                    response = requests.post('http://localhost:8080/v1.0/Locations',headers=headers,json=location)
                    
        print "creating locations finished"
                    
    def has_location(self,location_name):
        response = requests.get("http://localhost:8080/v1.0/Locations?$filter=name eq '" + location_name + "'")
        count = len(response.json()['value'])
        return True if (count >= 1) else False
    
    def has_thing(self,thing_name):
        response = requests.get("http://localhost:8080/v1.0/Things?$filter=name eq '" + thing_name + "'")
        count = len(response.json()['value'])
        return True if (count >= 1) else False
    
    def create_thing(self):

        thing = {
          "name": "Vehicle " + self.random_string(),
          "description": "Local shuttle",
        }
        
        return requests.post('http://localhost:8080/v1.0/Things',headers=self.headers,json=thing)

    def create_sensor(self,sensor):
        return requests.post('http://localhost:8080/v1.0/Sensors',headers=self.headers,json=sensor)
        
    def create_observed_property(self):

        observed_property = {
          "name": "Demo observed property" + self.random_string(),
          "description": "Demo observed property",
          "definition": "Demo definition"
        }
        
        return requests.post('http://localhost:8080/v1.0/ObservedProperties',headers=self.headers,json=observed_property)    

    def create_datastream(self,datastream):
        return requests.post('http://localhost:8080/v1.0/Datastreams',headers=self.headers,json=datastream)    
        
    def random_string(self):
        return ('%06x' % random.randrange(16**6)).upper()
    
    def seed_observations(self):
        
        # create a thing
        thing_id = self.create_thing().json()['@iot.id']
        
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
        
        print self.create_datastream(temperature_datastream).json()
        
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
        
        print self.create_datastream(speed_datastream).json()
        
        
        


# In[103]:


faker = Faker()
faker.create_locations()
faker.seed_observations()
# faker.create_thing().json()['@iot.id']
# faker.create_sensor()
# faker.run_seeder()

