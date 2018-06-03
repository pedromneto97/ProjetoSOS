# **SOS - Solução para Obtenção de Suporte**

O projeto SOS é desenvolvido por Pedro de Mattos Mariano Mendes Neto e Ricardo Harms Schiniegoski. Este projeto é desenvolvido
para a disciplina de Projeto de Sistema de Informação do curso de Engenharia de Computação da Universidade Estadual de Ponta Grossa (UEPG).
  
O principal objetivo do projeto é facilitar a obtenção de ajuda em um lar de idosos, porém devido a comunicação entre os ESPs ser feita através de protocolo TCP/IP, é possível adaptar o projeto para atuar através de um servidor, ampliando o raio de atuação.  
  
## **Equipamentos**

Para o desenvolvimento do projeto está sendo utilizado os seguintes equipamentos:
- ESP32 - Placa de desenvolvimento NodeMCU-32S
- Acelerômetro - Módulo GY-61 com saídas analógicas em cada um dos seus três eixos
- ~~LCD - Display LCD 16x02~~  
- Display OLED 128x64

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
  
### Receptor  
  
- Nível de bateria  
  
    A ideia é fazer um divisor de tensão do `VIN` com uma resistência equivalente do circuito de 10M. A primeira parte tem uma resistencia de 8M, após a resistência de 8M o circuito se divide indo para o ADC e para um resistor de 2M. Depois do resistor de 2M será ligado ao _ground_, assim a tensão no ADC será 1/5 da tensão de alimentação.

### Pulseira  
  
- Nível de bateria
- Limiar do acelerômetro  
  
  A partir de qual aceleração (em _g_) é uma queda.

## **Documentação**
  
### **Pinos do ESP32 - Pulseira**
  
O circuito do ESP32 está feito de maneira que o GPIO15 atua como a entrada, detectando a borda de subida e chamando uma função quando detecta.  
O GPIO2 atua como pino de saída para acionar o _LED_ e o _buzzer_.  
Já o GPIO4 atua como pino de saída para alimentar o botão, assim é possível fazer um _debounce_ para o botão.  
O acelerômetro está ligado no ESP32, sendo o eixo _X_ no GPIO32, o eixo _Y_ no GPIO35 e o eixo _Z_ no GPIO34.  
  
### **Pinos do ESP32 - Receptor**
  
O circuito do ESP32 está feito de maneira que o GPIO15 atua como uma saída para alimentar os botões do receptor. O GPIO2 atua como entrada, chamando uma função em que passa a ser exibido o próximo item da lista. O GPIO4 atua como entrada, chamando a função que remove o item atual da lista. O GPIO19 atua como uma saída para alimentar o buzzer.  
Os pinos 21 e 22 são utilizados para comunicação I2C com o display de OLED, sendo o GPIO21 como `sda` e o GPIO22 como `scl`.  
  
### **MODO DE OPERAÇÃO**
O projeto está separado pela atuação do ESP32, aonde um irá atuar como servidor e outros ESPs irão atuar como clientes.  
Pela necessidade de utilizar uma comunicação WiFi, caso não encontre um ponto de acesso previamente cadastrado, o ESP irá se tornar um ponto de acesso aonde poderá ser cadastrado o SSID e senha.  
**_APENAS PARA A PULSEIRA_**  
Durante o cadastro do Wifi poderá ser possível limpar o cadastro da pulseira.  
Após o cadastro do Wifi, se conectado, poderá ser cadastrado a pulseira, com a informação do **nome** e do **quarto**.  
Após todos os cadastros, a pulseira ficará esperando o botão ser pressionado. Ao pressionar o botão, irá emitir um beep e conectar ao servidor. Caso não seja possível se conectar ao servidor, a pulseira irá emitir um _beep_ extendido.   
A pulseira só irá requisitar ajuda uma vez a cada 15 segundos!  
**_APENAS PARA O RECEPTOR_**  
Após o cadastro do Wifi, o receptor irá se tornar um servidor e esperar a conexão da pulseira. Caso haja alguma conexão, será emitido um _beep_.  
Ao pressionar o botão de próximo, é exibido no display a próxima pessoa que requisitou ajuda e sempre que há mais de uma pessoa, um símbolo de + ficará visível no canto do display.  
Ao pressionar o botão de remover, o nome atual exibido no display será removido, retornando ao começo da lista.  
Foi implementado vários `try except` de maneira que tratem qualquer erro, salvem o estado atual e reiniciem o ESP32.
  
  **_EM ANDAMENTO_**
