import asyncio
from bleak import BleakScanner

async def main():
    while True:
      devices = await BleakScanner.discover() #scanning_mode='passive',bluez={'or_patterns':['aaa']})
      for d in devices:
          print(d)
          if d.address == 'D5:5D:7C:31:DD:D5':
            ba = d.details['props']['ManufacturerData'][2409]
            print(ba)
            print(''.join('{:02x}'.format(x) for x in ba))
            print(ba[9] - 128)
            print(ba[8])
            print(ba[10])

asyncio.run(main())