import paho.mqtt.client as mqtt
import json
from settings import Settings

class MQTT:
  def __init__(self):
    settings = Settings()['mqtt']
    self.__client = mqtt.Client()
    self.__client.username_pw_set(settings['username'],settings['password'])
    self.__client.connect(settings['host'])
    self.__statepath = settings['statepath']

  def SendState(self, data):
    packet = json.dumps(data)
    self.__client.publish(self.__statepath,packet,0)