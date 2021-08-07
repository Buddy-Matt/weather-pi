#!/usr/bin/python3
import asyncio
from udphandler import UDPHandler
from httpserver import HTTPServer
from weatherdata import WeatherData
from gui import GUI

#shared weather instance
curWeather = WeatherData()
#GUI - in infancy. For display
gui = GUI(curWeather)
#udp handler - for getting updates from the real weather station
udphandler = UDPHandler(curWeather)
#http sever - currently unused. May server up JSON data at some point
httpserver = HTTPServer(curWeather)

def dispatchUpdate():
  gui.Update()
udphandler.OnUpdate = dispatchUpdate

#main loop
async def main():
  gui.startGUI()
  await udphandler.startListening()
  await httpserver.startServer(curWeather)
  print("Initilisation complete")
  #keep on chugging forever
  await asyncio.Event().wait()

asyncio.run(main())