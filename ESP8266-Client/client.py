import socket
from gc import collect
# Classe client para ser utilizado na pulseira
class Client:

    # Construtor que chama o conectar
    def __init__(self, sta):
        self.sta = sta

    def client(self, dados):
        try:
            confs = self.sta.ifconfig()  # Recebe as configurações de endereço
            aux = confs[0].split('.')  # Sepera o endereço IP por ponto
            HOST = str(aux[0]) + '.' + str(aux[1]) + '.' + str(aux[2]) + '.' + str(100)
            # Seta as variáveis como nada
            confs = None
            aux = None
            collect()
            PORT = 5000  # Porta que o Servidor esta
            tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria o socket
            tcp.connect((HOST, PORT))  # Conecta com o servidor
            tcp.send(dados.encode('utf-8'))  # Envia para o servidor a mensagem em utf-8
            tcp.close()  # Fecha a conexão
        except:
            print("Não foi possível se conectar com o servidor")