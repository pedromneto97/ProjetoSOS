# Contribuição: Ariangelo Hauer Dias

import socket

import machine
import network
import ujson

CONTENT = """\
HTTP/1.0 200 OK

<!DOCTYPE html>
<html lang="pt-br">
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no"/>
        <meta charset="utf-8"> 
        <title>Cadastro</title>
        <style>
            .c{text-align: center;}
            div,input{padding:5px;font-size:1em;}
            input{width:95%;}
            body{text-align: center;font-family:verdana;}
            button{border:0;border-radius:0.3rem;background-color:#1fa3ec;color:#fff;line-height:2.4rem;font-size:1.2rem;width:100%;}
            .q{float: right;width: 64px;text-align: right;}
            .l{background: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAMAAABEpIrGAAAALVBMVEX///8EBwfBwsLw8PAzNjaCg4NTVVUjJiZDRUUUFxdiZGSho6OSk5Pg4eFydHTCjaf3AAAAZElEQVQ4je2NSw7AIAhEBamKn97/uMXEGBvozkWb9C2Zx4xzWykBhFAeYp9gkLyZE0zIMno9n4g19hmdY39scwqVkOXaxph0ZCXQcqxSpgQpONa59wkRDOL93eAXvimwlbPbwwVAegLS1HGfZAAAAABJRU5ErkJggg==") no-repeat left center;background-size: 1em;}
        </style>
        <script>
            function c(l) {
                document.getElementById("nome").value = l.innerText || l.textContent;
                document.getElementById("quarto").focus();
            }
        </script>
    </head>
    <body>
        <div style="text-align:left;display:inline-block;min-width:260px;">
            <br/>
            Código do transmissor:
            <br/>
            ---lines---
            <form method="get" action="salvacadastro">
                <br/>
                <input id="nome" name="nome" length=32 placeholder="Nome"><br/>
                <input id="quarto" name="quarto" length=64 type="password" placeholder="Quarto"><br/>
                <br/>
                <button type="submit">Salvar</button>
            </form>
        </div>
    </body>
</html>
"""


class DNSQuery:
    def __init__(self, data):
        self.data = data
        self.domain = ''

        # print("Reading datagram data...")
        m = data[2]  # ord(data[2])
        type = (m >> 3) & 15  # Opcode bits
        if type == 0:  # Standard query
            ini = 12
            lon = data[ini]  # ord(data[ini])
            while lon != 0:
                self.domain += data[ini + 1:ini + lon + 1].decode("utf-8") + '.'
                ini += lon + 1
                lon = data[ini]  # ord(data[ini])

    def request(self, ip):
        packet = b''
        # print("Request {} == {}".format(self.domain, ip))
        if self.domain:
            packet += self.data[:2] + b"\x81\x80"
            packet += self.data[4:6] + self.data[4:6] + b'\x00\x00\x00\x00'  # Questions and Answers Counts
            packet += self.data[12:]  # Original Domain Name Question
            packet += b'\xc0\x0c'  # Pointer to domain name
            packet += b'\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'  # Response type, ttl and resource data length -> 4 bytes
            packet += bytes(map(int, ip.split('.')))  # 4 bytes of IP
        return packet


def start(identificacao):
    # DNS Server
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(True)
    id = machine.unique_id()
    ap_if.config(essid='ESP32 SERVER-{:02X}:{:02X}:{:02X}:{:02X}'.format(id[0], id[1], id[2], id[3]),
                 authmode=1)  # authmode=1 == no pass
    ip = ap_if.ifconfig()[0]
    print('APDNS Server: {:s}'.format(ip))

    udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udps.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udps.setblocking(False)
    udps.bind(('', 53))

    # Web Server
    ai = socket.getaddrinfo(ip, 80)
    addr = ai[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    s.settimeout(2)
    # print("Web Server: Listening http://{}:80/".format(ip))

    configured = False
    d = {}
    # DNS Loop
    while not configured:
        try:
            data, addr = udps.recvfrom(1024)
            p = DNSQuery(data)
            udps.sendto(p.request(ip), addr)
        except:
            # just wait for APDNS
            pass

        # Web loop
        try:
            client_stream = s.accept()[0]
            req = client_stream.readline()

            while True:
                h = client_stream.readline()
                if h == b"" or h == b"\r\n" or h == None:
                    break

            request_url = req[5:18]
            if request_url == b'salvacadastro':
                params = req[19:-11]
                try:
                    d = {key: value for (key, value) in [x.replace(b'+', b' ').split(b'=') for x in params.split(b'&')]}
                    configured = True
                except:
                    d = {}

            client_stream.write(CONTENT.replace('---lines---', identificacao))
            client_stream.close()
        except:
            # Just wait timeout for web
            pass

    udps.close()
    s.close()
    ap_if.active(False)
    l = {}
    try:
        f = open('cadastros.json', 'r')
        l = ujson.loads(f.read())
        f.close()
    except:
        pass

    l.update({
        identificacao: {
            'nome': d[b'nome'].decode(),
            'quarto': int(d[b'quarto'].decode())
        }
    })
    f = open('cadastros.json', 'w')
    f.write(ujson.dumps(l))
    f.close()
    return d
