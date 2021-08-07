import tkinter as tk
from tkinter import ttk
import threading
from PIL import ImageTk, Image
import requests
from datetime import datetime
import math
import json
import yaml


#Helper to turn GPS into tile loc
def deg2num(lat_deg, lon_deg, zoom):
  lat_rad = math.radians(lat_deg)
  n = 2.0 ** zoom
  xtile = int((lon_deg + 180.0) / 360.0 * n)
  ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
  return (xtile, ytile, zoom)

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
      tile = Image.open(requests.get(url, stream=True).raw)
      finalimage.paste(tile,(x*256,(y+1)*256))

  return finalimage


epoch = datetime.utcfromtimestamp(0)
#Helper to get rainviewer latest image
def nextFrameTime():
    unixtime = int((datetime.utcnow() - epoch).total_seconds())
    return (600 - unixtime % 600) * 1000





class GUI():
  def __init__(self, weatherData):
    self.__weatherData = weatherData
    #grab settings - probably needs it own class ultimately, but will be fine here for now
    with open("settings.yaml","r") as stream:
      try:
        __settings = yaml.load(stream, Loader=yaml.SafeLoader)
      except:
        print("malformed settings file")
        sys.exit()

    #preload images
    self.__tileTarget = deg2num(__settings['map']['lat'],__settings['map']['long'],__settings['map']['zoom'])
    self.__cropOffset = (__settings['map']['cropx'],__settings['map']['cropy'], __settings['map']['cropx']+400, __settings['map']['cropy']+480)
    self.__mapimage = grabImages(self.__tileTarget,"https://tile.openstreetmap.org/",".png").crop(self.__cropOffset)
    self.__rainimages = []


  def addFrame(self,frame):
    rainimage = transparencify(grabImages(self.__tileTarget,"https://tilecache.rainviewer.com%s/256/" % frame['path'],"/1/1_1.png")).crop(self.__cropOffset)
    combinedimage = Image.new('RGBA',(400,480),"BLACK")
    combinedimage.paste(self.__mapimage,(0,0))
    combinedimage.paste(rainimage,(0,0),rainimage)
    self.__rainimages.append((combinedimage,frame['time']))
  


  def updateFrames(self):
    mapdata = json.loads(requests.get('https://api.rainviewer.com/public/weather-maps.json').content)
    newframe = False
    if len(self.__rainimages) == 0:
      for frame in mapdata['radar']['past']:
        self.addFrame(frame)
      newframe = True
    elif mapdata['radar']['past'][12]['time'] != self.__rainimages[12][1]:
      self.addFrame(mapdata['radar']['past'][12])
      self.__rainimages.pop(0)
      newframe = True

    if newframe:
      dispImage = ImageTk.PhotoImage(self.__rainimages[12][0])
      self.__mapImage.configure(image=dispImage)
      self.__mapImage.image = dispImage  

    return newframe

  def frameCheckTimer(self):
    print ("checking for new frames")
    self.__mapImage.after((nextFrameTime() if self.updateFrames() else 0) + 15000,lambda: self.frameCheckTimer())


  def startGUI(self):
    threading.Thread(target=self.__init_gui_thread, args=()).start()

  def Update(self):
    self.__InsideTemp.set("%.1f°C" % self.__weatherData.MainSensor.Temperature)
    self.__InsideHumid.set("%i%%" % self.__weatherData.MainSensor.Humidity)
    self.__OutsideTemp.set("%.1f°C" % self.__weatherData.RemoteSensor.Temperature)
    self.__OutsideHumid.set("%i%%" % self.__weatherData.RemoteSensor.Humidity)

  def __init_gui_thread(self):
    form = tk.Tk()
    #set screen size and no border
    form.geometry("800x480")
    #form.overrideredirect(1)
    form.configure(bg='black')

    #styling
    style = ttk.Style()
    style.theme_use('alt')
    style.configure("TLabelframe", foreground="white", background="black", bordercolor="white")
    style.configure("TLabelframe.Label", foreground="white", background="black")
    style.configure("TLabel", foreground="white", background="black", font="-family {DejaVu Sans} -size 36")
    style.configure("TFrame", foreground="white", background="black")

    #dynamic variables
    self.__InsideTemp = tk.StringVar()
    self.__InsideHumid = tk.StringVar()
    self.__OutsideTemp = tk.StringVar()
    self.__OutsideHumid = tk.StringVar()

    #map
    formmapimage = ImageTk.PhotoImage(self.__mapimage)
    self.__mapImage = ttk.Label(form, image=formmapimage)
    self.__mapImage.place(x=0,y=0,width=400,height=480)

    ttk.Button(form, text="History", command=lambda: self.playHistory(0)).place(x=0, y=0)
    
    #frames
    inframe = ttk.Labelframe(form,text="Indoors", relief=tk.SOLID)
    inframe.place(x=405,y=0,width=190,height=200)

    outframe = ttk.Labelframe(form,text="Outdoors", relief=tk.SOLID)
    outframe.place(x=605,y=0,width=190,height=200)

    wframe = ttk.Labelframe(form,text="Weather", relief=tk.SOLID)
    wframe.place(x=405,y=205,width=390,height=130)

    fcframe = ttk.Labelframe(form,text="Forecast", relief=tk.SOLID)
    fcframe.place(x=405,y=345,width=390,height=130)

    #labels
    ttk.Label(inframe,textvariable=self.__InsideTemp, anchor="center").place(relx=0,relwidth=1.0,rely=0,relheight=0.5)
    ttk.Label(inframe,textvariable=self.__InsideHumid, anchor="center").place(relx=0,relwidth=1.0,rely=0.5,relheight=0.5)
    ttk.Label(outframe,textvariable=self.__OutsideTemp, anchor="center").place(relx=0,relwidth=1.0,rely=0,relheight=0.5)
    ttk.Label(outframe,textvariable=self.__OutsideHumid, anchor="center").place(relx=0,relwidth=1.0,rely=0.5,relheight=0.5)

    #initiate map updater
    #self.frameCheckTimer()
    #get initial values
    self.Update()

    #start gui event loop
    form.mainloop()

  def playHistory(self, frame):
      frameimage = ImageTk.PhotoImage(self.__rainimages[frame][0])
      self.__mapImage.configure(image=frameimage)
      self.__mapImage.image = frameimage
      if frame < 12:
        self.__mapImage.after(200,lambda: self.playHistory(frame+1))


  def test(self):
    self.button.config(text=self.__weatherData.MainSensor.Temperature)



  




