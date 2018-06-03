import socket
from gc import collect

import ujson
from machine import reset


# Classe do server
class Server:

    # Construtor
    def __init__(self, sta):
        self.station = sta
        collect()

    # Servidor
    def servidor(self, device):
        try:
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
            server.listen(28)  # Começa a ouvir
            print("Endereço: " + ip)
            print("Esperando:\n")
            # Laço das mensagens do cliente
            while True:
                conn, addr = server.accept()  # Recebe a conecção e o endereço
                print('Connected by' + str(addr))
                device.p19.value(1)
                msg = conn.recv(1024)  # Recebe a mensagen
                print(addr, msg.decode('utf-8'), end='\n')
                tipo = msg.decode('utf-8')
                msg = conn.recv(1024)  # Recebe a mensagen
                print(addr, msg.decode('utf-8'), end='\n')
                pessoa = msg.decode('utf-8')
                msg = conn.recv(1024)  # Recebe a mensagen
                print(addr, msg.decode('utf-8'), end='\n')
                quarto = msg.decode('utf-8')
                list = ({
                    'tipo': tipo,
                    'nome': pessoa,
                    'quarto': quarto
                })
                print(list)
                device.lista.append(list)
                print(device.lista)
                if len(device.lista) == 1:
                    device.oled.fill(0)
                    device.oled.text(device.lista[0]['tipo'], 0, 0)
                    device.oled.text("Nome: " + device.lista[0]['nome'], 0, 20)
                    device.oled.text("Quarto: " + device.lista[0]['quarto'], 0, 40)
                    device.oled.show()
                else:
                    device.oled.text("+", 110, 0)
                    device.oled.show()
                print("Finalizando")
                device.p19.value(0)
                conn.close()  # Fecha a conexão
        except:
            if len(device.lista) > 0:
                try:
                    f = open('estado.json', 'w')
                    f.write(ujson.dumps(device.lista))
                    f.close()
                except:
                    print("Erro ao salvar estado")
            reset()
