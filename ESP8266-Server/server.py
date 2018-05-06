import network
import socket
from gc import collect
# Classe do server
class Server:

    # Construtor
    def __init__(self, sta):
        self.station = sta
        collect()

    # Servidor
    def servidor(self):
        # Cria o socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        confs = self.station.ifconfig()  # Recebe as configurações de endereço
        aux = confs[0].split('.')  # Sepera o endereço IP por ponto
        # Monta o 192.168.1.25
        ip = str(aux[0]) + '.' + str(aux[1]) + '.' + str(aux[2]) + '.' + str(100)
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
        conn.close()  # Fecha a conexão
