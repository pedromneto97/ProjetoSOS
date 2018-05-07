#Contribuição: Ariangelo Hauer Dias

import ntptime
import utime
import sys
from gc import collect

collect()

from connect import Connect
from machine import Pin, ADC, RTC, unique_id, I2C, reset
from client import Client
from pulseira import Pulseira

class Device:
    def __init__(self):
        self.c = Connect()
        self.connection = self.c.start()
        id = unique_id() 
        self.rtc = ()
        self.hex_id = b'{:02x}{:02x}{:02x}{:02x}'.format(id[0], id[1], id[2], id[3])
        listHexId = [];
        listHexId.append(self.hex_id)


def main():
    device = Device()
    client = Client()
    connected = device.connection.isconnected()
    boot = True

    while True:
        if not connected:
            connected = device.connection.isconnected()
        else:
            if boot:
                print('Connected as : {} - Device id : {}'.format(device.connection.ifconfig()[0], device.hex_id))
                print('')
                timeout = 5
                setTime = False
                while not setTime and timeout > 0:
                    try:
                        ntp = ntptime.settime()
                        setTime = True
                    except:
                        utime.sleep(1)
                        timeout -= 1 
                
                boot = False 
                device.rtc = RTC()
            pulseira = Pulseira()
            client.client(pulseira.config)

if __name__== '__main__':
    main()
