from aiohttp import web
from digoodata import DigooData

class HTTPServer:
  def __init__(self,digooData: DigooData):
    self.__digooData = digooData
    

  async def hello(self,request):
      return web.Response(text="Temperature: %.1f°C" % self.__digooData.MainSensor.Temperature)


  async def startServer(self):
    app = web.Application()
    app.add_routes([web.get('/',self.hello)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner)    
    await site.start()
