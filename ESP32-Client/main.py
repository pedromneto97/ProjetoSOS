# Contribuição: Ariangelo Hauer Dias

from gc import collect

collect()

from connect import Connect
from machine import Pin, ADC, unique_id, reset, Timer, disable_irq, enable_irq, idle, RTC
from time import sleep, sleep_ms, localtime
from ntptime import settime
from client import Client
from pulseira import Pulseira


class Device:
    def __init__(self):
        self.c = Connect()
        self.connection = self.c.start()
        self.client = Client(self.connection)
        self.pulseira = Pulseira()

        # Alimentação
        self.p4 = Pin(4, Pin.OUT)
        self.p4.value(1)

        # Buzzer e LED
        self.p2 = Pin(2, Pin.OUT)  # LED
        self.p5 = Pin(5, Pin.OUT)  # BUZZER

        # Botão
        self.p15 = Pin(15, Pin.IN, Pin.PULL_DOWN)
        self.p15.irq(trigger=Pin.IRQ_RISING, handler=self.button)

        # Acelerômetro
        self.z = ADC(Pin(32))
        self.y = ADC(Pin(35))
        self.x = ADC(Pin(34))
        self.acelerometro()

        id = unique_id()
        self.hex_id = b'{:02x}{:02x}{:02x}{:02x}'.format(id[0], id[1], id[2], id[3])

    def acelerometro(self):
        self.x.width(ADC.WIDTH_10BIT)
        self.x.atten(ADC.ATTN_11DB)

        self.y.width(ADC.WIDTH_10BIT)
        self.y.atten(ADC.ATTN_11DB)

        self.z.width(ADC.WIDTH_10BIT)
        self.z.atten(ADC.ATTN_11DB)

        self.timer = Timer(0)
        self.timer.init(period=250, mode=Timer.PERIODIC, callback=self.verifica)

    def avisa(self):
        self.p2.value(1)
        self.p5.value(1)

    def desliga_aviso(self):
        self.p2.value(0)
        self.p5.value(0)

    # Função que verifica o acelerometro
    def verifica(self, p):
        xval = (self.x.read() - 462) / 105
        yval = (self.y.read() - 464) / 103
        zval = (self.z.read() - 474) / 102
        if abs(xval) > 2 or abs(yval) > 2 or abs(zval) > 2:
            self.avisa()
            sleep(2)
            self.desliga_aviso()
            resp = self.client.client(self.pulseira.config, "Emergência")
            if resp == False:
                self.avisa()
                sleep(7)
                self.desliga_aviso()

    # Alimenta o botão novamente
    def ativa(self, p):
        try:
            self.p4.value(1)
            p.deinit()
        except:
            reset()

    # Botão para chamar ajuda
    def button(self, p):
        try:
            irq = disable_irq()
            self.p4.value(0)
            enable_irq(irq)
            self.avisa()
            sleep(2)
            self.desliga_aviso()
            resp = self.client.client(self.pulseira.config, "Ajuda")
            if resp == False:
                self.avisa()
                sleep(7)
                self.desliga_aviso()
            t = Timer(-1)
            t.init(period=15000, mode=Timer.ONE_SHOT, callback=self.ativa)
        except:
            reset()


def main():
    device = Device()
    connected = device.connection.isconnected()
    boot = True

    while True:
        if not connected:
            connected = device.connection.isconnected()
        else:
            if boot:
                try:
                    settime()
                    l = localtime()
                    RTC().datetime(l[0:3] + (0,) + (l[3] - 3,) + l[4:6] + (0,))
                except:
                    pass
                print('Conectado como : {} - ID do dispositivo : {}'.format(device.connection.ifconfig()[0],
                                                                            device.hex_id))
                device.avisa()
                sleep_ms(700)
                device.desliga_aviso()
                boot = False
                break
    idle()


main()
