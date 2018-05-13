#Contribuição: Ariangelo Hauer Dias

import ntptime
import utime
import sys
from gc import collect

collect()

from connect import Connect
from machine import Pin, ADC, RTC, unique_id, I2C, reset, Timer
from time import sleep
from client import Client
from pulseira import Pulseira

class Device:
    def __init__(self):

        self.c = Connect()
        self.connection = self.c.start()
        self.client = Client(self.connection)
        self.pulseira = Pulseira()

        self.p4 = Pin(4, Pin.OUT)
        self.p4.value(1)
        self.p2 = Pin(2, Pin.OUT)
        self.p15 = Pin(15, Pin.IN, Pin.PULL_DOWN)
        self.p15.irq(trigger=Pin.IRQ_RISING, handler=self.button)

        id = unique_id() 
        self.rtc = ()
        self.hex_id = b'{:02x}{:02x}{:02x}{:02x}'.format(id[0], id[1], id[2], id[3])
        listHexId = [];
        listHexId.append(self.hex_id)

    def ativa(self, p):
        self.p4.value(1)
        p.deinit()

    def button(self,p):
        self.desativa_botao()
        self.p2.value(1)
        sleep(2)
        self.p2.value(0)
        self.client.client(self.pulseira.config, "Ajuda")

    def desativa_botao(self):
        self.p4.value(0)
        t = Timer(-1)
        t.init(period=15000, mode=Timer.ONE_SHOT, callback= self.ativa)
        
    
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

main()
