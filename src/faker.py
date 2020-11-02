
# coding: utf-8

import requests
import json
import random
import socket
import os
import threading
from time import sleep
from datetime import datetime

GOST = os.environ.get('GOST')
GOSTDB = os.environ.get('GOSTDB')
GOSTDB_PORT = os.environ.get('GOSTDB_PORT')
print("GOST: {}".format(GOST))
print("POSTGRES HOST: {} PORT: {}".format(GOSTDB, GOSTDB_PORT))
if GOST==None or GOSTDB==None or GOSTDB_PORT==None:
    print("Environment variables are not set.")
    os._exit(1)


class Faker:
    def __init__(self):
        self.headers = {'Content-type': 'application/json; charset=utf-8'}
        self.location_id = 0
        self.min_temp = 10
        self.max_temp = 30
        self.min_speed = 10
        self.max_speed = 60
        self.min_people = 0
        self.max_people = 10
        self.delay = 20
        self.all_location_ids = []
        self.rooturl = GOST
        print("init")

    def create_location(self,data):
        headers = {'Content-type': 'application/json; charset=utf-8'}
        response = requests.post(self.rooturl+'/Locations',headers=headers,json=data)

    def delete_location(self,location_id):
        response = requests.delete(self.rooturl+'/Locations('+location_id+')')

    def create_locations(self, filename):
        print("creating locations started. Source file: {}").format(filename)

        with open(filename) as data_file:
            locations = json.load(data_file)
            for location in locations:
                if not self.has_location(location['name']):
                    headers = {'Content-type': 'application/json; charset=utf-8'}
                    response = requests.post(self.rooturl+'/Locations',headers=headers,json=location)
                    self.location_id = response.json()['@iot.id']
                    self.all_location_ids.append(self.location_id)
                    print("create_locations {}").format(location)

        print("creating locations finished")

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

    def create_thing(self, filename, name):
      with open(filename) as data_file:
        things_data = json.load(data_file)
        print(things_data)
        
        for thing_data in things_data:
            # print("name {}".format(thing_data))
            if thing_data['name'] == name:
                print("Found: {}".format(name))
                break
        else: 
            thing_data = None

        if thing_data is None:
            print("Could not find {} in {}".format(name,filename))
            return
        
        thing = self.has_thing(thing_data['name'])

        if thing is not None:
          return thing

        print("create_thing {}".format(thing_data))
        return requests.post(self.rooturl+'/Things',headers=self.headers,json=thing_data).json()

    def has_sensor(self,sensor_name):

        response = requests.get(self.rooturl+"/Sensors?$filter=name eq '" + sensor_name + "'")
        response_sensors = response.json()['value']
        count = len(response_sensors)
        return response_sensors[0] if (count >= 1) else None

    def create_sensor(self,sensor_data):

        sensor = self.has_sensor(sensor_data['name'])

        if sensor is not None:
            return sensor

        print("create_sensor {}".format(sensor_data))
        return requests.post(self.rooturl+'/Sensors',headers=self.headers,json=sensor_data).json()

    def has_observed_property(self,observed_property_name):

        response = requests.get(self.rooturl+"/ObservedProperties?$filter=name eq '" + observed_property_name + "'")
        response_observed_properties = response.json()['value']
        count = len(response_observed_properties)
        return response_observed_properties[0] if (count >= 1) else None

    def create_observed_property(self,observed_property_data):

        observed_property = self.has_observed_property(observed_property_data['name'])

        if observed_property is not None:
            return observed_property

        print("create_observed_property {}".format(observed_property_data))
        return requests.post(self.rooturl+'/ObservedProperties',headers=self.headers,json=observed_property_data).json()

    def has_datastream(self,thing_id,datastream_name):

        response = requests.get(self.rooturl+"/Things("+str(thing_id)+")/Datastreams?$filter=name eq '" + datastream_name + "'")

        response_datastreams = response.json()['value']

        count = len(response_datastreams)

        return response_datastreams[0] if (count >= 1) else None

    def create_datastream(self,datastream_data):

        datastream = self.has_datastream(datastream_data["Thing"]['@iot.id'],datastream_data["name"])

        if datastream is not None:
            return datastream

        print("create_datastream {}".format(datastream_data))
        return requests.post(self.rooturl+'/Datastreams',headers=self.headers,json=datastream_data).json()

    def random_string(self):
        return ('%06x' % random.randrange(16**6)).upper()
    
    def current_time(self):
      return datetime.now().isoformat()[:-3] + 'Z'

    def create_observation(self,datastream_id,result,timestamp):
        observation = {
          "phenomenonTime": timestamp,
          "resultTime" : timestamp,
          "result" : result,
          "Datastream":{"@iot.id":datastream_id}
        }
        
        print("create_observation {}".format(observation))
        return requests.post(self.rooturl+'/Observations',headers=self.headers,json=observation)

    def update_thing(self,thing_id,location_id):
        thing = {
          "Locations": [
            {"@iot.id":location_id}
          ]
        }
        print("update_thing {}".format(thing))
        return requests.patch(self.rooturl+'/Things('+str(thing_id)+')',headers=self.headers,json=thing)

    def create_people_observation(self,people_datastream_id,timestamp):               
        front = random.randint(self.min_people,self.max_people)
        rear = random.randint(self.min_people,self.max_people)
        self.create_observation(people_datastream_id,{"front": front, "rear": rear},timestamp)


    def seed_data(self, thing, fast):

        thing_id = thing['@iot.id']
        thing_name = thing['name']

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

        # create a people-counter sensor
        people_sensor = {
          "name": "PeopleCounter",
          "description": "Measures the number of people traversing an entrance",
          "encodingType": "application/pdf",
          "metadata": "demo"
        }
        people_sensor_id = self.create_sensor(people_sensor)['@iot.id']

        # create an observed property for people-counter reading
        people_observed_property = {
          "name": "People Counter DS observed property",
          "description": "People Counter DS observed property",
          "definition": "Demo definition"
        }
        people_observed_property_id = self.create_observed_property(people_observed_property)['@iot.id']

        # create datastream for people-counter sensor
        people_datastream = {
          "name": "People Counter DS",
          "description": "Datastream for recording number of people traversing from each entrance",
          "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Observation",
          "unitOfMeasurement": None,
          "Thing":{"@iot.id":thing_id},
          "ObservedProperty":{"@iot.id":people_observed_property_id},
          "Sensor":{"@iot.id":people_sensor_id}
        }
        people_datastream_id = self.create_datastream(people_datastream)['@iot.id']

        location_count = len(self.all_location_ids)
        forward_direction = True
        current_location = 0

        # create observations
        i = 0
        while True:
            timestamp = self.current_time()
            print("Thing({}): {} @ {}".format(thing_id, thing_name, timestamp))

            # if i==0:
            #   self.create_people_observation(people_datastream_id,timestamp)

            if i%3==0:
              # add temperature observation
              temperature_value = round(random.uniform(self.min_temp,self.max_temp),2)
              self.create_observation(temperature_datastream_id,temperature_value,timestamp)

            # add speed observation
            speed_value = random.randint(self.min_speed*2 if fast else self.min_speed,self.max_speed*2 if fast else self.max_speed)
            self.create_observation(speedometer_datastream_id,speed_value,timestamp)  

            # change location
            if forward_direction is True:
                self.update_thing(thing_id,self.all_location_ids[current_location])
                current_location += 1
                if current_location == location_count:
                    forward_direction = False
                    current_location -= 2
                    # add people observation
                    self.create_people_observation(people_datastream_id,timestamp)
            else:
                self.update_thing(thing_id,self.all_location_ids[current_location])
                current_location -= 1
                if current_location == -1:
                    forward_direction = True
                    current_location += 2
                    # add people observation
                    self.create_people_observation(people_datastream_id,timestamp)
            sleep(self.delay/2 if fast else self.delay)
            i+=1

# wait for the server
while True:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((GOSTDB, int(GOSTDB_PORT)))
    if result == 0:
        print("postgres port is open!")
        break
    else:
        print("postgres port is not open! Will retry in 3s.")
        sleep(3)


faker = Faker()
faker.create_locations('locations.json')

thing_0 = faker.create_thing('things.json', name="Fraunhofer FIT Shuttle Bus")
thing_1 = faker.create_thing('things.json', name="Fraunhofer FIT Express")

threading.Thread(target=faker.seed_data, args=(thing_0,False,)).start()
threading.Thread(target=faker.seed_data, args=(thing_1,True,)).start()
