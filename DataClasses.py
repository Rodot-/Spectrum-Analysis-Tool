import sys
import numpy as np
import time
import operator
from DataManager import *
from astropy.io import fits

if sys.version_info[0] < 3:
	import Tkinter as Tk
else:
	import tkinter as Tk

PATH = 'downloads/SDSS/'

class Data:

	def __init__(self):

		self.MainDataArray = self.LoadDataFile() #All Data
		print "Conversion to Spectra Complete"

		self.MainDataArray = self.SortBy('REDSHIFT')
	
		print "Sorting Complete"
		self.DataPosition = 0
		CachedData = [[]] #Stores Data from previously opened files
		self.currentDataArray = self.MainDataArray
		self.currentData = []
		self.DefineCurrentData()

		print "Setup Complete"	

		#self.DefineCurrentData()

		#print type(self.currentData)
		#print type(self.currentData[0])
		#print len(self.currentData[0])

		#self.currentData[0].getSpectrum()

		#self.ReleaseDataPoints()

		#print self.currentData[0].Flux
		#self.currentData[1].getSpectrum()
		#print self.currentData[0]['REDSHIFT']

		#self.NextGroup()

		#self.currentData[0].getSpectrum()

		#print self.currentData[0]['GroupID']
		#print self.currentData[0].Flux
		#print self.currentData[0]['REDSHIFT']

		#self.PreviousGroup()
		#print self.currentData[0].Flux
		#print self.currentData[0]['REDSHIFT']

		#print self.ReleaseDataPoints()

		#print self.currentData[0].dtype.names[0]

	def LoadDataFile(self): #Loads the Spectra data

		T0 = time.clock()

		RawData = getMatchesArray()

		DTYPE = RawData.dtype

		T1 = time.clock()

		print "Raw Data Loading Time: ", time.clock() - T0

		result = map(Spectrum, RawData)

		print "Data Conversion Time: ", time.clock() - T1

		return result

	def DefineCurrentData(self): #Builds the list of matching spectra	

		self.currentData = self.DefineData('GroupID', self.currentDataArray)

	def ViewMarkedData(self, Value, Parent): #Chose what kind of data to view, Value can be "interesting" or "not_interesting"

		self.currentDataArray = self.DefineData('Interesting', Parent, Value)

	def DefineData(self, Field, Parent, template = None): #defines a subset from a Parent of matching fields

		T0 = time.clock()

		if template == None: template = Parent[self.DataPosition][Field]

		matches = np.where(np.asarray(Parent)[Field] == template)

		print "Subset Creation Time: ", time.clock() - T0

		return [Parent[i] for i in matches[0]]

	def NextGroup(self): #Jump to the next Group

		T0 = time.clock()

		currentGroup = self.currentDataArray[self.DataPosition]['GroupID']

		Max = len(self.currentDataArray) - 1

		while self.currentDataArray[self.DataPosition]['GroupID'] == currentGroup:
			if self.DataPosition == Max:

				self.DataPosition = -1

			self.DataPosition += 1

		self.DefineCurrentData()
					
		print "Next Group Time: ", time.clock() - T0

	def PreviousGroup(self): #Jump to the previous group

		T0 = time.clock()

		currentGroup = self.currentDataArray[self.DataPosition]['GroupID']

		Max = len(self.currentDataArray)

		while self.currentDataArray[self.DataPosition]['GroupID'] == currentGroup:

			if self.DataPosition == 0:

				self.DataPosition = Max

			self.DataPosition -= 1

		self.DefineCurrentData()
					
		print "Prev Group Time: ", time.clock() - T0

	def ReleaseDataPoints(self): #returns the wavelength and flux of group

		T0 = time.clock()

		for i in self.currentData:

			if len(i.Flux) == 0:

				i.getSpectrum()

		print "Release Data Time: ", time.clock() - T0

		return [[Spectra.Flux, Spectra.Lambda] for Spectra in self.currentData]

	def SortBy(self, key): #Sorting by Schwartzian transform

		T0 = time.clock()

		index = np.argsort(np.asarray(self.MainDataArray),order = key)

		print "Sorting Time: ", time.clock() - T0

		return [self.MainDataArray[i] for i in index]

	def ToggleInteresting(self):

		if self.currentData[0]['Interesting'] == 'Not_Interesting':
			NewFlag = 'Interesting'
		else:
			NewFlag = 'Not_Interesting'

		self.ViewMarkedData(NewFlag, self.MainDataArray)
		self.DefineCurrentData()

class Spectrum(np.ndarray): #A class containing Information about a spectrum

	def __new__(cls, DataPoint):

		obj = np.asarray(DataPoint).view(cls)
		obj.Flux = []
		obj.Lambda = []
		return obj

	def __len__(self):

		return len(self.dtype)		

	def getSpectrum(self):

		Data = fits.open("".join((PATH, str(self['FILENAME']))))

		self.Flux = Data[1].data['flux']
		self.Lambda = 10**Data[1].data['LogLambda']
		
		Data.close()	

	def __array_finalize__(self, obj):

		self.Flux = getattr(obj, 'Flux', [])
		self.Lambda = getattr(obj,'Lambda',[])

#data = Data()
#print "Done"
