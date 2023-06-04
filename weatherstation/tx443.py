import math
import asyncio
import RPi.GPIO as GPIO

gpioPin = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(gpioPin, GPIO.OUT)

def checksum(msg):
  remainder = 0
  poly = 0x13 << 4
  nBytes = 4
  for byteNo in range(4):
    remainder ^= msg[byteNo]
    for bit in range(8):
      if (remainder & 0x80):
        remainder = (remainder << 1) ^ poly
      else:
        remainder = (remainder << 1)
  return (remainder >> 4 & 0x0F) ^ (msg[4] >> 4)

def encode (id,flags, temp, humid, chan):
  temp_f = (temp * 9/5) + 32 + 90
  temp_bytes = (math.ceil(temp_f*10) << 4).to_bytes(2,byteorder='big')
  msgBytes = [id & 0xFF, ((chan & 0xF) << 4) | (flags & 0xF), temp_bytes[0], temp_bytes[1] | (math.floor(humid/10) & 0xF), ((humid % 10) << 4) | (chan & 0xF)]
  msgBytes[1] = (checksum(msgBytes) << 4) |  (msgBytes[1] & 0x0F)
  return msgBytes

async def highFor(dur):
  GPIO.output(gpioPin, GPIO.HIGH)
  await asyncio.sleep(dur/1000000)

async def lowFor(dur):
  GPIO.output(gpioPin, GPIO.LOW)
  await asyncio.sleep(dur/1000000)

async def send (msg):
  for i in range(5):
    await lowFor(16000)

    for j in range(4):
      await highFor(1000)
      await lowFor(1000)

    await highFor(500)
    await lowFor(8000)

    for byte in msg:
      for bitNo in range(8):
        await highFor(500)
        if (byte >> (7-bitNo)) & 0x01:
          await lowFor(4000)
        else:
          await lowFor(2000)

    await highFor(500)
    await lowFor(80000)

async def encodeAndSend(temp, humid):
  msg = encode(0XFF,0,temp,humid,2)
  await send(msg)
