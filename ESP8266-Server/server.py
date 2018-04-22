import network
from time import sleep
import socket
import os

# Classe do server
class Server:
    # Classe para utilizar a wireless
    station = network.WLAN(network.STA_IF)
    ssid = "Pedro e Roberto"  # SSID da rede
    password = "P3dr03r0b3rt0"  # Senha da rede

    # Construtor
    def __init__(self):
        #f = open('wifi.txt','r')
        self.conectar()

    # Função para se conectar na rede
    def conectar(self):
        # Verifica se já está conectado
        if (self.station.isconnected()):
            print("Conectado")
            return
        # Ativa o Wifi
        self.station.active(True)
        # Conecta na rede
        self.station.connect(self.ssid, self.password)
        # Mantém no laço enquanto não estiver conectado
        while self.station.isconnected() == False:
            # machine.idle()
            print("Não conectado")
            sleep(2)
            pass

    # Servidor
    def servidor(self):
        # Enquanto não receber um endereço IP
        while self.station.status() != 5:
            pass
        # Cria o socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        confs = self.station.ifconfig()  # Recebe as configurações de endereço
        aux = confs[0].split('.')  # Sepera o endereço IP por ponto
        # Monta o 192.168.1.25
        ip = str(aux[0]) + '.' + str(aux[1]) + '.' + str(aux[2]) + '.' + str(25)
        # Define as configurações de IP, só alterando o IP do server
        self.station.ifconfig((ip, confs[1], confs[2], confs[3]))
        # Seta as variáveis como nada
        confs = None
        aux = None
        server.bind((ip, 5000))  # Da bind no endereço
        ip = None  # Esvazia
        server.listen(1)  # Começa a ouvir
        print("Esperando:\n")
        conn, addr = server.accept()  # Recebe a conecção e o endereço
        print('Connected by' + str(addr))
        # Laço das mensagens do cliente
        while True:
            msg = conn.recv(1024)  # Recebe a mensagen
            if not msg or (msg.decode('utf-8') is 'sair'):  # Compara e ver se é para sair
                break
            print(addr, msg.decode('utf-8'), end='\n')
        msg = "Sucesso"
        conn.send(msg.encode('utf-8'))  # Retorna a mensagem para o cliente
        print("Finalizando")
        conn.close() #Fecha a conecção
