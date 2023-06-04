import math
import ctypes
libc = ctypes.CDLL('libc.so.6')
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

def highFor(dur):
  GPIO.output(gpioPin, GPIO.HIGH)
  libc.usleep(dur)

def lowFor(dur):
  GPIO.output(gpioPin, GPIO.LOW)
  libc.usleep(dur)

def send (msg):
  for i in range(5):
    lowFor(16000)

    for j in range(4):
      highFor(1000)
      lowFor(1000)

    highFor(500)
    lowFor(8000)

    for byte in msg:
      for bitNo in range(8):
        highFor(500)
        if (byte >> (7-bitNo)) & 0x01:
          lowFor(4000)
        else:
          lowFor(2000)

    highFor(500)
    lowFor(80000)

def encodeAndSend(temp, humid):
  msg = encode(0XFD,0,temp,humid,2)
  print ('Sending 443Mhz Packet: ' + ' '.join('{:02x}'.format(x) for x in msg))
  send(msg)
  print ('Sent')
