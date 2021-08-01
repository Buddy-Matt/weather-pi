# weather-pi
Weatherstation with UDP server for "Digoo DG-EX001" and MQTT integration

Based on reverse engineering done by Mr Łukasz Kalamłacki: http://kalamlacki.eu/sp73.php and further detailed by @matjon https://github.com/matjon/em3371-controller/blob/main/Documentation/device_protocol.md

Should work with any EMAX EM3371 rebranded weasther station

## Aim

To build a weatehrstation app for a Raspberry PI utlisiing:

1. Data supplied from a "Digoo DG-EX001" budget WiFi weather station
2. Additional data from BMD180/DHT/BH1750 sensors

With the following features:

1. Display output for non-headless setups
2. MQTT integration to supply data to Homeassistant

## Current status

* Listens for UDP packets from the Digoo unit (Sent via DNS override of the default SMARTSERVER.EMAXTIME.CN server address)
* Deciphers data and displays to screen via terminal

