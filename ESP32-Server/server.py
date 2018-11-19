import socket
from gc import collect
from time import sleep_ms

import ujson
from machine import reset
from tipo import Tipo


# Classe do server
class Server:

    # Construtor
    def __init__(self, sta):
        self.station = sta

    def endereco(self):
        confs = self.station.ifconfig()  # Recebe as configurações de endereço
        aux = confs[0].split('.')  # Sepera o endereço IP por ponto
        # Monta o 192.168.1.25
        ip = str(aux[0]) + '.' + str(aux[1]) + '.' + str(aux[2]) + '.' + str(100)
        # Define as configurações de IP, só alterando o IP do server
        self.station.ifconfig((ip, confs[1], confs[2], confs[3]))
        # Seta as variáveis como nada
        del confs
        del aux
        return (ip, 5000)

    # Servidor
    def servidor(self, device, cadastro=False):
        # Cria o socket
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if cadastro:
            end = self.endereco()
            server.bind(end)  # Da bind no endereço
            server.listen(1)  # Começa a ouvir
            print("Endereço: " + end[0])
            print("Esperando:\n")
            # Laço das mensagens do cliente
            while True:
                conn, addr = server.accept()  # Recebe a conecção e o endereço
                print('Conectado por: ' + str(addr))
                msg = conn.recv(2048)  # Recebe a mensagen
                l = ujson.loads(msg.decode('utf-8'))
                if l['id'] not in device.cadastrados.keys():
                    conn.close()
                    server.close()
                    return l['id']
                conn.close()
        else:
            try:
                end = self.endereco()
                server.bind(end)  # Da bind no endereço
                server.listen(28)  # Começa a ouvir
                print("Endereço: " + str(end))
                print("Esperando:\n")
                # Laço das mensagens do cliente
                while True:
                    conn, addr = server.accept()  # Recebe a conecção e o endereço
                    print('Conectado por: ' + str(addr))
                    device.avisa()
                    msg = conn.recv(2048)  # Recebe a mensagen
                    l = ujson.loads(msg.decode('utf-8'))
                    if l['id'] not in device.cadastrados.keys():
                        conn.close()
                        device.desliga_aviso()
                        continue
                    if l['tipo'] in device.lista.keys():
                        flag = True
                        for item in device.lista[l['tipo']]:
                            if item['id'] == l['id']:
                                item['chamadas'] += 1
                                l['chamadas'] = item['chamadas']
                                l['horas'] = item['horas']
                                l['minutos'] = item['minutos']
                                flag = False
                                break
                        if flag:
                            device.lista[l['tipo']].append({
                                'id': l['id'],
                                'horas': l['horas'],
                                'minutos': l['minutos'],
                                'chamadas': l['chamadas']
                            })
                            device.altera_tamanho(l['tipo'], True)
                            device.ordenar()
                        del flag
                    else:
                        device.desliga_aviso()
                        conn.close()
                        continue
                    device.reinicia_inativo()
                    ind = next(i for i, valor in enumerate(device.lista[l['tipo']]) if valor['id'] == l['id'])
                    if device.iterador['tipo'] != l['tipo'] or device.iterador['iterador'] != ind:
                        anterior = device.anterior()
                        device.iterador['tipo'] = l['tipo']
                        device.iterador['iterador'] = ind
                        device.escreve_oled(tipo=l['tipo'], nome=device.cadastrados[l['id']]['nome'],
                                            quarto=device.cadastrados[l['id']]['quarto'], hora=l['horas'],
                                            minuto=l['minutos'], chamadas=int(l['chamadas']), posicao=True,
                                            anterior=anterior)
                    else:
                        device.escreve_oled(tipo=l['tipo'], nome=device.cadastrados[l['id']]['nome'],
                                            quarto=device.cadastrados[l['id']]['quarto'], hora=l['horas'],
                                            minuto=l['minutos'], chamadas=int(l['chamadas']), posicao=True)
                    sleep_ms(300)
                    device.desliga_aviso()
                    collect()
                    conn.close()  # Fecha a conexão
            except:
                if len(device.lista[Tipo.EMERGENCIA]) > 0 or len(device.lista[Tipo.AJUDA]) > 0 or len(
                        device.lista[Tipo.BATERIA]) > 0:
                    try:
                        f = open('estado.json', 'w')
                        f.write(ujson.dumps(device.lista))
                        f.close()
                    except:
                        print("Erro ao salvar estado")
                reset()
