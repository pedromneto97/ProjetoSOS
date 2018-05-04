import network
import machine
from time import sleep
import socket


# Classe client para ser utilizado na pulseira
class Client:
    # station é a variável para utilizar a wireless network
    station = network.WLAN(network.STA_IF)
    ssid = "Pedro e Roberto"  # ssid do WiFi
    password = "P3dr03r0b3rt0"  # Senha do ssid

    # Construtor que chama o conectar
    def __init__(self):
        self.conectar()

    def conectar(self):
        # Primeira condição é verificar se já está conectado
        if (self.station.isconnected()):
            print("Conectado")
            return
        self.station.active(True)  # Ativa o WiFi
        self.station.connect(self.ssid, self.password)  # Conecta na rede
        # Enquanto não estiver conectado, se mantém no loop
        while self.station.isconnected() == False:
            # Implementar para manter a máquina desligada enquanto espera se conectar
            # machine.idle()
            print("Não conectado")
            sleep(2)
            pass
        print("Conectado")

    def client(self):
        try:
            HOST = '192.168.1.25'  # Endereco IP do Servidor
            PORT = 5000  # Porta que o Servidor esta
            tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria o socket
            tcp.connect((HOST, PORT))  # Conecta com o servidor
            # Implementar para caso não haja conexão com o servidor
            print('Conectado com o servidor!\n Para sair escreva: sair')
            msg = input()
            # Mantém no laço enquando não escreve sair
            while True:
                tcp.send(msg.encode('utf-8'))  # Envia para o servidor a mensagem em utf-8
                if msg is 'sair':  # Compara se a mensagem é sair
                    break  # Sai do laço
                msg = input()
            msg = tcp.recv(1024)  # Recebe a resposta do servidor
            print(msg.decode('utf-8'))  # Escreve a mensagem do servidor
            tcp.close()  # Fecha a conexão
        except ConnectionError: