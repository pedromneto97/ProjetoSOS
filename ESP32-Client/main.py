# Contribuição: Ariangelo Hauer Dias

from gc import collect
from math import pow, sqrt
from os import remove, listdir
from time import sleep, sleep_ms, localtime

import ujson
from client import Client
from connect import Connect
from machine import Pin, ADC, unique_id, reset, Timer, disable_irq, enable_irq, idle, RTC
from ntptime import settime
from tipo import Tipo


class Device:
    def __init__(self):
        id = unique_id()
        self.hex_id = b'{:02x}{:02x}{:02x}{:02x}'.format(id[0], id[1], id[2], id[3])

        # Alimentação
        self.p4 = Pin(4, Pin.OUT)
        self.p4.value(1)

        # Buzzer e LED
        self.p2 = Pin(2, Pin.OUT)  # LED
        self.p5 = Pin(5, Pin.OUT)  # BUZZER

        # Deixa pré-definido para não reenviar, caso se conecte a rede, ativa o reenvio
        self.reenvio = True

        # Botão
        self.alimentacao = Timer(2)
        self.p15 = Pin(15, Pin.IN, Pin.PULL_DOWN)
        self.p15.irq(trigger=Pin.IRQ_RISING, handler=self.button)

        # Acelerômetro
        self.z = ADC(Pin(32))
        self.y = ADC(Pin(35))
        self.x = ADC(Pin(34))

        # Pino da bateria
        self.p33 = ADC(Pin(33))
        self.p33.width(ADC.WIDTH_10BIT)
        self.p33.atten(ADC.ATTN_11DB)

        # Timer da bateria
        self.bateria_timer = Timer(1)
        self.bateria_timer.init(period=1800000, mode=Timer.PERIODIC, callback=self.bateria)

        self.acelerometro()

        self.t_rede = Timer(-1)
        self.t_rede.init(period=300000, mode=Timer.PERIODIC, callback=self.reiniciar)

        self.c = Connect()
        self.connection = self.c.start()
        self.client = Client(self.connection)

        self.t_rede.deinit()

        self.t_reenvio = Timer(3)
        self.reenvio = False

    def acelerometro(self):
        self.x.width(ADC.WIDTH_10BIT)
        self.x.atten(ADC.ATTN_11DB)

        self.y.width(ADC.WIDTH_10BIT)
        self.y.atten(ADC.ATTN_11DB)

        self.z.width(ADC.WIDTH_10BIT)
        self.z.atten(ADC.ATTN_11DB)

        self.anterior = 0

        self.timer = Timer(0)
        self.timer.init(period=100, mode=Timer.PERIODIC, callback=self.verifica)

    def avisa(self):
        self.p2.value(1)
        self.p5.value(1)

    def desliga_aviso(self):
        self.p2.value(0)
        self.p5.value(0)

    def reiniciar(self, t):
        reset()

    # Função que verifica o acelerometro
    def verifica(self, p):
        xval = (self.x.read() - 464) / 102
        yval = (self.y.read() - 463) / 104
        zval = (self.z.read() - 475) / 99.3
        val = sqrt(pow(xval, 2) + pow(yval, 2) + pow(zval, 2))
        del xval
        del yval
        del zval
        if val > 3.5 or abs(val - self.anterior) > 1.3:
            self.avisa()
            sleep(2)
            self.desliga_aviso()
            try:
                hora = (RTC().datetime()[4], RTC().datetime()[5])
                self.client.client(mac=self.hex_id, tipo=Tipo.EMERGENCIA, hora=hora)
            except:
                self.avisa()
                sleep(7)
                self.desliga_aviso()
                try:
                    if not self.reenvio:
                        self.t_reenvio.init(period=300000, mode=Timer.PERIODIC, callback=self.reenviar)
                        self.reenvio = True
                except:
                    pass
        self.anterior = val
        del val

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
            self.alimentacao.init(period=17000, mode=Timer.ONE_SHOT, callback=self.ativa)
            enable_irq(irq)
            self.avisa()
            sleep(2)
            self.desliga_aviso()
            try:
                hora = (RTC().datetime()[4], RTC().datetime()[5])
                self.client.client(mac=self.hex_id, tipo=Tipo.AJUDA, hora=hora)
            except:
                self.avisa()
                sleep(7)
                self.desliga_aviso()
                try:
                    if not self.reenvio:
                        self.t_reenvio.init(period=300000, mode=Timer.PERIODIC, callback=self.reenviar)
                        self.reenvio = True
                except:
                    pass
        except:
            reset()

    def bateria(self, t):
        tensao = 2 * self.p33.read() * 3.3 / 1023
        if tensao < 3:
            self.avisa()
            sleep(2)
            self.desliga_aviso()
            try:
                hora = (RTC().datetime()[4], RTC().datetime()[5])
                self.client.client(mac=self.hex_id, tipo=Tipo.BATERIA, hora=hora)
            except:
                self.avisa()
                sleep(7)
                self.desliga_aviso()
                try:
                    if not self.reenvio:
                        self.t_reenvio.init(period=300000, mode=Timer.PERIODIC, callback=self.reenviar)
                        self.reenvio = True
                except:
                    pass

    def reenviar(self, t):
        try:
            print("Reenviando")
            f = open('estado.json', 'r')
            l = ujson.loads(f.read())
            f.close()
            for chave, valor in l.items():
                try:
                    self.client.client(mac=self.hex_id, tipo=valor['tipo'], hora=(valor['horas'], valor['minutos']),
                                       chamadas=valor['chamadas'])
                except:
                    raise
            try:
                t.deinit()
            except:
                pass
            self.reenvio = False
            try:
                remove('estado.json')
            except:
                print("Erro ao remover arquivo")
        except:
            print("Arquivo inexistente")


def main():
    device = Device()
    connected = device.connection.isconnected()
    boot = True

    while True:
        if not connected:
            connected = device.connection.isconnected()
            if not boot:
                print("Reconectando a rede")
                device.connection.start(False)
                device.t_rede.init(period=300000, mode=Timer.PERIODIC, callback=reset())
                boot = True
        else:
            if boot:
                try:
                    device.t_rede.deinit()
                except:
                    pass
                try:
                    settime()
                    l = localtime()
                    RTC().datetime(l[0:3] + (0,) + (l[3] - 3,) + l[4:6] + (0,))
                except:
                    pass
                device.avisa()
                sleep_ms(700)
                device.desliga_aviso()
                if 'estado.json' in listdir():
                    device.reenviar(device.t_reenvio)
                boot = False
            collect()
            idle()


main()
