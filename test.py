import asyncio
from bleak import BleakScanner

async def main():
    while True:
      d = await BleakScanner.find_device_by_address('D5:5D:7C:31:DD:D5')
      print(d)
      ba = d.details['props']['ManufacturerData'][2409]
      print(ba)
      print(''.join('{:02x}'.format(x) for x in ba))
      print(ba[9] - 128)
      print(ba[8])
      print(ba[10])
      await asyncio.sleep(29)

asyncio.run(main())