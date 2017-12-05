
# -*- coding: utf-8 -*-
import math
import time
import inspect
import numpy as np
from picoscope import ps6000
from matplotlib.mlab import find
import pylab as pl
import xlwt
import argparse
import decimal


class energyMeasure():
	def __init__(self):
		self.ps = ps6000.PS6000(connect=False)
		self.mCurr = []
		self.mDur = []
		self.sdCurr = []
		self.numberOfSamples=0
		self.captureLength = CLENGTH * 1E-3
		self.threshold = THRESHOLD
		self.samplingfreq = SAMPLINGFREQ
		self.capturesampleNo = self.captureLength * (self.samplingfreq * 1E6)
		self.containerA= []
		self.containerB = []
	
	def openScope(self):
		self.ps.open()

		self.ps.setChannel("A", coupling="DC", VRange=1, probeAttenuation=10)
		self.ps.setChannel("B", coupling = "DC", VRange = 1 , probeAttenuation=10)
		self.ps.setChannel("C", enabled= False)
		self.ps.setChannel("D", enabled=False)
		res = self.ps.setSamplingFrequency(self.samplingfreq * 1E6,int(self.capturesampleNo))

		self.sampleRate = res[0]
		print("Sampling @ %f MHz, %d samples"%(res[0]/1E6, res[1]))
		#Use external trigger to mark when we sample
		self.ps.setSimpleTrigger(trigSrc="B",enabled=False)

	def closeScope(self):
		self.ps.close()
	def armMeasure(self):
		self.ps.runBlock()


	def measure(self, filename):
		#setting the maximum number of waveform = 3000 -> 5min*60s*1000*ms*100= 300 000 waveforms
		i=0
		while(i<300000):
			self.armMeasure()
			while(self.ps.isReady() == False):pass
			dataA = self.ps.getDataV("A", int(self.capturesampleNo))
			dataB = self.ps.getDataV("B", int(self.capturesampleNo))
			self.containerA.append(-dataA)
			self.containerB.append(dataB)
			i=i+1

	def plotformat(self):
		self.containerA = np.asarray(self.containerA)
		self.containerB = np.asarray(self.containerB)
		print("The measurments contains:" + str(len(self.containerA))+"waveforms")                                                   
		fig	= pl.figure(figsize=(20,5))
		
		for i in range(len(self.containerA)):
			print("Working on plotting waveform "+str(i)+"of"+str(len(self.containerA)-1))  
			ax 	= 	fig.add_subplot(1,1,1)

			# major ticks every 15, minor ticks every 5                                      
			ymajor_ticks = np.arange(-0.500, 0.500, 0.020)                                              
			yminor_ticks = np.arange(-0.500, 0.500, 0.010)
			
			xmajor_ticks = np.arange(0, 500, 10)                                              
			xminor_ticks = np.arange(0, 500, 5)

			ax.set_xticks(xmajor_ticks)                                                       
			ax.set_xticks(xminor_ticks, minor=True)                                           
			ax.set_yticks(ymajor_ticks)                                                       
			ax.set_yticks(yminor_ticks, minor=True)
			ax.grid(which='minor', alpha=0.2)                                                
			ax.grid(which='major', alpha=0.5)   
			pl.suptitle('Waveform ' +str(i), fontsize = 12)
			ax.set_xlabel('Sample number of 100 ms')
			ax.set_ylabel('Voltage')
			pl.plot(self.containerA[i], linewidth= 0.5)
			pl.plot(self.containerB[i], linewidth= 0.5)
			pl.rc('grid', linestyle="-", color='black')
			pl.savefig("log\currentconsumption"+str(i)+args.experimentName+".png")
			#time.sleep(3)
			pl.clf()
		pl.close()
                                                 

	#Function used for viewing data after it has been analyzed
	def calculate_energy_consumption(self):
		fix_period=[1,10,60,1800,3600,14399,14400,15551700,15552000]
		t= [60,3600,86400,2592000,31536000]
		v_sleep, T_sleep, v_wake,T_wake,v_acq, T_acq, v_track, T_track = 2*1E-3,0,93.45*1E-3,4,79*1E-3,0,72*1E-3,1

		P_sleep = v_sleep*v_sleep
		P_wake  = v_wake*v_wake
		P_acq   = v_acq*v_acq
		P_track = v_track*v_track
		
		print(P_sleep)
		print(P_wake)
		print(P_acq)
		print(P_track)

		columns,rows= len(fix_period),len(t)
		Energy_consumption = [[0 for x in range(columns)] for y in range(rows)]
		print(Energy_consumption)

		i_iterator= 0
		j_iterator= 0

		for i in t:
			for j in fix_period:
				if(j_iterator>columns-1):
					j_iterator = 0   
				if((j<5) or (j>i) ):
					print(i_iterator,j_iterator)
					Energy_consumption[i_iterator][j_iterator]= -1
					j_iterator = j_iterator +1
					continue
				elif(j<14400):
					T_acq   = 1
				elif (j>14399 and j<15552000):
					T_acq   = 30      
				elif(j == 15552000):
					T_acq   = 35
				print("i",i)
				print("j=",j)
				print("T_acq=",T_acq)
				print("T_wake=",T_wake)
				print("T_track= ", T_track)
				T_sleep     = j - T_wake - T_acq - T_track 
				print("T_sleep=", T_sleep)
				Energy_consumption[i_iterator][j_iterator] = (P_sleep*T_sleep + P_wake*T_wake + P_acq*T_acq + P_track*T_track)*i/j
				print("Energy_consumption:",Energy_consumption[i_iterator][j_iterator])
				j_iterator = j_iterator +1

			i_iterator = i_iterator +1
			if(i_iterator>rows-1):
				i_iterator = 0  
		print (Energy_consumption)
		book = xlwt.Workbook()
		sh = book.add_sheet("Sheet 1")
		style = xlwt.XFStyle()
		# font
		font = xlwt.Font()
		font.bold = True
		style.font = font
    
		for i in range(columns):
			for j in range(rows):
				sh.write(i,j,Energy_consumption[j][i])
		book.save('dataa.xls')

if __name__ == "__main__":


	parser = argparse.ArgumentParser(description='Get statistics.')
	parser.add_argument('-e', dest='experimentName', type=str,required=True, help='Name of the experiment')
	parser.add_argument('-t', dest='threshold', type=float,required=True, help='Trigger Voltage Threshold')
	parser.add_argument('-s', dest='maxsamples', type=int, required=True, help='Number of data samples for statistical analysis.')
	parser.add_argument('-F',dest='samplingFreq', type=float, required=True, help='Sampling frequency in MS/s.')
	parser.add_argument('-v', dest='voltage', type=float, required=True, help='Voltage to power up the board')
	parser.add_argument('-c', dest='captureLen', type=float, required=True, help='Capture duration of each waveform in msec')

	args = parser.parse_args()
	THRESHOLD = args.threshold
	SAMPLINGFREQ = args.samplingFreq
	FILENAME = "excel\ " + args.experimentName + ".xls"
	CLENGTH = args.captureLen
	em = energyMeasure()
	em.openScope()
	try:
			start= time.time()
			em.measure(args.experimentName)
			end= time.time()
			print("Execution time=",end-start)
			em.plotformat()
			em.output()
		
		#em.output(FILENAME,args.experimentName,args.voltage,THRESHOLD)
	except KeyboardInterrupt:
		end= time.time()
		print("Execution time=",end-start)
		em.plotformat()
		em.output()
		#em.output(FILENAME,args.experimentName,args.voltage,THRESHOLD)
		pass
	em.closeScope()

	#python energymeasure.py -e idag -t 0 -s 1 -F 0.005 -v 1 -c 100