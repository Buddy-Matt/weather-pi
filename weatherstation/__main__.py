#!/usr/bin/python3
import asyncio
from udphandler import UDPHandler
from httpserver import HTTPServer
from weatherdata import WeatherData
from mqtt import MQTT
from gui import GUI
from localdata import LocalData
import sys
import builtins

#print now flushes
builtins._print = builtins.print
def fprint(*args, **kwargs):
  ret = builtins._print(*args, **kwargs)
  sys.stdout.flush()
  return ret
builtins.print = fprint



print("WeatherPi Starting")
#shared weather instance
curWeather = WeatherData()
#udp handler - for getting updates from the real weather station
udphandler = UDPHandler(curWeather)
#http sever - currently unused. May serve up JSON data at some point
httpserver = HTTPServer(curWeather)
#local weather instance
localdata = LocalData()
#GUI For display
gui = GUI(curWeather,localdata)
#MQTT For reporting
mqtt = MQTT()

def dispatchUpdate():
  gui.Update()
  mqtt.SendState({
    "Digoo": curWeather.DataList,
    "Local": localdata.DataList
  })  
curWeather.OnUpdate = dispatchUpdate
localdata.OnUpdate = dispatchUpdate

#main loop
async def main():
  gui.startGUI()
  await udphandler.startListening()
  await httpserver.startServer()
  localdata.startPolling()
  print("Initilisation complete")
  #keep on chugging forever
  await asyncio.Event().wait()

asyncio.run(main())