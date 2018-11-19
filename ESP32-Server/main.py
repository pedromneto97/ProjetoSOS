# Contribuição: Ariangelo Hauer Dias

from os import remove

import cadastro
import ntptime
import ujson
import utime
from connect import Connect
from logo import escreve_SOS
from machine import Pin, RTC, unique_id, I2C, disable_irq, enable_irq, Timer, reset, ADC, SOFT_RESET, reset_cause
from server import Server
from ssd1306 import SSD1306_I2C
from tipo import Tipo


class Device:
    def __init__(self):
        id = unique_id()
        self.hex_id = b'{:02x}{:02x}{:02x}{:02x}'.format(id[0], id[1], id[2], id[3])

        # Listas
        self.lista = {
            Tipo.EMERGENCIA: [],
            Tipo.AJUDA: [],
            Tipo.BATERIA: []
        }
        self.iterador = {
            'tipo': Tipo.EMERGENCIA,
            'tamanho': {
                Tipo.EMERGENCIA: 0,
                Tipo.AJUDA: 0,
                Tipo.BATERIA: 0,
                'total': 0
            },
            'iterador': -1
        }

        self.cadastrados = {
            self.hex_id: {
                'nome': 'Receptor',
                'quarto': None
            }
        }

        # Pino da bateria
        self.p33 = ADC(Pin(33))
        self.p33.width(ADC.WIDTH_10BIT)
        self.p33.atten(ADC.ATTN_11DB)

        # Pino de alimentação
        self.p15 = Pin(15, Pin.OUT)
        self.p15.value(1)

        # Botão de remover
        self.p4 = Pin(4, Pin.IN, Pin.PULL_DOWN)

        # Timer que ativa o botão depois de 400ms
        self.t = Timer(0)
        self.t.init(period=400, mode=Timer.PERIODIC, callback=self.ativa)

        # OLED
        self.oled = SSD1306_I2C(128, 64, I2C(sda=Pin(21), scl=Pin(22)))
        self.oled.fill(0)
        escreve_SOS(self.oled)
        self.oled.show()

        try:
            f = open('estado.json', 'r')
            l = ujson.loads(f.read())
            print(l)
            self.lista[Tipo.EMERGENCIA] = l[Tipo.EMERGENCIA]
            self.iterador['tamanho'][Tipo.EMERGENCIA] = len(l[Tipo.EMERGENCIA])
            self.lista[Tipo.AJUDA] = l[Tipo.AJUDA]
            self.iterador['tamanho'][Tipo.AJUDA] = len(l[Tipo.AJUDA])
            self.lista[Tipo.BATERIA] = l[Tipo.BATERIA]
            self.iterador['tamanho'][Tipo.BATERIA] = len(l[Tipo.BATERIA])
            self.iterador['tamanho']['total'] = len(l[Tipo.BATERIA]) + len(l[Tipo.AJUDA]) + len(l[Tipo.EMERGENCIA])
            f.close()
            remove("estado.json")
        except:
            pass

        self.bateria_timer = Timer(1)
        self.bateria_timer.init(period=1800000, mode=Timer.PERIODIC, callback=self.bateria)

        # Buzzer
        self.p19 = Pin(19, Pin.OUT)
        self.p19.value(0)

        self.t_boot = Timer(2)
        self.t_boot.init(period=300000, mode=Timer.ONE_SHOT, callback=self.reiniciar)
        self.c = Connect()
        self.connection = self.c.start()
        self.t_boot.deinit()

        self.server = Server(self.connection)

        self.carregar_cadastros()

        while self.p4.value() == 0 and reset_cause() != SOFT_RESET:
            self.t_boot.init(period=120000, mode=Timer.ONE_SHOT, callback=self.reiniciar)
            self.oled.fill(0)
            self.oled.text("CADASTRO", 0, 32)
            self.oled.show()
            mac = self.server.servidor(device=self, cadastro=True)
            self.connection.active(False)
            self.oled.fill(0)
            self.oled.text("ID:", 0, 20)
            self.oled.text(mac, 0, 32)
            self.oled.show()
            dados = cadastro.start(mac)
            self.escreve_oled(nome=dados[b'nome'].decode(), quarto=dados[b'quarto'].decode())
            self.cadastrados.update({
                mac: {
                    'nome': dados[b'nome'].decode(),
                    'quarto': dados[b'quarto'].decode()
                }
            })
            self.connection = self.c.start()
            utime.sleep(1)
        try:
            self.t_boot.deinit
        except:
            pass
        # Botão de próximo
        self.p2 = Pin(2, Pin.IN, Pin.PULL_DOWN)
        self.p2.irq(trigger=Pin.IRQ_RISING, handler=self.proximo)

        # IRQ de remover
        self.p4.irq(trigger=Pin.IRQ_RISING, handler=self.remove)

        self.inatividade = Timer(2)
        self.inatividade.init(period=300000, mode=Timer.ONE_SHOT, callback=self.inativo)

    def reinicia_inativo(self):
        self.oled.poweron()
        self.inatividade.deinit()
        self.inatividade.init(period=300000, mode=Timer.ONE_SHOT, callback=self.inativo)

    def reiniciar(self, t):
        reset()

    def carregar_cadastros(self):
        # Try para carregar todos os cadastros
        try:
            f = open('cadastros.json', 'r')
            self.cadastrados.update(ujson.loads(f.read()))
            f.close()
        except:
            self.oled.fill(0)
            self.oled.text("Nao ha dados", 0, 32)
            self.oled.text("cadastrados", 0, 40)
            self.oled.show()

    def proximo(self, p=None, flag=True):
        try:
            irq = disable_irq()
            if flag:
                if p.value() == 1:
                    self.p15.value(0)
                else:
                    enable_irq(irq)
                    return
            enable_irq(irq)
            self.reinicia_inativo()
            contador = 0
            self.oled.fill(0)
            for chave, valor in self.lista.items():
                contador += len(valor)
            if contador == 0:
                self.oled.text("Nenhum pedido", 0, 32)
                self.oled.show()
            elif len(self.lista[self.iterador['tipo']]) <= self.iterador['iterador'] + 1:
                # Verifica para cada tipo, para evitar problemas se o iterador tivesse no meio
                # então foi feito caso a caso FOcando na prioridade
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
                elif self.iterador['tipo'] == Tipo.BATERIA:
                    if len(self.lista[Tipo.EMERGENCIA]) > 0:
                        self.iterador['tipo'] = Tipo.EMERGENCIA
                    elif len(self.lista[Tipo.AJUDA]) > 0:
                        self.iterador['tipo'] = Tipo.AJUDA
                self.iterador['iterador'] = 0
            else:
                self.iterador['iterador'] += 1
            if contador > 0:
                tipo = self.iterador['tipo']
                nome = self.cadastrados[self.lista[self.iterador['tipo']][self.iterador['iterador']]['id']]['nome']
                quarto = self.cadastrados[self.lista[self.iterador['tipo']][self.iterador['iterador']]['id']]['quarto']
                hora = self.lista[self.iterador['tipo']][self.iterador['iterador']]['horas']
                minuto = self.lista[self.iterador['tipo']][self.iterador['iterador']]['minutos']
                chamadas = self.lista[self.iterador['tipo']][self.iterador['iterador']]['chamadas']
                self.escreve_oled(tipo=tipo, nome=nome, quarto=quarto, hora=hora, minuto=minuto, chamadas=chamadas,
                                  posicao=True)
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
            enable_irq(irq)
            self.reinicia_inativo()
            self.oled.fill(0)
            contador = 0
            tipo = None
            nome = None
            quarto = None
            chamadas = None
            hora = None
            minuto = None
            # Caso não tenha nada na lista
            if len(self.lista[Tipo.EMERGENCIA]) == 0 and len(self.lista[Tipo.AJUDA]) == 0 and len(
                    self.lista[Tipo.BATERIA]) == 0:
                self.oled.text("Nenhum pedido", 0, 32)
                self.oled.show()
            # Caso na minha lista atual tenha mais de 2 elementos
            elif len(self.lista[self.iterador['tipo']]) > 1:
                del self.lista[self.iterador['tipo']][self.iterador['iterador']]
                self.altera_tamanho(self.iterador['tipo'])
                # Caso for o último elemento da lista, muda pra próxima lista com a prioridade
                if len(self.lista[self.iterador['tipo']]) == self.iterador['iterador']:
                    if len(self.lista[Tipo.EMERGENCIA]) > 0:
                        self.iterador['tipo'] = Tipo.EMERGENCIA
                        self.iterador['iterador'] = 0
                    elif len(self.lista[Tipo.AJUDA]) > 0:
                        self.iterador['tipo'] = Tipo.AJUDA
                        self.iterador['iterador'] = 0
                    elif len(self.lista[Tipo.BATERIA]) > 0:
                        self.iterador['tipo'] = Tipo.BATERIA
                        self.iterador['iterador'] = 0
                tipo = self.iterador['tipo']
                nome = self.cadastrados[self.lista[self.iterador['tipo']][self.iterador['iterador']]['id']]['nome']
                quarto = self.cadastrados[self.lista[self.iterador['tipo']][self.iterador['iterador']]['id']]['quarto']
                hora = self.lista[self.iterador['tipo']][self.iterador['iterador']]['horas']
                minuto = self.lista[self.iterador['tipo']][self.iterador['iterador']]['minutos']
                chamadas = self.lista[self.iterador['tipo']][self.iterador['iterador']]['chamadas']
                for chave, valor in self.lista.items():
                    contador += len(valor)
            else:
                del self.lista[self.iterador['tipo']][self.iterador['iterador']]
                self.altera_tamanho(self.iterador['tipo'])
                for chave, valor in self.lista.items():
                    if chave == self.iterador['tipo']:
                        continue
                    if contador > 0 and len(valor) > 0:
                        contador += len(valor)
                    elif len(valor) > 0:
                        contador += len(valor)
                        self.iterador['tipo'] = chave
                        self.iterador['iterador'] = 0
                        tipo = chave
                        nome = self.cadastrados[valor[0]['id']]['nome']
                        quarto = self.cadastrados[valor[0]['id']]['quarto']
                        hora = valor[0]['horas']
                        minuto = valor[0]['minutos']
                        chamadas = valor[0]['chamadas']
            if contador == 0:
                self.oled.text("Nenhum pedido", 0, 32)
                self.oled.show()
            else:
                self.escreve_oled(tipo=tipo, nome=nome, quarto=quarto, hora=hora, minuto=minuto, chamadas=chamadas,
                                  posicao=True)
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
        tensao = 2 * self.p33.read() * 3.3 / 1023
        if tensao < 3:
            self.avisa()
            utime.sleep(1)
            hora = 0
            minuto = 0
            chamadas = 0
            flag = True
            for item in self.lista[Tipo.BATERIA]:
                if item['id'] == self.hex_id:
                    item['chamadas'] += 1
                    chamadas = item['chamadas']
                    hora = item['horas']
                    minuto = item['minutos']
                    flag = False
            if flag:
                hora = RTC().datetime()[4]
                minuto = RTC().datetime()[5]
                chamadas = 1
                self.lista[Tipo.BATERIA].append({
                    'id': self.hex_id,
                    'horas': hora,
                    'minutos': minuto,
                    'chamadas': 1
                })
            i = next(i for i, valor in enumerate(self.lista[Tipo.BATERIA]) if valor['id'] == self.hex_id)
            self.iterador['tipo'] = Tipo.BATERIA
            self.iterador['iterador'] = i
            self.escreve_oled(tipo=Tipo.BATERIA, nome=self.cadastrados[self.hex_id]['nome'], hora=hora, minuto=minuto,
                              chamadas=chamadas, posicao=True)
            self.reinicia_inativo()
            self.desliga_aviso()

    def escreve_oled(self, tipo=None, nome=None, quarto=None, hora=None, minuto=None, chamadas=None, scroll=False,
                     rm=False, posicao=False):
        self.oled.fill(0)
        if not scroll:
            if not (tipo is None):
                self.oled.text(tipo, 0, 0)
            if not (nome is None):
                self.oled.text("Nome: " + nome, 0, 10)
            if not (quarto is None):
                self.oled.text("Quarto: " + str(quarto), 0, 20)
            if not (hora is None) or not (minuto is None):
                self.oled.text("Horario: {:02d}:{:02d}".format(hora, minuto), 0, 30)
            if not (chamadas is None):
                self.oled.text(str(chamadas), 110, 55)
            if posicao:
                self.oled.text(
                    "{:02d}".format(self.posicao_absoluta()) + "/" + "{:02d}".format(self.iterador['tamanho']['total']),
                    88, 0)
            self.oled.show()
        else:
            if rm:
                pass
                # Scroll para a direita
            else:
                pass
                # Scroll para baixo

    def inativo(self, t):
        t.deinit()
        self.oled.poweroff()

    def avisa(self):
        self.p19.value(1)

    def desliga_aviso(self):
        self.p19.value(0)

    # Incrementa ou decrementa o tamanho da lista
    def altera_tamanho(self, tipo, incrementa=False):
        if incrementa:
            self.iterador['tamanho'][tipo] += 1
            self.iterador['tamanho']['total'] += 1
        else:
            self.iterador['tamanho'][tipo] -= 1
            self.iterador['tamanho']['total'] -= 1

    # Função que busca a posição real de determinado iterador  na lista
    def posicao_absoluta(self):
        if self.iterador['tipo'] == Tipo.EMERGENCIA:
            return self.iterador['iterador'] + 1
        elif self.iterador['tipo'] == Tipo.AJUDA:
            return self.iterador['tamanho'][Tipo.EMERGENCIA] + self.iterador['iterador'] + 1
        elif self.iterador['tipo'] == Tipo.BATERIA:
            return self.iterador['tamanho'][Tipo.EMERGENCIA] + self.iterador['tamanho'][
                Tipo.AJUDA] + self.iterador['iterador'] + 1

    def ordenar(self):
        for chave, valor in self.lista.items():
            valor.sort(key=lambda x: [x['horas'], x['minutos']])


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
                    ntptime.settime()
                    l = utime.localtime()
                    if l[3] < 3:
                        l[3] = 21 + l[3]
                    RTC().datetime(l[0:3] + (0,) + (l[3] - 3,) + l[4:6] + (0,))
                except:
                    pass
                device.oled.fill(0)
                device.oled.text("Conectado a rede", 0, 32)
                device.oled.show()
                boot = False
                # Try para verificar se existe um arquivo com o estado da última vez
                if device.iterador['tamanho']['total'] > 0:
                    device.proximo(flag=False)
                else:
                    device.oled.fill(0)
                    device.oled.text("Nenhum pedido", 0, 32)
                    device.oled.show()
            device.server.servidor(device)


if __name__ == '__main__':
    main()
