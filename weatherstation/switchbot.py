import asyncio
from bleak import BleakScanner
from datetime import datetime

class SwitchBot:

  def __init__(self):
    self.__timestamp = None
    self.__battery = None
    self.__humidity = None
    self.__temp = None
    self.__timeoutTask = None

  async def __poll(self):
    while True:
      d = await BleakScanner.find_device_by_address('D5:5D:7C:31:DD:D5')
      if d:
        print("SwitchBot data received")
        ba = d.details['props']['ManufacturerData'][2409]
        self.__battery = ba[7] & 127
        self.__temp = (ba[9] - 128) + (ba[8] / 10)
        self.__humidity = ba[10]
        self.__timestamp = datetime.now()
        if self.__onUpdate != None:
          await self.__onUpdate()

        #start offline timer
        if self.__timeoutTask != None and not self.__timeoutTask.cancelled():
          self.__timeoutTask.cancel()
        self.__timeoutTask = asyncio.ensure_future(self.__timeout())
      await asyncio.sleep(29)

  async def __timeout(self):
    await asyncio.sleep(120)
    self.__init__()
    if self.__onUpdate != None:
      await self.__onUpdate()      

  def startPolling(self):
    self.__loop = asyncio.get_running_loop()
    self.__loop.create_task(self.__poll())


  @property
  def Temp(self):
    return self.__temp
  
  @property
  def Humidity(self):
    return self.__humidity
  
  @property
  def Battery(self):
    return self.__battery
  
  @property
  def Timestamp(self):
    return self.__timestamp
  
  @property
  def OnUpdate(self):
    return self.__onUpdate

  @OnUpdate.setter
  def OnUpdate(self, func):
    self.__onUpdate = func
  
  @property
  def DataList(self):
    return {
      "TimeStamp": self.Timestamp,
      "Temperature": self.Temp,
      "Humidity": self.Humidity,
      "Battery": self.Battery
    }