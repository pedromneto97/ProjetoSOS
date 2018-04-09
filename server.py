import network
import socket


class Server:
    station = network.WLAN(network.STA_IF)
    ssid = "Pedro"
    password = "12345678"

    def __init__(self):
        self.conectar()

    def conectar(self):
        if (self.station.isconnected):
            print("Conectado")
            return
        self.station.active(True)
        self.station.connect(self.ssid, self.password)
        while self.station.isconnected() == False:
            print("Não conectado")
            pass

    def servidor(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(self.station.ifconfig())
        server.bind((self.station.ifconfig()[0], 5002))
        server.listen(1)
        conn, addr = server.accept()
        server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        print( 'Connected by' + addr)