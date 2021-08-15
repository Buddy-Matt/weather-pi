from Adafruit_BMP import BMP085
import adafruit_dht
import adafruit_bh1750
import board
import asyncio
from datetime import datetime

class LocalData:

  def __init__(self):
    self.__bmp = BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES) #ULTRAHIGHRES mode as we're not taking many samples
    self.__dht = adafruit_dht.DHT11(board.D4)
    self.__bh = adafruit_bh1750.BH1750(board.I2C())
    self.__bmp180_temp = None
    self.__bmp180_pressure = None
    self.__dht11_temp = None
    self.__dht11_humidity = None
    self.__bh1750_lux = None
    self.__i2c_timestamp = None
    self.__dht_timestamp = None

  @property
  def OnUpdate(self):
    return self.__onUpdate

  @OnUpdate.setter
  def OnUpdate(self, func):
    self.__onUpdate = func

  async def __poll(self):
    while True:
      try:
        self.__bmp180_temp = self.__bmp.read_temperature()
        self.__bmp180_pressure = self.__bmp.read_pressure()
        self.__bh1750_lux = self.__bh.lux
        self.__i2c_timestamp = datetime.now()
        self.__dht11_temp = self.__dht.temperature
        self.__dht11_humidity= self.__dht.humidity
        self.__dht_timestamp = datetime.now()
      except:
        pass

      if self.__onUpdate != None:
        self.__onUpdate()      

      await asyncio.sleep(30)


  def startPolling(self):
    self.__loop = asyncio.get_running_loop()
    self.__loop.create_task(self.__poll())

  @property
  def Bmp180_Temp(self):
    return self.__bmp180_temp

  @Bmp180_Temp.setter
  def Bmp180_Temp(self,val):
    self.__bmp180_temp = val
  
  @property
  def Bmp180_Pressure(self):
    return self.__bmp180_pressure

  @Bmp180_Pressure.setter
  def Bmp180_Pressure(self,val):
    self.__bmp180_pressure = val


  @property
  def Dht11_Temp(self):
    return self.__dht11_temp

  @Dht11_Temp.setter
  def Dht11_Temp(self,val):
    self.__dht11_temp = val

  @property
  def Dht11_Humidity(self):
    return self.__dht11_humidity

  @Dht11_Humidity.setter
  def Dht11_Humidity(self,val):
    self.__dht11_humidity = val

  


  @property
  def Bh1750_Lux(self):
    return self.__bh1750_lux

  @Bh1750_Lux.setter
  def Bh1750_Lux(self,val):
    self.__bh1750_lux = val



  @property
  def Temp(self):
    if self.__dht11_temp == None:
      if self.__bmp180_temp == None:
        return None
      else:
        return self.__bmp180_temp
    elif self.__bmp180_temp == None:
      return self.__dht11_temp
    else:
      return round((self.__dht11_temp + self.__bmp180_temp) / 2,1)

  @property
  def Pressure(self):
    return self.__bmp180_pressure

  @property
  def Humidity(self):
    return self.__dht11_humidity

  @property
  def Lux(self):
    return self.__bh1750_lux

  @property
  def DataList(self):
    return {
      "I2C_TimeStamp": self.__i2c_timestamp,
      "DHT_TimeStamp": self.__dht_timestamp,
      "Temperature": self.Temp,
      "Temperature_Sensors": {
        "BMP180" : self.Bmp180_Temp,
        "DHT11": self.Dht11_Temp
      },
      "Pressure": self.Pressure,
      "Humidity": self.Humidity,
      "Lux": self.Lux
    }