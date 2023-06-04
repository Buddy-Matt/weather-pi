#!/usr/bin/python3
import asyncio
from udphandler import UDPHandler
from httpserver import HTTPServer
from digoodata import DigooData
from switchbot import SwitchBot
from mqtt import MQTT
from gui import GUI
from localdata import LocalData
import sys
import builtins
from tx443 import encodeAndSend

#print now flushes
builtins._print = builtins.print
def fprint(*args, **kwargs):
  ret = builtins._print(*args, **kwargs)
  sys.stdout.flush()
  return ret
builtins.print = fprint



print("WeatherPi Starting")
#shared weather instance
curWeather = DigooData()
#udp handler - for getting updates from the real weather station
udphandler = UDPHandler(curWeather)
#http sever - currently unused. May serve up JSON data at some point
httpserver = HTTPServer(curWeather)
#local weather instance
localdata = LocalData()
#switchbot thermohygrometer bluetooth instance
switchbot = SwitchBot()
#GUI For display
gui = GUI(curWeather,localdata, switchbot)
#MQTT For reporting
mqtt = MQTT()

def dispatchUpdate():
  gui.Update()
  mqtt.SendState({
    "Digoo": curWeather.DataList,
    "Local": localdata.DataList,
    "SwitchBot": switchbot.DataList
  }) 

async def sbUpdate():
  await encodeAndSend(switchbot.Temp,switchbot.Humidity)
  dispatchUpdate()

curWeather.OnUpdate = dispatchUpdate
localdata.OnUpdate = dispatchUpdate
switchbot.OnUpdate = sbUpdate

#main loop
async def main():
  gui.startGUI()
  mqtt.StartClient()
  await udphandler.startListening()
  await httpserver.startServer()
  localdata.startPolling()
  switchbot.startPolling()
  print("Initilisation complete")
  #keep on chugging forever
  await asyncio.Event().wait()

asyncio.run(main())