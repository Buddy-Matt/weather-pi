#!/usr/bin/python3

import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


install('aiohttp')
install('pillow')
install('pyyaml')
install('scikit-build')
install('tksvg')
install('pylunar')
install('paho-mqtt')
install('adafruit-bmp')
install('adafruit-circuitpython-dht')
install('adafruit-circuitpython-bh1750')
install('get-mac')
install('bleak')

#subprocess.check_call(["git","clone","https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code.git","extlib/"])

print('Please also apt install libgpiod2')
