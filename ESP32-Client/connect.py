# Autor: Ariangelo Hauer Dias

import time

import dnsquery
import machine
import network
import ubinascii
import ujson


class Connect:
    def __init__(self):
        self.ap_if = network.WLAN(network.AP_IF)
        if self.ap_if.active():
            self.ap_if.active(False)
        self.sta_if = network.WLAN(network.STA_IF)
        try:
            print("Lendo configuração...")
            f = open('config.json', 'r')
            self.config = ujson.loads(f.read())
            self.lconf = len(self.config)
            f.close()
        except:
            print("Configuração não encontrada.")
            self.config = {}
            self.lconf = 0

    def connection(self, s, p, timeout=10):
        self.sta_if.connect(s, p)
        while not self.sta_if.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1

    def start(self):
        if not self.sta_if.isconnected():
            print('Tentando conectar...', end="")
            self.sta_if.active(True)
            i = 0
            while i < len(self.config) and not self.sta_if.isconnected():
                self.connection(ubinascii.a2b_base64(ubinascii.unhexlify(self.config[i][0])),
                                ubinascii.a2b_base64(ubinascii.unhexlify(self.config[i][1])))
                print(".", end="")
                time.sleep_ms(200)
                i += 1

        if not self.sta_if.isconnected():
            self.sta_if.active(False)
            print('Rede não conectada')
            d = dnsquery.start()
            self.connection(d[b's'].decode(), d[b'p'].decode())
            if self.sta_if.isconnected():
                self.config[self.lconf] = [ubinascii.hexlify(ubinascii.b2a_base64(d[b's'])[:-1]),
                                           ubinascii.hexlify(ubinascii.b2a_base64(d[b'p'])[:-1])]
                f = open('config.json', 'w')
                f.write(ujson.dumps(self.config))
                f.close()
                machine.reset()
            else:
                time.sleep(1)
                machine.reset()

        return self.sta_if
