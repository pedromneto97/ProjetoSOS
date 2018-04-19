import network
import socket


class Server:
    # station = network.WLAN(network.STA_IF)
    ssid = "Pedro"
    password = "12345678"

    # def __init__(self):
    # self.conectar()
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

    def servidor(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('127.0.0.1', 5000))
        server.listen(1)
        conn, addr = server.accept()
        print('Connected by' + str(addr))
        while True:
            msg = conn.recv(1024)
            if (not msg or msg == 'sair'):
                break
            print(addr, msg.decode('utf-8'), end='\n')
        msg = "Sucesso"
        conn.send(msg.encode('utf-8'))
        print("Finalizando")
        conn.close()
