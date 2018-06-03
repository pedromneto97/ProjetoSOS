# Contribuição: Ariangelo Hauer Dias

import gc

import ntptime
import utime

gc.collect()

from connect import Connect
from machine import Pin, RTC, unique_id, I2C, disable_irq, enable_irq, Timer, reset
from server import Server
from ssd1306 import SSD1306_I2C


class Device:
    def __init__(self):
        # Lista
        self.lista = []
        self.iterador = 0

        # Timer que ativa o botão depois de 400ms
        self.t = Timer(-1)
        self.t.init(period=400, mode=Timer.PERIODIC, callback=self.ativa)

        # OLED
        self.oled = SSD1306_I2C(128, 64, I2C(sda=Pin(21), scl=Pin(22)))
        self.oled.fill(0)
        self.oled.text("Iniciando", 0, 32)
        self.oled.show()

        # Pino de alimentação
        self.p15 = Pin(15, Pin.OUT)
        self.p15.value(1)

        # Botão de próximo
        self.p2 = Pin(2, Pin.IN, Pin.PULL_DOWN)
        self.p2.irq(trigger=Pin.IRQ_RISING, handler=self.proximo)

        # Botão de remover
        self.p4 = Pin(4, Pin.IN, Pin.PULL_DOWN)
        self.p4.irq(trigger=Pin.IRQ_RISING, handler=self.remove)

        # Buzzer
        self.p5 = Pin(5, Pin.OUT)
        self.p5.value(0)

        self.c = Connect()
        self.connection = self.c.start()
        id = unique_id()
        self.rtc = ()
        self.hex_id = b'{:02x}{:02x}{:02x}{:02x}'.format(id[0], id[1], id[2], id[3])
        listHexId = [];
        listHexId.append(self.hex_id)

    def proximo(self, p):
        try:
            irq = disable_irq()
            if p.value() == 1:
                p.value(0)
            else:
                enable_irq(irq)
                return
            self.p15.value(0)
            if len(self.lista) > 0:
                if (self.iterador + 1) == len(self.lista):
                    self.iterador = 0
                else:
                    self.iterador = self.iterador + 1
                self.oled.fill(0)
                self.oled.text(self.lista[self.iterador]['tipo'], 0, 0)
                self.oled.text("Nome: " + self.lista[self.iterador]['nome'], 0, 20)
                self.oled.text("Quarto: " + self.lista[self.iterador]['quarto'], 0, 40)
                if len(self.lista) > 1:
                    self.oled.text("+", 110, 0)
                self.oled.show()
            else:
                self.oled.fill(0)
                self.oled.text("Nenhum pedido", 0, 32)
                self.oled.show()
            enable_irq(irq)
        except:
            reset()

    def remove(self, p):
        try:
            irq = disable_irq()
            if p.value() == 1:
                self.p15.value(0)
            else:
                enable_irq(irq)
                return
            print("Removendo")
            if len(self.lista) == 0:
                self.oled.fill(0)
                self.oled.text("Nenhum pedido", 0, 32)
                self.oled.show()
            elif len(self.lista) > 1:
                del self.lista[self.iterador]
                self.iterador = 0
                self.oled.fill(0)
                self.oled.text(self.lista[self.iterador]['tipo'], 0, 0)
                self.oled.text("Nome: " + self.lista[self.iterador]['nome'], 0, 20)
                self.oled.text("Quarto: " + self.lista[self.iterador]['quarto'], 0, 40)
                if len(self.lista) > 1:
                    self.oled.text("+", 110, 0)
                self.oled.show()
            else:
                del self.lista[0]
                self.oled.fill(0)
                self.oled.text("Nenhum pedido", 0, 32)
                self.oled.show()
            enable_irq(irq)
        except:
            reset()

    def ativa(self, p):
        if self.p15.value() == 0:
            self.p15.value(1)


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
