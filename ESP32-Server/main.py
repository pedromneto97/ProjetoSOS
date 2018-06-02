# Contribuição: Ariangelo Hauer Dias

import gc

import ntptime
import utime

gc.collect()

from connect import Connect
from machine import Pin, RTC, unique_id, I2C
from server import Server
from ssd1306 import SSD1306_I2C

class Device:
    def __init__(self):
        self.lista = []
        self.oled = SSD1306_I2C(128, 64, I2C(sda=Pin(21), scl=Pin(22)))
        self.oled.fill(0)
        self.oled.text("Iniciando", 0, 32)
        self.oled.show()
        self.c = Connect()
        self.connection = self.c.start()
        id = unique_id()
        self.rtc = ()
        self.hex_id = b'{:02x}{:02x}{:02x}{:02x}'.format(id[0], id[1], id[2], id[3])
        listHexId = [];
        listHexId.append(self.hex_id)


def main():
    device = Device()
    connected = device.connection.isconnected()
    boot = True

    while True:
        if not connected:
            connected = device.connection.isconnected()
        else:
            if boot:
                device.oled.fill(0)
                device.oled.text("Conectado ao WiFi", 0, 32)
                device.oled.show()
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
            s = Server(device.connection)
            device.oled.fill(0)
            device.oled.text("Nenhum pedido", 0, 32)
            device.oled.show()
            s.servidor(device)


if __name__ == '__main__':
    main()
