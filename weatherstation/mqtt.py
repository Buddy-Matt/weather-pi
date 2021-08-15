import paho.mqtt.client as mqtt
import json
from settings import Settings
import asyncio




class MQTT:
  def createClient(self):
    client = mqtt.Client()
    client.username_pw_set(self.__settings['username'],self.__settings['password'])
    return client

  def createOnlineDict(self, topic, timeout):
    client = self.createClient()
    client.will_set(topic,"offline",retain=True)
    return {
      "timeoutTask": None,
      "timeoutTime": timeout,
      "topic": topic,
      "lastTimeStamp": None,
      "client": client
    }

  def __init__(self):
    self.__settings = Settings()['mqtt']
    self.__client = self.createClient()
    self.__statetopic = self.__settings['basetopic'] + '/state'
    self.__weatherstationOnline = self.createOnlineDict(self.__settings['basetopic'] + '/online/weatherstation',60)
    self.__i2cOnline = self.createOnlineDict(self.__settings['basetopic'] + '/online/i2c',60)
    self.__dhtOnline = self.createOnlineDict(self.__settings['basetopic'] + '/online/dht',120)

  def __startAClient(self,client):
    client.connect(self.__settings['host'])
    client.loop_start()

  def StartClient(self):
    self.__startAClient(self.__client)
    self.__startAClient(self.__weatherstationOnline['client'])
    self.__startAClient(self.__i2cOnline['client'])
    self.__startAClient(self.__dhtOnline['client'])
    print('MQTT Running')


  def SendState(self, data):
    self.CheckSetOnline(data['Digoo']['TimeStamp'],self.__weatherstationOnline)
    self.CheckSetOnline(data['Local']['I2C_TimeStamp'],self.__i2cOnline)
    self.CheckSetOnline(data['Local']['DHT_TimeStamp'],self.__dhtOnline)

    del data['Digoo']['TimeStamp']
    del data['Local']['I2C_TimeStamp']
    del data['Local']['DHT_TimeStamp']
    packet = json.dumps(data)

    self.__client.publish(self.__statetopic,packet,0)


  def CheckSetOnline(self, payloadTimeStamp, onlineDict):
    if payloadTimeStamp != None and (onlineDict["lastTimeStamp"] == None or onlineDict["lastTimeStamp"] < payloadTimeStamp):
      onlineDict["lastTimeStamp"] = payloadTimeStamp
      onlineDict["client"].publish(onlineDict["topic"],"online",retain=True)
      if onlineDict["timeoutTask"] != None and not onlineDict["timeoutTask"].cancelled():
        onlineDict["timeoutTask"].cancel()
      onlineDict["timeoutTask"] = asyncio.ensure_future(self.Timeout(onlineDict))

  async def Timeout(self, onlineDict):
    await asyncio.sleep(onlineDict["timeoutTime"])
    onlineDict["client"].publish(onlineDict["topic"],"offline",retain=True)
