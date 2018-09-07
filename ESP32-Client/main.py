# Contribuição: Ariangelo Hauer Dias

from gc import collect
from math import pow, sqrt
from time import sleep, sleep_ms, localtime

from client import Client
from connect import Connect
from machine import Pin, ADC, unique_id, reset, Timer, disable_irq, enable_irq, idle, RTC
from ntptime import settime
from tipo import Tipo


class Device:
    def __init__(self):
        id = unique_id()
        self.hex_id = b'{:02x}{:02x}{:02x}{:02x}'.format(id[0], id[1], id[2], id[3])

        self.c = Connect()
        self.connection = self.c.start()
        self.client = Client(self.connection)

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

        # TODO-me implementar a leitura da bateria

        # TODO-me testar a leitura da bateria
        # Pino da bateria
        self.p33 = ADC(Pin(33))
        self.p33.width(ADC.WIDTH_12BIT)
        self.p33.atten(ADC.ATTN_11DB)

        # Timer da bateria
        self.bateria_timer = Timer(1)
        self.bateria_timer.init(period=3600000, mode=Timer.PERIODIC, callback=self.bateria)

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
        xval = (self.x.read() - 464) / 102
        yval = (self.y.read() - 463) / 104
        zval = (self.z.read() - 475) / 99.3
        if sqrt(pow(xval, 2) + pow(yval, 2) + pow(zval, 2)) > 2:
            self.avisa()
            sleep(2)
            self.desliga_aviso()
            hora = (RTC().datetime()[4], RTC().datetime()[5])
            resp = self.client.client(mac=self.hex_id, tipo=Tipo.EMERGENCIA, hora=hora)
            if not resp:
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
            if p.value() == 1:
                self.p4.value(0)
            else:
                enable_irq(irq)
                return
            enable_irq(irq)
            self.avisa()
            sleep(2)
            self.desliga_aviso()
            hora = (RTC().datetime()[4], RTC().datetime()[5])
            resp = self.client.client(mac=self.hex_id, tipo=Tipo.AJUDA, hora=hora)
            if not resp:
                self.avisa()
                sleep(7)
                self.desliga_aviso()
            t = Timer(-1)
            t.init(period=15000, mode=Timer.ONE_SHOT, callback=self.ativa)
        except:
            reset()

    def bateria(self, t):
        tensao = 2 * self.p33.read() * 3.6 / 4096
        if tensao < 3:
            self.avisa()
            sleep(2)
            self.desliga_aviso()
            hora = (RTC().datetime()[4], RTC().datetime()[5])
            resp = self.client.client(mac=self.hex_id, tipo=Tipo.BATERIA, hora=hora)
            if not resp:
                self.avisa()
                sleep(7)
                self.desliga_aviso()


def main():
    device = Device()
    connected = device.connection.isconnected()
    boot = True

    while True:
        if not connected:
            connected = device.connection.isconnected()
        else:
            if boot:
                # TODO-me timer para verificar caso caia a rede, se reconectar
                try:
                    settime()
                    l = localtime()
                    RTC().datetime(l[0:3] + (0,) + (l[3] - 3,) + l[4:6] + (0,))
                except:
                    pass
                device.avisa()
                sleep_ms(700)
                device.desliga_aviso()
                boot = False
            collect()
            idle()

main()
