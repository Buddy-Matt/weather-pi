import math

class Sensor:
  def __init__(self):
    self.__temperature = 0
    self.__humidity = 0
    self.__maxTemperature = 0
    self.__maxHumidity = 0
    self.__minTemperature = 0
    self.__minHumidity = 0

  def Update(self,data):
    if (data == b'\0xff\0xff\0xff\0xff\0xff\0xff\0xff\0xff\0xff'):
      self.__init__()
    else:
      self.Temperature = data[0x00:0x02]
      self.Humidity = data[0x02:0x03]
      self.MaxTemperature = data[0x03:0x05]
      self.MaxHumidity = data[0x05:0x06]
      self.MinTemperature = data[0x06:0x08]
      self.MinHumidity = data[0x08:0x09]

  def __tfrombytes(self,data):
    raw = int.from_bytes(data,byteorder="little")
    return math.floor((raw - 1220) / 1.8) / 10

  def OutputValues(self):
    print("Temperature: %.1f°C" % self.Temperature )
    print("Humidity: %i%%" % self.Humidity )
    print("Max Temperature: %.1f°C" % self.MaxTemperature )
    print("Max Humidity: %i%%" % self.MaxHumidity )
    print("Min Temperature: %.1f°C" % self.MinTemperature )
    print("Min Humidity: %i%%" % self.MinHumidity )

  @property
  def Humididty(self):
    return self.__humidity

  @Humididty.setter
  def Humidity(self,data):
    self.__humidity = int.from_bytes(data,byteorder="little")

  @property
  def Temperature(self):
    return self.__temperature

  @Temperature.setter
  def Temperature(self,data):
    self.__temperature = self.__tfrombytes(data)

  @property
  def MaxHumidity(self):
    return self.__maxHumidity

  @MaxHumidity.setter
  def MaxHumidity(self,data):
    self.__maxHumidity = int.from_bytes(data,byteorder="little")
  
  @property
  def MaxTemperature(self):
    return self.__maxTemperature

  @MaxTemperature.setter
  def MaxTemperature(self,data):
    self.__maxTemperature = self.__tfrombytes(data)

  @property
  def MinHumidity(self):
    return self.__minHumidity

  @MinHumidity.setter
  def MinHumidity(self,data):
    self.__minHumidity = int.from_bytes(data,byteorder="little")

  @property
  def MinTemperature(self):
    return self.__minTemperature

  @MinTemperature.setter
  def MinTemperature(self,data):
    self.__minTemperature = self.__tfrombytes(data)

  @property
  def DataList(self):
    return {
      "Temperature": self.Temperature,
      "Humidity": self.Humidity
    }