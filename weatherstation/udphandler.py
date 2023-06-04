import socket
from digoodata import DigooData
import os
import asyncio
import sys

HOST, PORT = '0.0.0.0', 17000
sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  




class UDPHandler():
  class __Factory(asyncio.DatagramProtocol):
    def __init__(self, parent):
      super().__init__()
      self.parent = parent

    def connection_made(self, transport):
      self.transport = transport

    def datagram_received(self, data, addr):
      func = data[7]
      plen = data[10]
      if func == 1 and plen > 0:
        self.parent.decode_weather(data[0x0C:0x0C+plen]) # 57 bytes of data
      elif func == 0 or func ==1:
        sock.sendto(data,addr) #bounce



  def __init__(self,digooData: DigooData):
    self.__digooData = digooData
    self.__onUpdate = None

  async def startListening(self):
    loop = asyncio.get_running_loop()
    await loop.create_datagram_endpoint(lambda : self.__Factory(self), local_addr=(HOST,PORT))
    print("server created")

  def decode_weather(self, data: bytearray):
    print("Digoo data received")
    self.__digooData.Update(data)

