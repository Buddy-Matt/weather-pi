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