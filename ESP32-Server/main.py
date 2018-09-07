# Contribuição: Ariangelo Hauer Dias

from os import remove

import ujson
import utime
from connect import Connect
from logo import escreve_SOS
from machine import Pin, RTC, unique_id, I2C, disable_irq, enable_irq, Timer, reset, ADC
from ntptime import settime
from ssd1306 import SSD1306_I2C
from tipo import Tipo

from server import Server


class Device:
    def __init__(self):
        id = unique_id()
        self.hex_id = b'{:02x}{:02x}{:02x}{:02x}'.format(id[0], id[1], id[2], id[3])

        # TODO-me trabalhar o cadastro do novo dispositivo
        # Listas
        self.lista = {
            Tipo.EMERGENCIA: [],
            Tipo.AJUDA: [],
            Tipo.BATERIA: []
        }
        self.iterador = {
            'tipo': Tipo.EMERGENCIA,
            'iterador': -1
        }
        # TODO-me testar a leitura do arquivo de cadastrados
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

        # TODO-me testar a leitura da bateria
        self.bateria_timer = Timer(1)
        self.bateria_timer.init(period=3600000, mode=Timer.PERIODIC, callback=self.bateria)

        # TODO-me testar timer de inatividade
        self.inatividade = Timer(2)
        self.inatividade.init(period=300000, mode=Timer.ONE_SHOT, callback=self.inativo)

    def reinicia_inativo(self):
        self.oled.poweron()
        self.inatividade.deinit()
        self.inatividade.init(period=300000, mode=Timer.ONE_SHOT, callback=self.inativo)

    def proximo(self, p):
        try:
            irq = disable_irq()
            if p.value() == 1:
                self.p15.value(0)
            else:
                enable_irq(irq)
                return
            self.reinicia_inativo()
            # TODO-me Verificar como está sendo disponibilizado no visor
            contador = 0
            self.oled.fill(0)
            for chave, valor in self.lista.items():
                contador += len(valor)
            if contador == 0:
                self.oled.text("Nenhum pedido", 0, 32)
            elif len(self.lista[self.iterador['tipo']]) >= self.iterador['iterador'] + 1:
                if self.iterador['tipo'] == Tipo.BATERIA:
                    for chave, valor in self.lista.items():
                        if len(valor) > 0:
                            self.iterador['tipo'] = chave
                            break
                else:
                    if self.iterador['tipo'] == Tipo.EMERGENCIA:
                        if len(self.lista[Tipo.AJUDA]) > 0:
                            self.iterador['tipo'] = Tipo.AJUDA
                        elif len(self.lista[Tipo.BATERIA]) > 0:
                            self.iterador['tipo'] = Tipo.BATERIA
                    elif self.iterador['tipo'] == Tipo.AJUDA:
                        if len(self.lista[Tipo.BATERIA]) > 0:
                            self.iterador['tipo'] = Tipo.BATERIA
                        elif len(self.lista[Tipo.EMERGENCIA]) > 0:
                            self.iterador['tipo'] = Tipo.EMERGENCIA
                self.iterador['iterador'] = 0
            else:
                self.iterador['iterador'] += 1
            if contador > 0:
                self.oled.text(self.iterador['tipo'], 0, 0)
                self.oled.text(
                    "Nome: " + self.cadastrados[self.lista[self.iterador['tipo']][self.iterador['iterador']]['id']][
                        'nome'], 0, 20)
                self.oled.text(
                    "Quarto: " + self.cadastrados[self.lista[self.iterador['tipo']][self.iterador['iterador']]['id']][
                        'quarto'], 0, 40)
                self.oled.text(
                    "Horario: " + self.lista[self.iterador['tipo']][self.iterador['iterador']]['horas'] + ':' +
                    self.lista[self.iterador['tipo']][self.iterador['iterador']]['minutos'], 0,
                    60)
                self.oled.text(self.lista[self.iterador['tipo']][self.iterador['iterador']]['chamadas'], 110, 60)
                if contador > 1:
                    self.oled.text("+", 110, 0)
            self.oled.show()
            enable_irq(irq)
        except:
            if len(self.lista[Tipo.EMERGENCIA]) > 0 or len(self.lista[Tipo.AJUDA]) > 0 or len(
                    self.lista[Tipo.BATERIA]) > 0:
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
            self.reinicia_inativo()
            # TODO-me Verificar como está sendo disponibilizado no visor
            self.oled.fill(0)
            contador = 0
            if len(self.lista['emergencia']) == 0 and len(self.lista['ajuda']) == 0 and len(self.lista['bateria']) == 0:
                self.oled.text("Nenhum pedido", 0, 32)
            elif len(self.lista[self.iterador['tipo']]) > 1:
                del self.lista[self.iterador['tipo']][self.iterador['iterador']]
                if len(self.lista[self.iterador['tipo']]) == self.iterador['iterador']:
                    self.iterador = {
                        'tipo': 'emergencia',
                        'iterador': 0
                    }
                self.oled.text(self.iterador['tipo'], 0, 0)
                self.oled.text(
                    "Nome: " + self.cadastrados[self.lista[self.iterador['tipo']][self.iterador['iterador']]['id']][
                        'nome'], 0, 20)
                self.oled.text(
                    "Quarto: " + self.cadastrados[self.lista[self.iterador['tipo']][self.iterador['iterador']]['id']][
                        'quarto'], 0, 40)
                self.oled.text(
                    "Horario: " + self.lista[self.iterador['tipo']][self.iterador['iterador']]['horas'] + ':' +
                    self.lista[self.iterador['tipo']][self.iterador['iterador']]['minutos'], 0,
                    60)
                self.oled.text(self.lista[self.iterador['tipo']][self.iterador['iterador']]['chamadas'], 110, 60)
                for chave, valor in self.lista.items():
                    contador += len(valor)
            else:
                del self.lista[self.iterador['tipo']]
                for chave, valor in self.lista.items():
                    if chave == self.iterador['tipo']:
                        continue
                    if len(valor) > 0:
                        contador += len(valor)
                        if contador > 0:
                            break
                        self.iterador = {
                            'tipo': chave,
                            'iterador': 0
                        }
                        self.oled.text(chave, 0, 0)
                        self.oled.text("Nome: " + self.cadastrados[valor[0]['id']]['nome'], 0, 20)
                        self.oled.text("Quarto: " + self.cadastrados[valor[0]['id']]['quarto'], 0, 40)
                        self.oled.text(
                            "Horario: " + valor[0]['horas'] + ':' + valor[0]['minutos'], 0,
                            60)
                        self.oled.text(valor[0]['chamadas'], 110, 60)
            if contador == 0:
                self.oled.text("Nenhum pedido", 0, 32)
            elif contador > 1:
                self.oled.text("+", 110, 0)
            self.oled.show()
            enable_irq(irq)
        except:
            if len(self.lista[Tipo.EMERGENCIA]) > 0 or len(self.lista[Tipo.AJUDA]) > 0 or len(
                    self.lista[Tipo.BATERIA]) > 0:
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
            self.avisa()
            utime.sleep(1)
            for item in self.lista[Tipo.BATERIA]:
                if item['id'] == self.hex_id:
                    item['chamadas'] += 1
                else:
                    self.lista[Tipo.BATERIA].append({
                        'id': self.hex_id,
                        'hora': RTC().datetime()[4],
                        'minuto': RTC().datetime()[5],
                        'chamadas': 1
                    })
            self.desliga_aviso()

    def inativo(self, t):
        t.deinit()
        self.oled.poweroff()

    def avisa(self):
        self.p19.value(1)

    def desliga_aviso(self):
        self.p19.value(0)


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
                    l = utime.localtime()
                    RTC().datetime(l[0:3] + (0,) + (l[3] - 3,) + l[4:6] + (0,))
                except:
                    pass
                device.oled.fill(0)
                device.oled.text("Conectado a rede", 0, 32)
                device.oled.show()
                boot = False
                # Try para carregar todos os cadastros
                try:
                    f = open('cadastros.json', 'r')
                    device.cadastrados.update(ujson.loads(f.read()))
                    f.close()
                except:
                    device.oled.fill(0)
                    device.oled.text("Nao ha dados", 0, 32)
                    device.oled.text("cadastrados", 0, 40)
                    device.oled.show()

                # Try para verificar se existe um arquivo com o estado da última vez
                try:
                    f = open('estado.json', 'r')
                    device.lista = ujson.loads(f.read())
                    f.close()
                    device.proximo(device.p15)
                    remove("estado.json")
                except:
                    device.oled.fill(0)
                    device.oled.text("Nenhum pedido", 0, 32)
                    device.oled.show()
                s = Server(device.connection)
            s.servidor(device)


if __name__ == '__main__':
    main()
