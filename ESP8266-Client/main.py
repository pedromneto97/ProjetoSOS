import machine
import client

machine.freq(160000000)

while True:
    c = client.Client() #Cria o cliente
    c.client() #Chama a função para se conectar com o servidor
