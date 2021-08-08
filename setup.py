#!/usr/bin/python3

import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


install('aiohttp')
install('pillow')
install('pyyaml')
install('tkinter')
install('tksvg')
install('pylunar')