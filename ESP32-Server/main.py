# Contribuição: Ariangelo Hauer Dias

import gc

import ntptime
import ujson
import utime

gc.collect()

from os import remove
from connect import Connect
from logo import escreve_SOS
from machine import Pin, RTC, unique_id, I2C, disable_irq, enable_irq, Timer, reset, ADC
from server import Server
from ssd1306 import SSD1306_I2C


class Device:
    def __init__(self):
        # TODO-me trabalhar o cadastro do novo dispositivo
        # Listas
        self.lista = {
            'emergencia': [],
            'ajuda': [],
            'bateria': []
        }
        self.iterador = 0
        # TODO-me fazer a leitura do arquivo de cadastrados
        self.cadastrados = {
            self.hex_id: {
                'nome': 'Transmissor',
                'quarto': None
            }
        }

        # Pino da bateria
        self.p33 = ADC(Pin(33))
        self.p33.width(ADC.WIDTH_12BIT)
        self.p33.atten(ADC.ATTN_11DB)

        # Pino de alimentação
        self.p15 = Pin(15, Pin.OUT)
        self.p15.value(1)

        # Timer que ativa o botão depois de 400ms
        self.t = Timer(-1)
        self.t.init(period=400, mode=Timer.PERIODIC, callback=self.ativa)

        # OLED
        self.oled = SSD1306_I2C(128, 64, I2C(sda=Pin(21), scl=Pin(22)))
        self.oled.fill(0)
        escreve_SOS(self.oled)
        self.oled.show()

        # Botão de próximo
        self.p2 = Pin(2, Pin.IN, Pin.PULL_DOWN)
        self.p2.irq(trigger=Pin.IRQ_RISING, handler=self.proximo)

        # Botão de remover
        self.p4 = Pin(4, Pin.IN, Pin.PULL_DOWN)
        self.p4.irq(trigger=Pin.IRQ_RISING, handler=self.remove)

        # TODO-me implementar scroll

        # Buzzer
        self.p19 = Pin(19, Pin.OUT)
        self.p19.value(0)

        self.c = Connect()
        self.connection = self.c.start()
        id = unique_id()
        self.rtc = ()
        self.hex_id = b'{:02x}{:02x}{:02x}{:02x}'.format(id[0], id[1], id[2], id[3])
        listHexId = [];
        listHexId.append(self.hex_id)

        # TODO-me implementar a leitura da bateria
        self.bateria_timer = Timer(1)
        self.bateria_timer.init(period=3600000, mode=Timer.PERIODIC, callback=self.bateria)

    def proximo(self, p):
        try:
            # TODO-me rever esta condicional
            irq = disable_irq()
            if p.value() == 1:
                p.value(0)
            else:
                enable_irq(irq)
                return
            self.p15.value(0)
            # TODO-me Atualizar como está sendo disponibilizado no vispor
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
            if len(self.lista) > 0:
                try:
                    f = open('estado.json', 'w')
                    f.write(ujson.dumps(self.lista))
                    f.close()
                except:
                    print("Erro ao salvar estado")
            reset()

    def remove(self, p):
        try:
            irq = disable_irq()
            if p.value() == 1:
                self.p15.value(0)
            else:
                enable_irq(irq)
                return
            # print("Removendo")
            # TODO-me Atualizar como está sendo disponibilizado no vispor
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
            if len(self.lista) > 0:
                try:
                    f = open('estado.json', 'w')
                    f.write(ujson.dumps(self.lista))
                    f.close()
                except:
                    print("Erro ao salvar estado")
            reset()

    def ativa(self, t):
        if self.p15.value() == 0:
            self.p15.value(1)

    def bateria(self, t):
        tensao = 2 * self.p33.read() * 3.6 / 4096
        if tensao < 3:
            self.lista['bateria'].append({
                'id': self.hex_id
                'hora':
            })


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
                device.oled.text("Conectado a rede", 0, 32)
                device.oled.show()
                timeout = 5
                setTime = False
                while not setTime and timeout > 0:
                    try:
                        ntp = ntptime.settime()
                        l = utime.localtime()
                        RTC().datetime(l[0:3] + (0,) + (l[3] - 3,) + l[4:6] + (0,))
                        setTime = True
                    except:
                        utime.sleep(1)
                        timeout -= 1

                boot = False
                device.rtc = RTC()
            s = Server(device.connection)
            # Try para verificar se existe um arquivo com o estado da última vez
            try:
                f = open('estado.json', 'r')
                device.lista = ujson.loads(f.read())
                f.close()
                device.oled.fill(0)
                device.oled.text(device.lista[device.iterador]['tipo'], 0, 0)
                device.oled.text("Nome: " + device.lista[device.iterador]['nome'], 0, 20)
                device.oled.text("Quarto: " + device.lista[device.iterador]['quarto'], 0, 40)
                if len(device.lista) > 1:
                    device.oled.text("+", 110, 0)
                device.oled.show()
                remove("estado.json")
            except:
                device.oled.fill(0)
                device.oled.text("Nenhum pedido", 0, 32)
                device.oled.show()
            s.servidor(device)


if __name__ == '__main__':
    main()
