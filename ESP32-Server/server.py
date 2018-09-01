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
                    device.oled.fill(0)
                    device.oled.text('ATENCAO!', 0, 0)
                    device.oled.fill('CADASTRAR TRANSMISSOR!', 0, 30)
                    device.oled.show()
                    conn.close()
                    server.close()
                    return
                if list['mac'] in device.lista.keys():
                    if list['tipo'] in device.lista.get(list['mac']).keys():
                        device.lista.get(list['mac']).get(list['tipo']).update({
                            "chamadas": device.lista.get(list['mac']).get(list['tipo'])['chamadas'] + list['chamadas']
                        })
                    else:
                        device.lista.get(list['mac']).update({list['tipo']: {
                            "horas": list['horas'] + ":" + list['minutos'],
                            "chamadas": list['chamadas']
                        }})
                else:
                    device.lista.update({list['mac']: {list['tipo']: {
                        "horas": list['horas'] + ":" + list['minutos'],
                        "chamadas": list['chamadas']
                    }}})
                print(device.lista)
                # TODO-me Agrupar e exibir o número de solicitações por tipo
                device.oled.fill(0)
                device.oled.text(device.lista[0]['tipo'], 0, 0)
                device.oled.text("Nome: " + device.cadastrados[list['mac']]['nome'], 0, 20)
                device.oled.text("Quarto: " + device.cadastrados[list['mac']]['quarto'], 0, 40)
                device.oled.text("Horario: " + list['horas'] + ':' + list['minutos'], 0, 60)
                device.oled.text(list['chamadas'], 110, 60)
                if len(device.lista) > 1:
                    device.oled.text("+", 110, 0)
                device.oled.show()
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
