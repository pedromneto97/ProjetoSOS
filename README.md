# **SOS - Solução para Obtenção de Suporte**

O projeto SOS é desenvolvido por Pedro de Mattos Mariano Mendes Neto e Ricardo Harms Schiniegoski. Este projeto é desenvolvido
para a disciplina de Projeto de Sistema de Informação do curso de Engenharia de Computação da Universidade Estadual de Ponta Grossa (UEPG).
  
O principal objetivo do projeto é facilitar a obtenção de ajuda em um lar de idosos, porém devido a comunicação entre os ESPs ser feita através de protocolo TCP/IP, é possível adaptar o projeto para atuar através de um servidor, ampliando o raio de atuação.  
  
## **Equipamentos**

Para o desenvolvimento do projeto está sendo utilizado os seguintes equipamentos:
- ESP32 - Placa de desenvolvimento NodeMCU-32S
- Acelerômetro - Módulo GY-61 com saídas analógicas em cada um dos seus três eixos
- LCD - Display LCD 16x02


## **Ferramentas**

Para a parte de programação do projeto está sendo utilizado as seguintes ferramentas:
- Python3.5 - Linguagem de programação compatível com o MicroPython
- PIP - Sistema gerenciador de pacotes do Python
- [Micropython](http://micropython.org/) - Versão compacta do Python e otimizada para microcontroladores
- [Esptool](https://github.com/espressif/esptool) - Ferramenta para instalação do firmware em ESPs
- [Ampy](https://github.com/adafruit/ampy) - Adafruit MicroPython Tool, ferramenta para comunicação serial com o ESP, utilizada para manipular os arquivos dentro do ESP


## **Instalação**
### **Preparando o ambiente**
Primeiramente é necessário instalar o Python3.5 e para isso utiliza-se
  
    sudo apt-get install python3.5  

Após instalar o Python3.5 deve-se instalar o pip para a versão 3.5 do Python. Para isso deve-se seguir os seguintes passos:  
  
    cd [seu_diretorio]  
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py  
    python3.5 get-pip.py  

É possível ver a versão atual do pip e o Python utilizando o `pip -V`  
  
Instalado o pip é possível instalar o esptool utilizando:  
  
    pip install esptool  
E para instalar o ampy:  
  
    pip install adafruit-ampy  
Pode haver alguns problemas com o esptool e o ampy devido a necessidade de permissão ao utilizar a porta usb pelo `/dev/ttyUSB0`, caso isso ocorra, é necessário instalar os dois utilizando o `sudo`.  
  
### **Instalando o firmware no ESP32**
  
O _firmware_ do ESP32 junto com os outros _firmwares_ podem ser encontrados na página de download do [MicroPython](http://micropython.org/download)  
Basta baixar o _firmware_ correspondente a sua placa de desenvolvimento. O _firmware_ do ESP32 ainda está em desenvolvimento, portanto há _builds_ diárias.  
  
Após baixar o _firmware_ do ESP32, basta seguir os passos:  
  
    esptool.py --port /dev/ttyUSB0 erase_flash
    esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-firmware.bin
  
## **Manipulação de arquivos no ESP**
  
Para colocar os arquivos no ESP32, utiliza-se o programa ampy:  
  
    ampy -p /dev/ttyUSB0 put main.py
  
Para remover um arquivo no ESP32:  
  
    ampy -p /dev/ttyUSB0 rm main.py
  
Também é possível listar os arquivos e pegar o conteúdo deles:  
  
    ampy -p /dev/ttyUSB0 ls
    ampy -p /dev/ttyUSB0 get main.py  
  
## **Em andamento**  
  
- Nível de bateria
- Cadastro da pulseira
- Comunicação dos dados
- Atuação do acelerômetro
- Atuação do botão de solicitação de ajuda
- Display das informações no LCD
- Botões do LCD

## **Documentação**
  
O projeto está separado pela atuação do ESP32, aonde um irá atuar como servidor e outros ESPs irão atuar como clientes.  
Pela necessidade de utilizar uma comunicação WiFi, caso não encontre um ponto de acesso, o ESP irá se tornar um ponto de acesso aonde poderá ser cadastrado o SSID e senha.  
  
  **_EM ANDAMENTO_**
