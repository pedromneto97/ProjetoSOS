import network
from time import sleep
import socket


class Client:
    station = network.WLAN(network.STA_IF)
    ssid = "Pedro e Roberto"
    password = "P3dr03r0b3rt0"

    def __init__(self):
        self.conectar()

    def conectar(self):
        if (self.station.isconnected()):
            print("Conectado")
            return
        self.station.active(True)
        self.station.connect(self.ssid, self.password)
        while self.station.isconnected() == False:
            print("Não conectado")
            sleep(2)
            pass
        print("Conectado")

    def client(self):
        while self.station.status() != 5:
            pass
        HOST = '0.0.0.0'  # Endereco IP do Servidor
        PORT = 8266  # Porta que o Servidor esta
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dest = (HOST, PORT)
        tcp.connect(dest)
        print('Para sair use CTRL+X\n')
        msg = input()
        while True:
            tcp.send(msg.encode('utf-8'))
            if msg is 'sair':
                break
            msg = input()
        msg = tcp.recv(1024)
        print(msg.decode('utf-8'))
        tcp.close()
