import network
from time import sleep
import socket


class Server:
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

    def servidor(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        confs = self.station.ifconfig()
        aux = confs[0].split('.')
        ip = str(aux[0]) + '.'+ str(aux[1]) +'.'+str(aux[2])+'.'+str(25)
        self.station.ifconfig((ip, confs[1], confs[2], confs[3]))
        confs = None
        aux = None
        ip = None
        server.bind(('192.168.1.25', 5000))
        server.listen(1)
        print("Esperando:\n")
        conn, addr = server.accept()
        print('Connected by' + str(addr))
        while True:
            msg = conn.recv(1024)
            if not msg or (msg is 'sair'):
                break
            print(addr, msg.decode('utf-8'), end='\n')
        msg = "Sucesso"
        conn.send(msg.encode('utf-8'))
        print("Finalizando")
        conn.close()
