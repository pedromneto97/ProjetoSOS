import socket

# Classe client para ser utilizado na pulseira
class Client:

    # Construtor que chama o conectar
    def __init__(self, sta):
        self.sta = sta

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
        except :
            print("Não foi possível se conectar")