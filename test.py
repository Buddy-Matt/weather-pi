import asyncio
from bleak import BleakScanner
from datetime import datetime
import time

async def main():
    while True:
      devices = await BleakScanner.discover() #scanning_mode='passive',bluez={'or_patterns':['aaa']})
      for d in devices:
          #print(d)
          if d.address == 'D5:5D:7C:31:DD:D5':
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            print(current_time)
            ba = d.details['props']['ManufacturerData'][2409]
            print(ba)
            print(''.join('{:02x}'.format(x) for x in ba))
            print('Major')
            print( (1 if (ba[9] & 128) == 128 else -1) * (ba[9] & 127) )
            print('Minor')
            print(ba[8])
            print('combined')
            print((1 if (ba[9] & 128) == 128 else -1) * ((ba[9] & 127) + (ba[8] / 10)))
            print('humid')
            print(ba[10])
            time.sleep(30)

asyncio.run(main())