
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


	def rms(self,DATA):
		rms_val=0.0000000000000
		for i in range(len(DATA)):
			rms_val += math.pow(DATA[i],2)
		rms_val= rms_val/len(DATA)
		rms_val = math.sqrt(float(rms_val))
		return rms_val

	def voltagedrop(self, DATAA,DATAB):
		drop=[]
		for i in range(len(DATAA)):
			drop.append(float(DATAA[i]-DATAB[i]))
		return drop

	def computeMeanAndStdevSubChannel(self,subChannelA, to):
		for i in range(len(self.containerA)):
			
			self.mCurr.append(np.mean(subChannelA))
			self.sdCurr.append(np.std(subChannelA))
			fs = self.sampleRate / 1000
			self.mDur.append(to / fs)
			self.allvalues.append(subChannelA)

		print ("Number of samples: ", fs)
		print ("Duration: ", to / fs)
		print("MeanCurrent:", np.mean(subChannelA))
		print("StandardDeviation:", np.std(subChannelA))

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
                                                 


	def output(self, filename, x, y, z):
		book = xlwt.Workbook()
		sh = book.add_sheet("Sheet 1")
		style = xlwt.XFStyle()
		# font
		font = xlwt.Font()
		font.bold = True
		style.font = font
		variables = [x, y, z, (self.sampleRate/1E6), self.captureLength * 1E3, self.capturesampleNo]
		desc = ['TextName', 'Voltage(V)', "Thresh_Vol", "Sampling Freq", "Capture Length(ms)", "Capture Samples/calc"]
		
		for n, (v_desc, v) in enumerate(zip(desc, variables)):
			sh.write(n, 0, v_desc, style=style)
			sh.write(n, 1, v)
		n+=2
		sh.write(n,0,'Allvalues', style =style)
		index =1
		for m,e1 in enumerate(self.allvalues, n):
			sh.write(m, 0, 'allvalues'  + str(index))
			sh.write(m, 1, e1)
			print (m)
			print (e1)
			index += 1
		book.save(filename)
"""		sh.write(n, 0, 'SampleDuration(ms)', style=style)
		sh.write(n, 1, 'Duration(ms)', style=style)
		sh.write(n, 2, 'MeanCurrent(A)', style=style)
		sh.write(n, 3, 'StandardError',style=style)
		index = 1
		for m, e1 in enumerate(self.mDur, n+1):
			sh.write(m, 0, 'Sample'  + str(index))
			sh.write(m, 1, e1)
			index += 1
		
		for m, e2 in enumerate(self.mCurr, n+1):
			sh.write(m, 2, (e2))
		for m, e3 in enumerate(self.sdCurr, n+1):
			sh.write(m, 3, e3)

		m += 2
		sh.write(m,0,"Average", style=style)
		sh.write(m,1,np.mean(self.mDur))
		sh.write(m,2,np.mean(self.mCurr))
		sh.write(m,3,np.mean(self.sdCurr))
		
		power = np.mean(self.mCurr) * y
		m+=3
		sh.write(m,0,"Power(Watt)", style=style)
		sh.write(m,1, power)

		energy = (np.mean(self.mDur)/1000) * y * np.mean(self.mCurr)
		m+=1
		sh.write(m,0,"Energy(J)", style=style)
		sh.write(m,1, energy)"""

		#book.save(filename)


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