from machine import freq
# from time import sleep
# import server
from AP import AccessPoint

freq(160000000)
ap = AccessPoint()
ap.web_server()
# while True:
# Cria o server
# serv = server.Server()
# Chama o server
# s = serv.servidor()
