import pulseiraDNS
import ujson
import machine

class Pulseira:
    def __init__(self):
        try:
            print("Reading configuration...")
            f = open('pulseira.json', 'r')
            self.config = ujson.loads(f.read())
            f.close()
        except:
            print("Pulseira não cadastrada")
            self.start()


    def start(self):
            d = pulseiraDNS.start()
            self.config = {
                'nome':d[b'nome'],
                'quarto':d[b'quarto']
            }
            f = open('config.json', 'w')
            f.write(ujson.dumps(self.config))
            f.close()
            machine.reset()