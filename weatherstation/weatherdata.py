from datetime import datetime
from sensor import Sensor
import math

class WeatherData:

  def __init__(self):
    self.__timestamp = None
    self.__battery = None
    self.__lostsignal = None
    self.__mainSensor = Sensor()
    self.__remoteSensor = Sensor()
    self.__pressure = None
    self.__forecast = None

  @property
  def OnUpdate(self):
    return self.__onUpdate

  @OnUpdate.setter
  def OnUpdate(self, func):
    self.__onUpdate = func

  def Update(self,data):
    self.Timestamp = data[0x01:0x08]

    self.__battery = data[0x2d]
    self.__lostsignal = data[0x2e]

    self.MainSensor = data[0x09:0x12]
    self.RemoteSensor = data[0x12:0x1b]
#    self.RemoteSensor2 = data[0x1b:0x24]
#    self.RemoteSensor3 = data[0x24:0x2d]
    self.Pressure = data[0x2f:0x31]
    self.Forecast = data[0x31]

    if self.__onUpdate != None:
      self.__onUpdate()


  @property
  def Timestamp(self):
    return self.__timestamp
  @Timestamp.setter
  def Timestamp(self,data: bytearray):
    self.__timestamp = datetime(2000 + data[0x01], #year
											       		data[0x02], #month
    	        									data[0x03], 
		      		    							data[0x04],
	  				  	        				data[0x05],
  				  	  			 	  			math.floor(data[0x06] / 2)
                                )

  @property
  def Pressure(self):
    return self.__pressure
  @Pressure.setter
  def Pressure(self,data: bytearray):
    self.__pressure = int.from_bytes(data,byteorder="little")

  @property
  def Forecast(self):
    return self.__forecast
  @Forecast.setter
  def Forecast(self,data):
    self.__rawforecast = data
    if data == 0x00:
      self.__forecast = 'Sunny'
    elif data == 0x10:
      self.__forecast = 'Partial Clouds'
    elif data == 0x20:
      self.__forecast = 'Cloudy'
    elif data == 0x30:
      self.__forecast = 'Rain'
    elif data == 0x40:
      self.__forecast = 'Thunder'
    else:
      self.__forecast = 'Unknown (%x)' % data

  @property
  def RawForecast(self):
    return self.__rawforecast
  @RawForecast.setter
  def RawForecast(self,data):
    self.Forcecast(data)

  @property
  def MainSensor(self):
    return self.__mainSensor
  @MainSensor.setter
  def MainSensor(self,data: bytearray):
    self.__mainSensor.Update(data)

  @property
  def RemoteSensor(self):
    return self.__remoteSensor
  @RemoteSensor.setter
  def RemoteSensor(self,data: bytearray):
    self.__remoteSensor.Update(data)


  @property
  def DataList(self):
    return {
      "TimeStamp": self.Timestamp,
      "Pressure": self.Pressure,
      "Forecast": self.Forecast,
      "MainSensor": self.MainSensor.DataList,
      "RemoteSensor": self.RemoteSensor.DataList
    }