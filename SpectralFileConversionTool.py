'''
Program Name: SpectralFileConversionTool.py

Author: John T. O'Brien

Purpose: Changes the formats of spectrum files to be used in the Spectrum Analysis tool.  Helps the tool interpret data from DR7 or earlier when comparing to DR8 or later.  Also, significantly reduced the file size of each data file.

Instruction: Place this program in the same directory as your "downloads" folder used for the Spectrum Analysis Tool.  Run $ python SpectralFileConversionTool.py from the console.  This tool does not need to be run on data from DR8 or above, but it will significantly reduce the file sizes.  This tool does not need to be run on DR7 or earlier as long as no data from DR8 or later is present. 

Note: In order to run, you must have the most recent version of astropy.  Use "$ conda update astropy" to update to the most recent version.
'''
#from __future__ import print_function
from astropy.io import fits
import sys
import numpy as np
import os


if os.path.isfile('downloads/target_fibermap.fits'):

        Maps = fits.open('downloads/target_fibermap.fits')
        maps = np.asarray(Maps[1].data)
        Maps.close()
        print "Opened Fibermap"

else:

        print 'Cant Find target_fibermap.fits'




def ChangeSDSS(FileName): #This is the function that actually does the reformatting

	Sdata = fits.open(FileName) #Opens the .fits file you want to modify

	if Sdata[0].header['EXPID01'] == 'Converted': #Checks if this file has already been converted.  If so, closes the file, and ends the function
	
		Sdata.close() 

		return 0

	MJD = Sdata[0].header['MJD'] #Gets the MJD

	PLATE = Sdata[0].header['PLATEID'] #Gets the Plate ID

	FIBER = Sdata[0].header['FIBERID'] #Gets the Fiber ID

	COEFF0 = Sdata[0].header['COEFF0'] #Gets COEFF0
 
	COEFF1 = Sdata[0].header['COEFF1'] #Gets COEFF1

	if MJD < 55000: #Data comes from DR7 or earlier 

		Z = Sdata[0].header['Z']

		SPEC = Sdata[0].data[0] #Spectrum Data
	
		RA = Sdata[0].header['RAOBJ'] #RA

		DEC = Sdata[0].header['DECOBJ'] #DEC
	
		headers = fits.Header() #Defines the new headers

		headers.set('RAOBJ', RA)
		headers.set('DECOBJ', DEC)


	else: #data comes from DR8 or Later
		
		Z = Sdata[2].data['Z'][0]

		SPEC = Sdata[1].data['flux'] #Spectrum
		
		RA = Sdata[0].header['PLUG_RA'] #RA
		
		DEC = Sdata[0].header['PLUG_DEC'] #DEC
		
		headers = fits.Header() #Defines the new headers
	
		headers.set('RAOBJ', RA)
		headers.set('DECOBJ', DEC)

	#Setting up headers
	headers.set('MJD', MJD)
	headers.set('PLATEID', PLATE)
	headers.set('FIBERID', FIBER)
	headers.set('COEFF0', COEFF0)
	headers.set('COEFF1', COEFF1)
	headers.set('Z', Z)
	headers.set('EXPID01', 'Converted')

	LOGLAM = np.arange(0,len(SPEC)) #Calculating log(lambda)
	LOGLAM = LOGLAM * COEFF1 + COEFF0

	#Setting up the columns (Make sure not to adjust formats!)
	col1 = fits.Column(name='flux',format='E', array=SPEC) 
	col2 = fits.Column(name='LogLambda',format='D', array=LOGLAM)
	
	#Creating column Definition
	cols = fits.ColDefs([col1,col2])

	#Making the Binary Table
	BinTabHDU = fits.BinTableHDU.from_columns(cols)

	#Creating the Primary HDU
	PrimHDU = fits.PrimaryHDU(header = headers)

	#Putting the HDU list together
	hdulist = fits.HDUList([PrimHDU,BinTabHDU])

	if os.path.isfile(FileName): #Check if the old file exists and removes it

	        os.system("rm "+FileName)


	hdulist.writeto(FileName) #Writes the new HDU lsit with the original file name
	Sdata.close(FileName) #Closes the .fits file





def ChangeBOSS(FileName):

	Sdata = fits.open(FileName) #Opens the .fits file you want to modify

	if Sdata[0].header['EXPID01'] == 'Converted': #Checks if this file has already been converted.  If so, closes the file, and ends the function
	
		Sdata.close() 

		return 0

	MJD = Sdata[0].header['MJD'] #Gets the MJD

	PLATE = Sdata[0].header['PLATEID'] #Gets the Plate ID

	FIBERLIST = Sdata[5].data['FIBERID'] #List of Fiber IDs

	COEFF0 = Sdata[0].header['COEFF0'] #Gets COEFF0
 
	COEFF1 = Sdata[0].header['COEFF1'] #Gets COEFF1

	SPECLIST = Sdata[0].data #List of Spectrum Data
	
	RALIST = Sdata[5].data['RA'] #List of RA

	DECLIST = Sdata[5].data['DEC'] #List of DEC
	
	mapIndex = []

	#Trying to match target_fibermap.fits to current file

	for i in range(len(maps)):

		for j in range(len(maps['MJD'][i])):

			mapIndex.append(i)

			mapIndex.append([maps['MJD'][i][j], maps['PLATE'][i][j], maps['FIBERID'][i][j]])


	#End matching attemp

	headers = fits.Header() #Defines the new headers

	#Setting up headers
	headers.set('MJD', MJD)
	headers.set('PLATEID', PLATE)
	headers.set('COEFF0', COEFF0)
	headers.set('COEFF1', COEFF1)
	headers.set('EXPID01', 'Converted')

	for n in range(len(SPECLIST)): #Making a bunch of Files for each quasar

		Index = mapIndex[mapIndex.index([MJD,PLATE,FIBERLIST[n]])-1]
		headers.set('FIBERID',FIBERLIST[n])
		headers.set('RAOBJ',RALIST[n])
		headers.set('DECOBJ',DECLIST[n])
		headers.set('Z', maps['ZFINAL'][Index])

		LOGLAM = np.arange(0,len(SPECLIST[n])) #Calculating log(lambda)
		LOGLAM = LOGLAM * COEFF1 + COEFF0

		NewFileName = FileName[0:FileName.rfind('/')+1]+'spSpec-'+str(MJD)+'-'+str(PLATE)+"-"+str(FIBERLIST[n])+".fit"

		#Setting up the columns (Make sure not to adjust formats!)
		col1 = fits.Column(name='flux',format='E', array=SPECLIST[n]) 
		col2 = fits.Column(name='LogLambda',format='D', array=LOGLAM)
	
		#Creating column Definition
		cols = fits.ColDefs([col1,col2])

		#Making the Binary Table
		BinTabHDU = fits.BinTableHDU.from_columns(cols)

		#Creating the Primary HDU
		PrimHDU = fits.PrimaryHDU(header = headers)

		#Putting the HDU list together
		hdulist = fits.HDUList([PrimHDU,BinTabHDU])

		if os.path.isfile(NewFileName): #Check if the old file exists and removes it

	        	os.system("rm "+NewFileName)
			print "These Files Already Exist:", FileName
			break

		hdulist.writeto(NewFileName) #Writes the new HDU lsit with the original file name
		print NewFileName

	Sdata.close(FileName) #Closes the .fits file
	if os.path.isfile(FileName):
		os.system("rm "+FileName)

'''
f = 0 #Counter

for i in os.listdir("downloads/BOSS"): #Looking for files in the "downloads" directory
         if os.path.isfile(os.path.join("downloads/BOSS",i)): #Check if the file is in the directory

		f += 1 #Count

		ChangeBOSS("downloads/BOSS/"+i) #runt the function

		#Print The count and the file name being looked at
		print str(f)+"  "+i+"     " 

'''
