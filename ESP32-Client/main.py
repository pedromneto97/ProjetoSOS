#Contribuição: Ariangelo Hauer Dias

import ntptime
import utime
import sys
from gc import collect

collect()

from connect import Connect
from machine import Pin, ADC, RTC, unique_id, I2C, reset
from time import sleep
from client import Client
from pulseira import Pulseira

class Device:
    def __init__(self):
        self.c = Connect()
        self.connection = self.c.start()
        self.client = Client(self.connection)
        self.pulseira = Pulseira()
        self.botao = Pin(15,Pin.IN,Pin.PULL_DOWN)
        self.botao.irq(trigger= Pin.IRQ_RISING, handler=self.pressionado)
        self.saida = Pin(14,Pin.OUT)
        self.botao.irq(trigger= Pin.IRQ_FALLING, handler=self.liberado)
        id = unique_id() 
        self.rtc = ()
        self.hex_id = b'{:02x}{:02x}{:02x}{:02x}'.format(id[0], id[1], id[2], id[3])
        listHexId = [];
        listHexId.append(self.hex_id)
    
    def pressionado(self, p):
        self.saida.value(1)
        self.client.client(self.pulseira.config)
    def liberado(self,p):
        self.saida.value(0)
        
    
def main():
    device = Device()
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
                break
    device.client.client(device.pulseira.config, 'Ajuda')

main()
