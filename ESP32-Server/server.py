import socket
from gc import collect

import ujson
from machine import reset


# Classe do server
class Server:

    # Construtor
    def __init__(self, sta):
        self.station = sta

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
            del confs
            del aux
            server.bind((ip, 5000))  # Da bind no endereço
            server.listen(28)  # Começa a ouvir
            print("Endereço: " + ip)
            print("Esperando:\n")
            # Laço das mensagens do cliente
            while True:
                conn, addr = server.accept()  # Recebe a conecção e o endereço
                print('Conectado por: ' + str(addr))
                device.p19.value(1)
                msg = conn.recv(1024)  # Recebe a mensagen
                list = ujson.loads(msg.decode('utf-8'))
                if list['mac'] not in device.cadastrados:
                    conn.close()
                    device.p19.value(0)
                    continue
                if list['tipo'] in device.lista.keys():
                    flag = True
                    for item in device.lista[list['tipo']]:
                        if item['id'] == list['id']:
                            item['chamadas'] += 1
                            list['chamadas'] = item['chamadas']
                            flag = False
                            break
                    if flag:
                        device.lista[list['tipo']].append({
                            'id': list['mac'],
                            'horas': list['horas'],
                            'minutos': list['minutos'],
                            'chamadas': list['chamadas']
                        })
                    del flag
                else:
                    device.p19.value(0)
                    conn.close()
                    continue
                print(device.lista)
                device.oled.fill(0)
                device.oled.text(device.lista[list['tipo']], 0, 0)
                device.oled.text("Nome: " + device.cadastrados[list['mac']]['nome'], 0, 20)
                device.oled.text("Quarto: " + device.cadastrados[list['mac']]['quarto'], 0, 40)
                device.oled.text("Horario: " + list['horas'] + ':' + list['minutos'], 0, 60)
                device.oled.text(device.list['chamadas'], 110, 60)
                if len(device.lista) > 1:
                    device.oled.text("+", 110, 0)
                device.oled.show()
                device.p19.value(0)
                collect()
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
