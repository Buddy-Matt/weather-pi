import paho.mqtt.client as mqtt
import json
from settings import Settings
import getmac



class MQTT:
  def createClient(self):
    client = mqtt.Client()
    client.username_pw_set(self.__settings['username'],self.__settings['password'])
    return client

  def createOnlineDict(self, topic):
    client = self.createClient()
    client.will_set(topic,"offline",retain=True)
    return {
      "topic": topic,
      "client": client
    }

  def __init__(self):
    self.__settings = Settings()['mqtt']
    self.__client = self.createClient()
    self.__statetopic = self.__settings['basetopic'] + '/state'
    self.__weatherstationOnline = self.createOnlineDict(self.__settings['basetopic'] + '/online/weatherstation')
    self.__i2cOnline = self.createOnlineDict(self.__settings['basetopic'] + '/online/i2c')
    self.__dhtOnline = self.createOnlineDict(self.__settings['basetopic'] + '/online/dht')
    self.__switchbotOnline = self.createOnlineDict(self.__settings['basetopic'] + '/online/switchbot')

  def __startAClient(self,client):
    client.connect(self.__settings['host'])
    client.loop_start()

  def __registerHA(self):
    if self.__settings['hatopic'] != None:
      Payload = {
        "unique_id": getmac.get_mac_address() + ":temp",
        "name": "WeatherPI Temperature",
        "availability_topic": self.__i2cOnline["topic"],
        "device": {
          "manufacturer":"Buddy-Matt",
          "model":"WeatherPI",
          "name":"WeatherPI",
          "identifiers":[getmac.get_mac_address()]
        },
        "device_class": "temperature",
        "state_class": "measurement",
        "state_topic": self.__settings['basetopic'] + '/state',
        "value_template": "{{ value_json.Local." + ("Temperature_Sensors.BMP180" if self.__settings['tempsensor'] == "i2c" else ("Temperature_Sensors.DHT11" if self.__settings['tempsensor'] == "dht" else "Temperature")) + "}}",
        "unit_of_measurement": "°C"
      }
      self.__client.publish(self.__settings['hatopic'] + "/sensor/weatherpi/temperature/config", json.dumps(Payload), retain=True)
      Payload = {
        "unique_id": getmac.get_mac_address() + ":pressure",
        "name": "WeatherPI Pressure",
        "availability_topic": self.__i2cOnline["topic"],
        "device": {
          "manufacturer":"Buddy-Matt",
          "model":"WeatherPI",
          "name":"WeatherPI",
          "identifiers":[getmac.get_mac_address()]
        },
        "device_class": "pressure",
        "state_class": "measurement",
        "state_topic": self.__settings['basetopic'] + '/state',
        "value_template": "{{ value_json.Local.Pressure }}",
        "unit_of_measurement": "hPa"
      }
      self.__client.publish(self.__settings['hatopic'] + "/sensor/weatherpi/pressure/config", json.dumps(Payload), retain=True)
      Payload = {
        "unique_id": getmac.get_mac_address() + ":humidity",
        "name": "WeatherPI Humidity",
        "availability_topic": self.__dhtOnline["topic"],
        "device": {
          "manufacturer":"Buddy-Matt",
          "model":"WeatherPI",
          "name":"WeatherPI",
          "identifiers":[getmac.get_mac_address()]
        },
        "device_class": "humidity",
        "state_class": "measurement",
        "state_topic": self.__settings['basetopic'] + '/state',
        "value_template": "{{ value_json.Local.Humidity }}",
        "unit_of_measurement": "%"
      }
      self.__client.publish(self.__settings['hatopic'] + "/sensor/weatherpi/humidity/config", json.dumps(Payload), retain=True)
      Payload = {
        "unique_id": getmac.get_mac_address() + ":lux",
        "name": "WeatherPI Lux",
        "availability_topic": self.__i2cOnline["topic"],
        "device": {
          "manufacturer":"Buddy-Matt",
          "model":"WeatherPI",
          "name":"WeatherPI",
          "identifiers":[getmac.get_mac_address()]
        },
        "device_class": "illuminance",
        "state_class": "measurement",
        "state_topic": self.__settings['basetopic'] + '/state',
        "value_template": "{{ value_json.Local.Lux }}",
        "unit_of_measurement": "lx"
      }
      self.__client.publish(self.__settings['hatopic'] + "/sensor/weatherpi/illuminance/config", json.dumps(Payload), retain=True)
      Payload = {
        "unique_id": getmac.get_mac_address() + ":digoo:pressure",
        "name": "Digoo Pressure",
        "availability_topic": self.__weatherstationOnline["topic"],
        "device": {
          "manufacturer":"Digoo",
          "model":"DG-EX001",
          "name":"Digoo Weather Station",
          "identifiers":[getmac.get_mac_address() + ":digoo"],
          "via_device": getmac.get_mac_address()
        },
        "device_class": "pressure",
        "state_class": "measurement",
        "state_topic": self.__settings['basetopic'] + '/state',
        "value_template": "{{ value_json.Digoo.Pressure }}",
        "unit_of_measurement": "hPa"
      }
      self.__client.publish(self.__settings['hatopic'] + "/sensor/digoo/pressure/config", json.dumps(Payload), retain=True)
      Payload = {
        "unique_id": getmac.get_mac_address() + ":digoo:forecast",
        "name": "Digoo Forecast",
        "availability_topic": self.__weatherstationOnline["topic"],
        "device": {
          "manufacturer":"Digoo",
          "model":"DG-EX001",
          "name":"Digoo Weather Station",
          "identifiers":[getmac.get_mac_address() + ":digoo"],
          "via_device": getmac.get_mac_address()
        },
        "state_topic": self.__settings['basetopic'] + '/state',
        "value_template": "{{ value_json.Digoo.Forecast }}"
      }
      self.__client.publish(self.__settings['hatopic'] + "/sensor/digoo/forecast/config", json.dumps(Payload), retain=True)
      Payload = {
        "unique_id": getmac.get_mac_address() + ":digoo:inside:temperature",
        "name": "Digoo Inside Temperature",
        "availability_topic": self.__weatherstationOnline["topic"],
        "device": {
          "manufacturer":"Digoo",
          "model":"DG-EX001",
          "name":"Digoo Weather Station",
          "identifiers":[getmac.get_mac_address() + ":digoo"],
          "via_device": getmac.get_mac_address()
        },
        "device_class": "temperature",
        "state_class": "measurement",
        "state_topic": self.__settings['basetopic'] + '/state',
        "value_template": "{{ value_json.Digoo.MainSensor.Temperature }}",
        "unit_of_measurement": "°C"
      }
      self.__client.publish(self.__settings['hatopic'] + "/sensor/digoo/insidetemperature/config", json.dumps(Payload), retain=True)
      Payload = {
        "unique_id": getmac.get_mac_address() + ":digoo:inside:humidity",
        "name": "Digoo Inside Humidity",
        "availability_topic": self.__weatherstationOnline["topic"],
        "device": {
          "manufacturer":"Digoo",
          "model":"DG-EX001",
          "name":"Digoo Weather Station",
          "identifiers":[getmac.get_mac_address() + ":digoo"],
          "via_device": getmac.get_mac_address()
        },
        "device_class": "humidity",
        "state_class": "measurement",
        "state_topic": self.__settings['basetopic'] + '/state',
        "value_template": "{{ value_json.Digoo.MainSensor.Humidity }}",
        "unit_of_measurement": "%"
      }
      self.__client.publish(self.__settings['hatopic'] + "/sensor/digoo/insidehumidity/config", json.dumps(Payload), retain=True)
      Payload = {
        "unique_id": getmac.get_mac_address() + ":digoo:outside:temperature",
        "name": "Digoo Outside Temperature",
        "availability_topic": self.__weatherstationOnline["topic"],
        "device": {
          "manufacturer":"Digoo",
          "model":"DG-EX001",
          "name":"Digoo Weather Station",
          "identifiers":[getmac.get_mac_address() + ":digoo"],
          "via_device": getmac.get_mac_address()
        },
        "device_class": "temperature",
        "state_class": "measurement",
        "state_topic": self.__settings['basetopic'] + '/state',
        "value_template": "{{ value_json.Digoo.RemoteSensor.Temperature }}",
        "unit_of_measurement": "°C"
      }
      self.__client.publish(self.__settings['hatopic'] + "/sensor/digoo/outsidetemperature/config", json.dumps(Payload), retain=True)
      Payload = {
        "unique_id": getmac.get_mac_address() + ":digoo:outside:humidity",
        "name": "Digoo Outside Humidity",
        "availability_topic": self.__weatherstationOnline["topic"],
        "device": {
          "manufacturer":"Digoo",
          "model":"DG-EX001",
          "name":"Digoo Weather Station",
          "identifiers":[getmac.get_mac_address() + ":digoo"],
          "via_device": getmac.get_mac_address()
        },
        "device_class": "humidity",
        "state_class": "measurement",
        "state_topic": self.__settings['basetopic'] + '/state',
        "value_template": "{{ value_json.Digoo.RemoteSensor.Humidity }}",
        "unit_of_measurement": "%"
      }
      self.__client.publish(self.__settings['hatopic'] + "/sensor/digoo/outsidehumidity/config", json.dumps(Payload), retain=True)
      Payload = {
        "unique_id": getmac.get_mac_address() + ":switchbot:temperature",
        "name": "SwitchBot Temperature",
        "availability_topic": self.__switchbotOnline["topic"],
        "device": {
          "manufacturer":"SwitchBot",
          "model":"Indoor/Outdoor Thermo-Hygrometer",
          "name":"SwitchBot Indoor/Outdoor Thermo-Hygrometer",
          "identifiers":[getmac.get_mac_address() + ":switchbot"],
          "via_device": getmac.get_mac_address()
        },
        "device_class": "temperature",
        "state_class": "measurement",
        "state_topic": self.__settings['basetopic'] + '/state',
        "value_template": "{{ value_json.SwitchBot.Temperature }}",
        "unit_of_measurement": "°C"
      }
      self.__client.publish(self.__settings['hatopic'] + "/sensor/switchbot/temperature/config", json.dumps(Payload), retain=True)
      Payload = {
        "unique_id": getmac.get_mac_address() + ":switchbot:humidity",
        "name": "SwitchBot Humidity",
        "availability_topic": self.__switchbotOnline["topic"],
        "device": {
          "manufacturer":"SwitchBot",
          "model":"Indoor/Outdoor Thermo-Hygrometer",
          "name":"SwitchBot Indoor/Outdoor Thermo-Hygrometer",
          "identifiers":[getmac.get_mac_address() + ":switchbot"],
          "via_device": getmac.get_mac_address()
        },
        "device_class": "humidity",
        "state_class": "measurement",
        "state_topic": self.__settings['basetopic'] + '/state',
        "value_template": "{{ value_json.SwitchBot.Humidity }}",
        "unit_of_measurement": "%"
      }
      self.__client.publish(self.__settings['hatopic'] + "/sensor/switchbot/humidity/config", json.dumps(Payload), retain=True)



  def StartClient(self):
    try:
      self.__startAClient(self.__client)
      self.__startAClient(self.__weatherstationOnline['client'])
      self.__startAClient(self.__i2cOnline['client'])
      self.__startAClient(self.__dhtOnline['client'])
      self.__startAClient(self.__switchbotOnline['client'])
      self.__registerHA()
    except Exception as e:
      print(e)

    print('MQTT Running')


  def SendState(self, data):
    self.CheckSetOnline(data['Digoo']['TimeStamp'],self.__weatherstationOnline)
    self.CheckSetOnline(data['Local']['I2C_TimeStamp'],self.__i2cOnline)
    self.CheckSetOnline(data['Local']['DHT_TimeStamp'],self.__dhtOnline)
    self.CheckSetOnline(data['SwitchBot']['TimeStamp'],self.__switchbotOnline)

    del data['Digoo']['TimeStamp']
    del data['Local']['I2C_TimeStamp']
    del data['Local']['DHT_TimeStamp']
    del data['SwitchBot']['TimeStamp']

    packet = json.dumps(data)

    self.__client.publish(self.__statetopic,packet,0)


  def CheckSetOnline(self, payloadTimeStamp, onlineDict):
    onlineDict["client"].publish(onlineDict["topic"],"online" if payloadTimeStamp != None else "offline",retain=True)
