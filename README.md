# **SOS - Solução para Obtenção de Suporte**

O projeto SOS é desenvolvido por Pedro de Mattos Mariano Mendes Neto e Ricardo Harms Schiniegoski
e tem como objetivo facilitar a obtenção de ajuda em um lar de idosos. Este projeto é desenvolvido
para a disciplina de Projeto de Sistema de Informação do curso de Engenharia de Computação da
Universidade Estadual de Ponta Grossa (UEPG).


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
- [Esptool]((https://github.com/espressif/esptool) - Ferramenta para instalação do firmware em ESPs
- [Ampy](https://github.com/adafruit/ampy) - Adafruit MicroPython Tool, ferramenta para comunicação serial com o ESP, utilizada para manipular os arquivos dentro do ESP


## **Instalação**

Primeiramente é necessário instalar o Python3.5 e para isso utiliza-se
`sudo apt-get install python3.5`

Após instalar o Python3.5 deve-se instalar o pip. Para isso deve-se seguir os seguintes passos:
`cd [seu_diretorio]`
`curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py`
`python3.5 get-pip.py`
