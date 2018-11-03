import socket
from gc import collect

import ujson


# Classe client para ser utilizado no transmissor
class Client:

    # Construtor que chama o conectar
    def __init__(self, sta):
        self.sta = sta

    def client(self, mac, tipo, hora, chamadas=1, reenvio=False):
        d = {
            "id": mac,
            "tipo": tipo,
            "chamadas": chamadas,
            "horas": hora[0],
            "minutos": hora[1]
        }
        if reenvio:
            try:
                end = self.endereco()
                tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria o socket
                tcp.connect(end)  # Conecta com o servidor
                tcp.send(ujson.dumps(d).encode('utf-8'))
                tcp.close()  # Fecha a conexão
            except:
                raise
        else:
            try:
                end = self.endereco()
                tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria o socket
                tcp.connect(end)  # Conecta com o servidor
                tcp.send(ujson.dumps(d).encode('utf-8'))
                tcp.close()  # Fecha a conexão
            except:
                print("Não foi possível se conectar com o servidor")
                raise

    def endereco(self):
        try:
            confs = self.sta.ifconfig()  # Recebe as configurações de endereço
            aux = confs[0].split('.')  # Sepera o endereço IP por ponto
            HOST = str(aux[0]) + '.' + str(aux[1]) + '.' + str(aux[2]) + '.' + str(100)
            # Seta as variáveis como nada
            del confs
            del aux
            collect()
            print("Host: " + HOST)
            PORT = 5000  # Porta que o Servidor esta
            return (HOST, PORT)
        except:
            print("Erro ao capturar o HOST")
            raise
