#from tkinter import *                     # import tkinter (Python3)
from Tkinter import *                    # import tKinter (Python2) - Biblioteca para desenhar imagens

#from subprocess import call

import os 
import RPi.GPIO as GPIO                  # download from python.org
import time              
import sys
import numpy                              # sudo apt-get python-numpy

#def shutdown(pin):
    #call('halt', shell=False)

# Cria o Array para pegar as leituras
def createBoolList(size=8):
    ret = []
    for i in range(8):
        ret.append(False)
    return ret

# Função chamada para fechar o programa
def cleanAndExit():
    print("Cleaning...")
    GPIO.cleanup()    # Limpa as GPIOs
    print("Bye!")
    sys.exit() # Fecha o programa python

	
power_off = 18 # Pino em que está ligado o botão vermelho
GPIO.setmode(GPIO.BCM) # Seta a nomenclatura dos pinos para BCM (SoC) em vez de Board (Placa, que é sujeita a mudanças)
GPIO.setup(power_off, GPIO.IN) # Seta o pino 18 como entrada (Semelhante ao 'pinMode(18, INPUT)' do Arduino) 

# Aqui começa a classe principal, que eu usei como modelo para o desenvolvimento
class HX711:
    def __init__(self, dout, pd_sck, gain=128):
        self.PD_SCK = pd_sck # Atribui o pino pd_sck a uma variável interna, chamada PD_SCK
        self.DOUT = dout # Faz a mesma coisa acima, mas para dout/DOUT

        GPIO.setmode(GPIO.BCM)              # Set pinout to BCM numbering system (Broadcom SOC) 
        GPIO.setup(self.PD_SCK, GPIO.OUT)   # Set pd_sck as output pin (yellow wire) 
        GPIO.setup(self.DOUT, GPIO.IN)      # Set dout as input pin (green wire)
 #       GPIO.setup(self.OFF, GPIO.IN)       # Set off as input pin (button to power off)

 #       self.OFF = 0
		# Declaração de variáveis internas
        self.GAIN = 0
        self.OFFSET = 0
        self.SCALE = 1
        self.REFERENCE_UNIT = 1 # The value returned by the hx711 that corresponds to your reference unit AFTER dividing by the scale
        self.lastVal = 0

        #GPIO.output(self.PD_SCK, True)
        #GPIO.output(self.PD_SCK, False)

        self.set_gain(gain)

        time.sleep(1)
		
	# Conversa com o HX711
    def is_ready(self):
        return GPIO.input(self.DOUT) == 0

    def set_gain(self, gain):
        if gain is 128:
            self.GAIN = 1
        elif gain is 64:
            self.GAIN = 3
        elif gain is 32: 
            self.GAIN = 2

        GPIO.output(self.PD_SCK, False)
        self.read()

    def read(self):
        while not self.is_ready():
            #print("WAITING")
            pass
		# Aqui é o 'TCHANS' da leitura, em que os 24 bits do HX711 são armazenados num array e tratados
		# com a biblioteca Numpy
        dataBits = [createBoolList(), createBoolList(), createBoolList()]
        dataBytes = [0x0] * 4
		
        for j in range(2, -1, -1):
            for i in range(0, 8):
                GPIO.output(self.PD_SCK, True)
                dataBits[j][i] = GPIO.input(self.DOUT)
                GPIO.output(self.PD_SCK, False)
            dataBytes[j] = numpy.packbits(numpy.uint8(dataBits[j]))	
		
        #set channel and gain factor for next reading
        for i in range(self.GAIN):
            GPIO.output(self.PD_SCK, True)
            GPIO.output(self.PD_SCK, False)

        #check for all 1
        #if all(item is True for item in dataBits[0]):
        #    return int(self.lastVal)

        dataBytes[2] ^= 0x80
        np_arr8 = numpy.uint8(dataBytes)
        np_arr32 = np_arr8.view('uint32')
        self.lastVal = np_arr32

        return int(self.lastVal)

    def read_average(self, times=10):
        values = 0
        for i in range(times):
            values += self.read()
	
        return values / times

    def get_value(self, times=10):
        return self.read_average(times) - self.OFFSET

    def get_units(self, times=10):
        return float(self.get_value(times)) / float(self.SCALE)

    def get_weight(self, times=10):
        load_kg = float(float(self.get_units(times)) / float(self.REFERENCE_UNIT)) 
        if(load_kg > 1):
            return "%.1f" % load_kg
            #return ("%.1f" % float(float(self.get_units(times)) / float(self.REFERENCE_UNIT)))
        else:
            return "%.1f" % 0
	
	# Código para a tara
    def tare(self, times=15):
        # Backup SCALE value
        scale = self.SCALE
        self.set_scale(1)

        # Backup REFERENCE_UNIT VALUE
        reference_unit = self.REFERENCE_UNIT
        self.set_reference_unit(1)

        value = self.read_average(times)
        self.set_offset(value)

        self.set_scale(scale)
        self.set_reference_unit(reference_unit)

    def set_scale(self, scale):
        self.SCALE = scale

    def set_offset(self, offset):
        self.OFFSET = offset

    def set_reference_unit(self, reference_unit):
        self.REFERENCE_UNIT = reference_unit

    # HX711 datasheet states that setting the PDA_CLOCK pin on high for a more than 60 microseconds would power off the chip.
    # I'd recommend it to prevent noise from messing up with it. I used 100 microseconds, just in case.
    def power_down(self):
        GPIO.output(self.PD_SCK, False)
        GPIO.output(self.PD_SCK, True)
        time.sleep(0.0001)

    def power_up(self):
        GPIO.output(self.PD_SCK, False)
        time.sleep(0.0001)

############# EXAMPLE


hx = HX711(14, 15) # verde = 14, amarelo = 15 - INICIA PD_OUT Sendo pino 14 e DOUT sendo pino 15
hx.set_scale(1000) # seta a escala
hx.set_reference_unit(12) # seta a referencia (aqui foi feito a calibração, alterando essas duas funções)
hx.power_down() # reset no hx711
hx.power_up()   # reset no hx711
hx.tare()     # seta a tara, chama lá em cima esse código

# Daqui pra baixo é criado a tela e o programa principal, que chama as funções lá em cima

root = Tk() # chg --> Cria a tela principal do programa (Tkinter)
var = DoubleVar() # --> Cria a variável 'var' do tipo 'DoubleVar()', que é coisa interna do Tkinter (essa variável vai mostrar o peso na tela)
logo = PhotoImage(file="/home/pi/arthur/b300/balanca03.png") # Carrega o background e salva em 'logo'
root.attributes("-fullscreen", True) # Seta o programa como fullscreen (esconde botões pra fechar/minimizar e titulo)
root.config(cursor="none") # Esconde o ponteiro do mouse

# Esses códigos comentados são pra desenvolvermos depois
# A intenção é que a tela seja redimensionada automaticamente de acordo com a resolução do monitor
#scale_w = 1360/1920
#scale_h = 768/1080
#logo.subsample(scale_w, scale_h)

#w = 1000
#h = 650

#ws = root.winfo_screenwidth()
#hs = root.winfo_screenheight()

#x = (ws/2) - (w/2)
#y = (hs/2) - (h/2)

#root.geometry('%dx%d+%d+%d' % (w, h, x, y))

# Aqui começa o desenho da tela do programa com as atualizações das leituras do peso no monitor
w = Label(root, 
         justify=CENTER, 
         compound=CENTER, 
         padx=1, 
         bg="black", 
         textvariable = var, # variável texto recebe a leitura
         fg="white",
         font=("Arial", 190), 
         image=logo).pack()
		 
###### LOOP PRINCIPAL DO PROGRAMA #####
while True: # loop infinito
    try:
        val = hx.get_weight() # armazena o peso atual em 'val'
        var.set(val) # muda a variável 'var'(que está atribuída dentro do 'textvariable' dentro da tela) de acordo com o peso
        hx.power_down() # prepara o hx711 pra próxima leitura
        hx.power_up()
        time.sleep(0.5) # espera um tempo
        root.update_idletasks() # atualiza a tela do tkinter com o novo peso

		# código pra o raspberry pi quando apertar o botão vermelho
        while(GPIO.input(power_off) == True):
            count = 1            
            time.sleep(1)
            count = count - 1
            var.set(count)
            root.update_idletasks()
            if (count == 0):
                var.set("Bye!") # Escreve 'Bye!' na variável 'var'
                root.update_idletasks() # atualiza a tela com o novo valor dessa variável 
                os.system("sudo shutdown -h now") # Comando linux para desligar o raspberry pi    
				
    # Caso for apertado o X do programa ou alguma coisa do teclado, o programa fecha.    
    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
###### LOOP PRINCIPAL DO PROGRAMA #####
		
		
##### Códigos abaixo para testes de outras funcionalidades		
		
#def callback(*args):
    #val = hx.get_weight()
    #var.set(val)
    #hx.power_down()
    #hx.power_up()
    #time.sleep(0.5)

#var.trace("w", callback)

#while True: 
    #try:
        #def callback(*args):
            #val = hx.get_weight()
            #var.set(val)
        #var.trace("w", callback)
	#val = hx.get_value()
        #val = hx.get_weight()
        #print(val)
        #var = DoubleVar()
        #var.set(val)
        #w = Label(root, textvariable=val) # chg
        #w.pack() # chg
        #root.mainloop() #chg
        
        #w = Label(root, justify=CENTER, compound = TOP, padx = 10, textvariable=var,image=logo).pack(side="right")
	#root.mainloop()
        
        #hx.power_down()
        #hx.power_up()
        #time.sleep(0.5)
    #except (KeyboardInterrupt, SystemExit):
        #cleanAndExit()       	  


# create Tk root widget
#root = Tk()   

# load image into logo variable  
#logo = PhotoImage(file="icon.png")
                      
# multi-line text
#explanation = """At present, only GIF and PPM/PGM
#formats are supported, but an interface exists to 
#allow additional image file formats to be added 
#easily."""		  

# second label inside root
#w = Label(root,  
	  #justify=CENTER,
	  #compound = TOP,	
	  #padx = 10,
	  #text=explanation,
	  #image=logo).pack(side="right")

# start view
#root.mainloop()
