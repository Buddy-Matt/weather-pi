from aiohttp import web
from weatherdata import WeatherData

class HTTPServer:
  def __init__(self,weatherData: WeatherData):
    self.__weatherData = weatherData
    

  async def hello(self,request):
      return web.Response(text="Temperature: %.1f°C" % self.__weatherData.MainSensor.Temperature)


  async def startServer(self,wd):
    app = web.Application()
    app.add_routes([web.get('/',self.hello)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner)    
    await site.start()
