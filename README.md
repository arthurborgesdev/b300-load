# b300-load (Balança eletrônica para campanha da saúde)

## Pra que serve?

Para ser utilizada em uma campanha publicitária incentivando as pessoas a se preocuparem mais com a saúde.


## Como funciona?

Ao ligar o equipamento (desenvolvido utilizando 4 células de carga, um raspberry pi 3 e um módulo hx711), o mesmo é iniciado com um SO Linux que ao ligar chama o script para carregar o programa escrito em Python. O mesmo acessa o GPIO do raspberry, lê os dados das células de carga e transfere as informações para o monitor através da porta HDMI.


## Arquivos principais e suas funções

**/research-links**

Contém a maior parte dos links utilizados para pesquisa, que ajudaram o desenvolvimento do protótipo.

**/bmkt.sh**

Roda o script balanca.py até que uma tecla seja pressionada para finalizar o programa. 

**/balanca.py**

Arquivo principal. Reponsável por fazer a conversão das medidas do HX711 para strings e mostrar os dados na tela utilizando Tkinter. Contém rotinas para calibrar a balança antes de aferir o peso.

**/display.py**

Arquivo contendo código para renderização da tela. Utilizado como base para renderização do peso.