from machine import freq
from time import sleep
import server

freq(160000000)
# led = machine.Pin(15, machine.Pin.OUT)
#  Porta 13 = D7
#  Porta 15 = D8
# but = machine.Pin(13, machine.Pin.IN)

while True:
    serv = server.Server()
    sleep(3)
    s = serv.servidor()
