# b300-load (Electronic weight machine for a health campaign)

## What it is for?

To be used in a marketing campaign to encourage people to worry more about health.


## How it works?

The equipment consists of a Raspberry PI 3, 4 load cells and a hx711 module.

When the equipment is turned on, a Linux OS boots and calls the Python script. This script access the raspberry PI GPIOs, read data from the load cells and transfer the data to the monitor display through a HDMI port. The monitor then shows the weight of the person.

## Main files and its functionalities

**/research-links**

Contains the most part of the hyperlinks used in the research, that helped the development of the prototype.

**/bmkt.sh**

Runs the balanca.py script, until a keyboard key is pressed to terminate the program.

**/balanca.py**

Main file. Responsible to make the conversion between the HX711 meterings to String and to show the data on the screen using Tkinter. Contains routines to calibrate the weigth machine before reading the weight.

**/display.py**

File that contains the code to render the information on the screen. Used as a frame to render the weight.
