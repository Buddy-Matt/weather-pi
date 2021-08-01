#!/usr/bin/python3

import socket
import sys
import asyncio
import datetime
import math
from weatherdata import WeatherData
import os

HOST, PORT = '0.0.0.0', 17000


# async def requestWeather():
# 	while True:
# 		try:
# 			message = bytearray()
# 			message.append(0x3c)
# 			message.append(0x57)
# 			message.append(0x01)
# 			message.append(0x69)
# 			message.append(0xf0)
# 			message.append(0x71)
# 			message.append(0x10)
# 			message.append(0x90) #function number
# 			message.append(0x00)
# 			message.append(0x00)
# 			message.append(0x00) #payload size
# 			message.append(0x3e)
# 			#payload goes here
# 			csum = sum(message) % 256
# 			message.append(csum)
# 			message.append(0x3e)
# 			print ('sending "%s"' % message, file=sys.stderr)
# 			await loop.sock_sendall(sock,message)
# 		except Exception as err:
# 			print(err)
# 		await asyncio.sleep(30)

sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  

def decode_sensor(data):
	print(data)

def decode_weather(data):
		os.system("clear")
		wd = WeatherData(data)
		print()
		print(wd.Timestamp)
		print()
		print("Forcecast: %s" % wd.Forecast)
		print("Pressure: %ihPa" % wd.Pressure)
		print()
		print("Outdoor Sensor")
		print("==============")
		wd.RemoteSensor.OutputValues()
		print()
		print("Indoor Sensor")
		print("==============")
		wd.MainSensor.OutputValues()

def handle_client(data,addr):
	func = data[7]
	plen = data[10]
	if func == 1 and plen > 0:
		decode_weather(data[0x0C:0x0C+plen]) # 57 bytes of data
	elif func == 0 or func ==1:
		sock.sendto(data,addr) #bounce


class UDPHandler(asyncio.DatagramProtocol):
	def __init__(self):
		super().__init__()

	def connection_made(self, transport):
		self.transport = transport
	
	def datagram_received(self, data, addr):
		handle_client(data,addr)


loop = asyncio.get_event_loop()
t = loop.create_datagram_endpoint(UDPHandler, local_addr=(HOST,PORT))
loop.run_until_complete(t)
print("server created")
loop.run_forever()

