
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
		self.allvalues = []
		self.numberOfSamples=0
		self.captureLength = CLENGTH * 1E-3
		self.threshold = THRESHOLD
		self.samplingfreq = SAMPLINGFREQ
		self.capturesampleNo = self.captureLength * (self.samplingfreq * 1E6)
	
	def openScope(self):
		self.ps.open()

		self.ps.setChannel("A", coupling="DC", VRange=1, probeAttenuation=10, BWLimited = 2)
		self.ps.setChannel("B", enabled = False)
		self.ps.setChannel("C", enabled= False)
		#self.ps.setChannel("C", enabled=False)
		self.ps.setChannel("D", enabled=False)
		res = self.ps.setSamplingFrequency(self.samplingfreq * 1E6,int(self.capturesampleNo))

		self.sampleRate = res[0]
		print("Sampling @ %f MHz, %d samples"%(res[0]/1E6, res[1]))
		#Use external trigger to mark when we sample
		#self.ps.setSimpleTrigger(trigSrc="NONE")

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
		print("Waiting for trigger")
		while(self.ps.isReady() == False):pass
		print("Sampling Done")
		print("captureSampleNo: ",int(self.capturesampleNo))
		print("Number of samples :",self.numberOfSamples)
		dataA = self.ps.getDataV("A", int(self.capturesampleNo))
		#print (dataA)
		#print (len(dataA))
		#self.allvalues.append(dataA)
		
		"""fig = pl.figure()
		pl.plot(dataA)
		pl.savefig("fig\currentconsumption"+str(em.numberOfSamples)+args.experimentName+".png")
		fig.clf()
		pl.close()"""
		"""
		dataB = self.ps.getDataV("B", int(self.capturesampleNo))
		indices = []
		for index in range(len(dataB)):
			if dataB[index] >= THRESHOLD:
				break;

		print("Index: ", index)
		if self.numberOfSamples == 0:
			pass
		if (index+1) < len(dataB):
			self.numberOfSamples = self.numberOfSamples + 1
			self.computeMeanAndStdevSubChannel(dataA[1:index], index)				
		"""

		"""#print "dataA:",self.rms(dataA)
		#dataB = self.ps.getDataV("B",int(self.capturesampleNo))
		#print "dataB:",self.rms(dataB)
		#temp= np.subtract(dataA,dataB)
		#temp= self.rms(temp)
		#print "rms:",temp
		self.allvalues.append(temp)
		if(self.capturesampleNo!=0):
			if(self.numberOfSamples%100==0):
				fig = pl.figure()
				pl.plot(self.allvalues)
				pl.savefig("fig\currentconsumption"+str(self.numberOfSamples)+filename+".png")
				fig.clf()
				pl.close()
				self.allvalues = []

		self.numberOfSamples = self.numberOfSamples + 1"""

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
	parser.add_argument('-c', dest='captureLen', type=float, required=True, help='Capture duration in msec')

	args = parser.parse_args()
	THRESHOLD = args.threshold
	SAMPLINGFREQ = args.samplingFreq
	FILENAME = "excel\ " + args.experimentName + ".xls"
	CLENGTH = args.captureLen
	em = energyMeasure()
	em.openScope()
	try:
		while (1):
			em.armMeasure()
			em.measure(args.experimentName)
		
		#em.output(FILENAME,args.experimentName,args.voltage,THRESHOLD)
	except KeyboardInterrupt:
		em.output(FILENAME,args.experimentName,args.voltage,THRESHOLD)
		"""fig = pl.figure()
		pl.plot(em.allvalues)
		pl.savefig("fig\currentconsumption"+str(em.numberOfSamples)+args.experimentName+".png")
		fig.clf()
		pl.close()"""
		pass
	em.closeScope()