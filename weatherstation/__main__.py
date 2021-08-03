#!/usr/bin/python3
import asyncio
from udphandler import UDPHandler
from httpserver import HTTPServer
from weatherdata import WeatherData

async def main():
  curWeather = WeatherData()
  udphandler = UDPHandler(curWeather)
  await udphandler.startListening()
  httpserver = HTTPServer(curWeather)
  await httpserver.startServer(curWeather)
  await asyncio.Event().wait()

asyncio.run(main())