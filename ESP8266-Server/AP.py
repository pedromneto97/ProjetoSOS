import network
import socket
import os


class AccessPoint:
    ap = network.WLAN(network.AP_IF)

    def __init__(self):
        self.ap.active(True)
        self.ap.config(essid='receptor', authmode=4, password='teste123')

    def web_server(self):
        flag = False
        addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
        s = socket.socket()
        s.bind(addr)
        s.listen(1)
        while True:
            html = """
               <!DOCTYPE html>
               <html>
                   <head>
                       <title>ESP WiFi</title>
                   </head>
                   <body>
                       <form>
                           <div>
                               <label for="SSID">SSID</label>
                               <input type="text" id="SSID" name="SSID">
                           </div>
                           <div class="form-group">
                               <label for="pasword">Senha</label>
                               <input type="password" id="pasword" name="password">
                           </div>
                           <button type="submit">Conectar</button>
                       </form>
                   </body>
               </html>
            """
            cl, addr = s.accept()
            print('client connected from', addr)
            cl_file = cl.makefile('rwb', 0)
            while True:
                line = cl_file.readline()
                line = line.decode('ascii')
                indice = line.find('GET')
                if indice != -1:
                    indice = line.find('/', indice + 3)
                    if indice != -1:
                        indice = line.find('SSID', indice + 1)
                        seg = line.find('&password=', indice)
                        if indice != -1 and seg != -1:
                            ssid = line[indice + 5:seg]
                            ssid = ssid.replace('+', ' ')
                            indice = line.find(' HTTP')
                            if indice != -1:
                                password = line[seg + 10: indice]
                                f = open('wifi.txt', 'w')
                                f.write(ssid + '\n')
                                f.write(password + '\n')
                                f.close()
                                html = """
                                       <!DOCTYPE html>
                                       <html>
                                           <head>
                                               <title>ESP WiFi</title>
                                           </head>
                                           <body>
                                               <h1>Login salvo!</h1>
                                           </body>
                                       </html>
                                       """
                                flag = True
                if not line or line == '\r\n':
                    break
            response = html
            cl.send(response)
            cl.close()
            if flag:
                self.ap.active(False)
                return
