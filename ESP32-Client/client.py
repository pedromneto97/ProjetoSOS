import socket
from gc import collect

import ujson


# Classe client para ser utilizado na pulseira
class Client:

    # Construtor que chama o conectar
    def __init__(self, sta):
        self.sta = sta

    # TODO-me implementar enviar o horário
    def client(self, mac, tipo, hora, chamadas=1, reenvio=False):
        if reenvio:
            try:
                end = self.endereco()
                tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria o socket
                tcp.connect(end)  # Conecta com o servidor
                d = {
                    "id": mac,
                    "tipo": tipo,
                    "chamadas": chamadas,
                    "horas": hora[1],
                    "minutos": hora[2]
                }
                tcp.send(ujson.dumps(d).encode('utf-8'))
                tcp.close()  # Fecha a conexão
                return True
            except:
                return False
        else:
            try:
                end = self.endereco()
                tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria o socket
                tcp.connect(end)  # Conecta com o servidor
                d = {
                    "id": mac,
                    "tipo": tipo,
                    "chamadas": chamadas,
                    "hora": hora[1],
                    "minuto": hora[2]
                }
                tcp.send(ujson.dumps(d).encode('utf-8'))
                tcp.close()  # Fecha a conexão
                return True
            except:
                # TODO-me validar se está funcionando corretamente e acertar o envio desses dados salvos
                print("Não foi possível se conectar com o servidor")
                l = {}
                try:
                    f = open('estado.json', 'r')
                    l = ujson.loads(f.read())
                    f.close()
                finally:
                    try:
                        flag = True
                        for item in l:
                            if item['tipo'] == tipo:
                                flag = False
                                item['chamadas'] += 1
                                break
                        if flag:
                            l.update({len(l): {
                                "tipo": tipo,
                                "chamadas": chamadas,
                                "hora": hora[1],
                                "minuto": hora[2]
                            }})
                            f = open('estado.json', 'w')
                            f.write(ujson.dumps(l))
                            f.close()
                            del l
                            del flag
                    except:
                        print("Erro ao salvar estado")
                return False

    def endereco(self):
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
