import serial
import os
import time
serdev = "COM3"
s= serial.Serial(serdev)
"""order= raw_input(" Enter E to turn on gps, D to turn off, or R to reset ")
while(1):
	if(order=="D"):
		order= "E"
	elif(order=="E"):
		order="D"
	s.write(order)
	print order
	time.sleep(1)
	s.close"""


while(1):
	order= raw_input(" Enter E to turn on gps, D to turn off, or R to reset ")
	if(order=="D"):
		order= "D"
	elif(order == "E"):
		order=="E"
	elif(order == "R"):
		order=="R"
	s.write(order)
	print order
	time.sleep(1)
	s.close




