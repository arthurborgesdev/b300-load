#!/bin/sh

usr_type = ""
while [ "usr_type" != "end" ]
do
	echo "Type anything to run (end to quit)"
	read usr_type
	hx711 | python3 balanca.py
done
