import tkinter as tk
import tksvg
from tkinter import ttk
import asyncio
from PIL import Image,ImageTk
import requests
from datetime import datetime
import math
import json
import pylunar
import sys
from settings import Settings

#Helper to turn GPS into tile loc
def deg2num(lat_deg, lon_deg, zoom):
  lat_rad = math.radians(lat_deg)
  n = 2.0 ** zoom
  xtile = int((lon_deg + 180.0) / 360.0 * n)
  ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
  return (xtile, ytile, zoom)

def dd2dms(d):
  neg = (d < 0)
  s = abs(d) * 3600.0
  m,s = divmod(s,60.0)
  d,m = divmod(m,60.0)
  if neg:
    if d > 0:
      d = -d
    elif m > 0:
      m = -m
    else:
      s = -s
  return (d,m,s)


#Helper to turn block into transparent pixel
def transparencify(img):
  img = img.convert("RGBA")
  datas = img.getdata()

  newData = []
  for item in datas:
      if item[0] == 0 and item[1] == 0 and item[2] == 0:
          newData.append((0, 0, 0, 0))
      else:
          newData.append(item)

  img.putdata(newData)
  return img

#Helper to get tiles from web
def grabImages(target,preXYurl,postXYurl):
  finalimage = Image.new('RGB',(512,778))

  for x in range(0,2):
    for y in range(-1,2):
      url = "%s%s/%s/%s%s" % (preXYurl, target[2], target[0] + x, target[1] + y, postXYurl)
      print("Grabbing %s" % url)
      tile = Image.open(requests.get(url, headers={'User-Agent': 'WeatherPI'}, stream=True).raw)
      finalimage.paste(tile,(x*256,(y+1)*256))

  return finalimage

def epochToTimeString(epoch):
  return datetime.fromtimestamp(epoch).strftime('%H:%M:%S')

epoch = datetime.utcfromtimestamp(0)
#Helper to get rainviewer latest image
def nextFrameTime():
    unixtime = int((datetime.utcnow() - epoch).total_seconds())
    return (600 - unixtime % 600) * 1000

def nextMidnight():
    unixtime = int((datetime.utcnow() - epoch).total_seconds())
    return (86400 - unixtime % 86400) * 1000


class GUI():
  def __init__(self, digooData, localData, switchbot):
    self.ready = False
    self.__digooData = digooData
    self.__localData = localData
    self.__switchbot = switchbot
    settings = Settings()['map']


    #preload images
    self.__tileTarget = deg2num(settings['lat'],settings['long'],settings['zoom'])
    self.__cropOffset = (settings['cropx'],settings['cropy'], settings['cropx']+400, settings['cropy']+480)
    self.__mapimage = grabImages(self.__tileTarget,"https://tile.openstreetmap.org/",".png").crop(self.__cropOffset)
    self.__rainimages = []

    #mooninfo
    self.__mi = pylunar.MoonInfo(dd2dms(settings['lat']),dd2dms(settings['long']))


  def addFrame(self,frame):
    rainimage = transparencify(grabImages(self.__tileTarget,"https://tilecache.rainviewer.com%s/256/" % frame['path'],"/1/1_1.png")).crop(self.__cropOffset)
    combinedimage = Image.new('RGBA',(400,480),"BLACK")
    combinedimage.paste(self.__mapimage,(0,0))
    combinedimage.paste(rainimage,(0,0),rainimage)
    self.__rainimages.append((combinedimage,frame['time']))
  


  def updateFrames(self):
    try:
      mapdata = json.loads(requests.get('https://api.rainviewer.com/public/weather-maps.json').content)
      newframe = False
      if len(self.__rainimages) == 0:
        for frame in mapdata['radar']['past']:
          self.addFrame(frame)
        newframe = (int((datetime.utcnow() - epoch).total_seconds()) - self.__rainimages[12][1]) < 600
      elif mapdata['radar']['past'][12]['time'] != self.__rainimages[12][1]:
        self.addFrame(mapdata['radar']['past'][12])
        self.__rainimages.pop(0)
        newframe = True

      if newframe:
        dispImage = ImageTk.PhotoImage(self.__rainimages[12][0])
        self.__mapImage.configure(image=dispImage)
        self.__mapImage.image = dispImage
        self.__RainTime.set(epochToTimeString(self.__rainimages[12][1]))

      return newframe
    except:
      return False


  def startTimedFuncs(self):
    self.__moonPhase.after(50, lambda: self.moonCheck())
    #self.__mapImage.after(1000, lambda: self.rainCheck())

  def rainCheck(self):
    print ("checking for new frames")
    self.__mapImage.after((nextFrameTime() if self.updateFrames() else 0) + 15000,lambda: self.rainCheck())

  def moonCheck(self):
    print ("Checking moon phase")
    self.__mi.update(datetime.utcnow())
    phaseicon = self.__phases[self.__mi.phase_name()]
    self.__moonPhase.configure(image=phaseicon)
    self.__moonPhase.image = phaseicon
    self.__moonPhase.after(nextMidnight() + 1000, lambda: self.moonCheck())


  def startGUI(self):
    asyncio.get_running_loop().run_in_executor(None, self.__init_gui_thread)

  def Update(self):
    if self.ready:# and self.__digooData.Timestamp != None:
#      self.__InsideTemp.set("%.1f°C" % self.__digooData.MainSensor.Temperature)
#      self.__InsideHumid.set("%i%%" % self.__digooData.MainSensor.Humidity)
#      self.__OutsideTemp.set("%.1f°C" % self.__digooData.RemoteSensor.Temperature)
#      self.__OutsideHumid.set("%i%%" % self.__digooData.RemoteSensor.Humidity)
      self.__InsideTemp.set("%.1f°C" % (self.__localData.Temp or 0))
      self.__InsideHumid.set("%i%%" % (self.__localData.Humidity or 0))
      self.__OutsideTemp.set("%.1f°C" % (self.__switchbot.Temp or 0))
      self.__OutsideHumid.set("%i%%" % (self.__switchbot.Humidity or 0))

      if self.__digooData.Timestamp != None:
        self.__Barometer.set("%ihPa" % self.__digooData.Pressure )
        weathericon = self.__iconsBig[self.__digooData.RawForecast]
        self.__forcastMain.configure(image=weathericon)
        self.__forcastMain.image = weathericon


  def __init_gui_thread(self):
    self.__form = tk.Tk()
    #set screen size and no border
    self.__form.geometry("800x480")
    #form.overrideredirect(1)
    self.__form.configure(bg='black')

    #styling
    style = ttk.Style()
    style.theme_use('alt')
    style.configure("TLabelframe", foreground="white", background="black", bordercolor="white")
    style.configure("TLabelframe.Label", foreground="white", background="black")
    style.configure("TLabel", foreground="white", background="black")
    style.configure("Big.TLabel", font="-family {'Nimbus Sans Narrow' Sans} -size 36")
    style.configure("Medium.TLabel", font="-family {'Nimbus Sans Narrow' Sans} -size 24")
    style.configure("TFrame", foreground="white", background="black")

    #icons
    self.__iconsBig = {
    0x00: tksvg.SvgImage(file="weatherstation/img/sun.svg", scaletoheight=80),
    0x10: tksvg.SvgImage(file="weatherstation/img/partcloud.svg", scaletoheight=80),
    0x20: tksvg.SvgImage(file="weatherstation/img/cloud.svg", scaletoheight=80),
    0x30: tksvg.SvgImage(file="weatherstation/img/rain.svg", scaletoheight=80),
    0x40: tksvg.SvgImage(file="weatherstation/img/thunder.svg", scaletoheight=80),
    0x50: tksvg.SvgImage(file="weatherstation/img/snow.svg", scaletoheight=80),
    }

    self.__iconsSmall = {
    0x00: tksvg.SvgImage(file="weatherstation/img/sun.svg", scaletowidth=30),
    0x10: tksvg.SvgImage(file="weatherstation/img/partcloud.svg", scaletowidth=30),
    0x20: tksvg.SvgImage(file="weatherstation/img/cloud.svg", scaletowidth=30),
    0x30: tksvg.SvgImage(file="weatherstation/img/rain.svg", scaletowidth=30),
    0x40: tksvg.SvgImage(file="weatherstation/img/thunder.svg", scaletowidth=30),
    0x50: tksvg.SvgImage(file="weatherstation/img/snow.svg", scaletowidth=30)
    }    

    self.__phases = {
    'NEW_MOON': tksvg.SvgImage(file="weatherstation/img/moon-new.svg", scaletoheight=80),
    'WAXING_CRESCENT': tksvg.SvgImage(file="weatherstation/img/moon-waxing.svg", scaletoheight=80),
    'FIRST_QUARTER': tksvg.SvgImage(file="weatherstation/img/moon-waxing-quarter.svg", scaletoheight=80),
    'WAXING_GIBBOUS': tksvg.SvgImage(file="weatherstation/img/moon-waxing-gibbous.svg", scaletoheight=80),
    'FULL_MOON': tksvg.SvgImage(file="weatherstation/img/moon-full.svg", scaletoheight=80),
    'WANING_GIBBOUS': tksvg.SvgImage(file="weatherstation/img/moon-waning-gibbous.svg", scaletoheight=80),
    'LAST_QUARTER': tksvg.SvgImage(file="weatherstation/img/moon-waning-quarter.svg", scaletoheight=80),
    'WANING_CRESCENT': tksvg.SvgImage(file="weatherstation/img/moon-waning.svg", scaletoheight=80),
    } 



    #map
    formmapimage = ImageTk.PhotoImage(self.__mapimage)
    self.__mapImage = ttk.Label(self.__form, image=formmapimage)
    self.__mapImage.place(x=0,y=0,width=400,height=480)

    ttk.Button(self.__form, text="History", command=lambda: self.playHistory(0)).place(x=0, y=0)
    
    #frames
    inframe = ttk.Labelframe(self.__form,text="Indoors", relief=tk.SOLID)
    inframe.place(x=405,y=0,width=190,height=200)

    outframe = ttk.Labelframe(self.__form,text="Outdoors", relief=tk.SOLID)
    outframe.place(x=605,y=0,width=190,height=200)

    wframe = ttk.Labelframe(self.__form,text="Weather", relief=tk.SOLID)
    wframe.place(x=405,y=205,width=390,height=130)

    mpframe = ttk.Labelframe(wframe,text="Moon Phase", relief=tk.FLAT, labelanchor="n")
    mpframe.place(relx=0, relwidth=0.25, rely=0, relheight=1)

    cfframe = ttk.Labelframe(wframe,text="Forecast", relief=tk.FLAT, labelanchor="n")
    cfframe.place(relx=0.25, relwidth=0.25, rely=0, relheight=1)

    bframe = ttk.Labelframe(wframe,text="Barometer", relief=tk.FLAT, labelanchor="n")
    bframe.place(relx=0.5, relwidth=0.5, rely=0, relheight=1)

    fcframe = ttk.Labelframe(self.__form,text="Met.no Forecast", relief=tk.SOLID)
    fcframe.place(x=405,y=345,width=390,height=130)

    #dynamic variables
    self.__InsideTemp = tk.StringVar()
    self.__InsideHumid = tk.StringVar()
    self.__OutsideTemp = tk.StringVar()
    self.__OutsideHumid = tk.StringVar()
    self.__Barometer = tk.StringVar()
    self.__RainTime = tk.StringVar()

    #labels
    ttk.Label(inframe,textvariable=self.__InsideTemp, anchor="center", style="Big.TLabel").place(relx=0,relwidth=1.0,rely=0,relheight=0.5)
    ttk.Label(inframe,textvariable=self.__InsideHumid, anchor="center", style="Big.TLabel").place(relx=0,relwidth=1.0,rely=0.5,relheight=0.5)
    ttk.Label(outframe,textvariable=self.__OutsideTemp, anchor="center", style="Big.TLabel").place(relx=0,relwidth=1.0,rely=0,relheight=0.5)
    ttk.Label(outframe,textvariable=self.__OutsideHumid, anchor="center", style="Big.TLabel").place(relx=0,relwidth=1.0,rely=0.5,relheight=0.5)
    self.__moonPhase = ttk.Label(mpframe,anchor="center")
    self.__moonPhase.place(relx=0, relwidth=1, rely=0, relheight=1)
    self.__forcastMain = ttk.Label(cfframe,anchor="center")
    self.__forcastMain.place(relx=0, relwidth=1, rely=0, relheight=1)
    ttk.Label(bframe,textvariable=self.__Barometer, anchor="center", style="Medium.TLabel").place(relx=0,relwidth=1.0,rely=0,relheight=1.0)
    ttk.Label(self.__form,textvariable=self.__RainTime, anchor="center", style="TLabel").place(relx=0.0, rely=1.0, anchor="sw")
    
    #initiate various timed updates
    self.startTimedFuncs()
    #get initial values
    self.Update()

    #start gui event loop
    self.ready = True
    self.__form.mainloop()

  def playHistory(self, frame):
      frameimage = ImageTk.PhotoImage(self.__rainimages[frame][0])
      self.__mapImage.configure(image=frameimage)
      self.__mapImage.image = frameimage
      self.__RainTime.set(epochToTimeString(self.__rainimages[frame][1]))
      if frame < 12:
        self.__mapImage.after(200,lambda: self.playHistory(frame+1))



  




