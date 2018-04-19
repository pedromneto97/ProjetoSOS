# import network
import socket


class Client:
    # station = network.WLAN(network.STA_IF)
    ssid = "Pedro"
    password = "12345678"

    # def __init__(self):
    #     self.conectar()
    #
    # def conectar(self):
    #     if (self.station.isconnected):
    #         print("Conectado")
    #         return
    #     self.station.active(True)
    #     self.station.connect(self.ssid, self.password)
    #     while self.station.isconnected() == False:
    #         print("Não conectado")
    #         pass

    def client(self):
        HOST = '127.0.0.1'  # Endereco IP do Servidor
        PORT = 5003  # Porta que o Servidor esta
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dest = (HOST, PORT)
        tcp.connect(dest)
        print('Para sair use CTRL+X\n')
        msg = input()
        while msg != 'sair':
            tcp.send(msg.encode('utf-8'))
            msg = input()
        msg = tcp.recv(1024)
        print(msg.decode('utf-8'))
        tcp.close()
