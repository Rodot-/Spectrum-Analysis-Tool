'''
Program Name: SpectralFileConversionTool.py

Author: John T. O'Brien

Purpose: Changes the formats of spectrum files to be used in the Spectrum Analysis tool.  Helps the tool interpret data from DR7 or earlier when comparing to DR8 or later.  Also, significantly reduced the file size of each data file.

Instruction: Place this program in the same directory as your "downloads" folder used for the Spectrum Analysis Tool.  Run $ python SpectralFileConversionTool.py from the console.  This tool does not need to be run on data from DR8 or above, but it will significantly reduce the file sizes.  This tool does not need to be run on DR7 or earlier as long as no data from DR8 or later is present. 

Note: In order to run, you must have the most recent version of astropy.  Use "$ conda update astropy" to update to the most recent version.

Command Line Arguments:

-c //Run Conversion

--indir=DIRECTORY // Input Directory (Default is downloads/SDSS/)

--outdir=DIRECTORY // Output Directory (Default is downloads/SDSS)
	// **Will Overwrite Directory Contents**

'''
#from __future__ import print_function
from astropy.io import fits
import sys
import numpy as np
import os
import getopt

if os.path.isfile('downloads/target_fibermap.fits'): #Only Needed For Rev-Map

        Maps = fits.open('downloads/target_fibermap.fits')
        maps = np.asarray(Maps[1].data)
        Maps.close()
        print "Opened Fibermap"

else:

        print 'Cant Find target_fibermap.fits'

def ChangeSpec(FileName): #This is the function that actually does the reformatting

	InputFile = "/".join((InputDirectory, FileName))
	OutputFile = "/".join((OutputDirectory, FileName))

	with fits.open(InputFile) as Sdata:#Opens the .fits file you want to modify

		try:

			if Sdata[0].header['EXPID01'] == 'Converted': #Checks if this file has already been converted.  If so, closes the file, and ends the function
		
				Sdata.close() 
	
				return 0
	
		except:

			print "Unknown Error"

		MJD = Sdata[0].header['MJD'] #Gets the MJD
	
		PLATE = Sdata[0].header['PLATEID'] #Gets the Plate ID
	
		FIBER = Sdata[0].header['FIBERID'] #Gets the Fiber ID
	
		COEFF0 = Sdata[0].header['COEFF0'] #Gets COEFF0
 
		COEFF1 = Sdata[0].header['COEFF1'] #Gets COEFF1
	
		try: #Data comes from spSpec- format 
	
			Z = Sdata[0].header['Z'] #Redshift
	
			SPEC = Sdata[0].data[0] #Spectrum Data
		
			RA = Sdata[0].header['RAOBJ'] #RA
	
			DEC = Sdata[0].header['DECOBJ'] #DEC
		

		except: #data comes from spec- fomat
		
			Z = Sdata[2].data['Z'][0] #Redshift

			SPEC = Sdata[1].data['flux'] #Spectrum
		
			RA = Sdata[0].header['PLUG_RA'] #RA
		
			DEC = Sdata[0].header['PLUG_DEC'] #DEC
		
		headers = fits.Header() #Defines new headers
		
		#Setting up headers
		
		headers.set('RAOBJ', RA)
		headers.set('DECOBJ', DEC)
		headers.set('MJD', MJD)
		headers.set('PLATEID', PLATE)
		headers.set('FIBERID', FIBER)
		headers.set('COEFF0', COEFF0)
		headers.set('COEFF1', COEFF1)
		headers.set('Z', Z)
		headers.set('EXPID01', 'Converted')
	
		LOGLAM = Sdata[1].data['loglam']	

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
	
		Overwrite(InputFile)

		hdulist.writeto(OutputFile) #Writes the new HDU lsit with the original file name
		Sdata.close(InputFile) #Closes the .fits file





def ChangeBOSS(FileName): #Converts Data from BOSS reverberation mapping.  Depreciated

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


def RemoveExisting(FileName): #Removes FileName

	if os.path.isfile(FileName): #Check if the old file exists and removes it
		os.system(" ".join(("rm",FileName)))

def DoNothing(arg=None): #Does nothing.  I promise

	pass

ChangeSDSS = ChangeSpec #For Version transition Purposes

def ConvertDirectory(): #Converst all files in a directory.  Outputs Failed Files
	if InputDirectory != OutputDirectory:

		Cache = os.listdir(OutputDirectory)
		FileList = list(set(os.listdir(InputDirectory)) - set(Cache))
		
	else:
	
		FileList = os.listdir(InputDirectory)

	print len(FileList), "Files Found"	
	print "Running Conversion"

	with open('Failures.txt', 'wb') as Failures:

		Failures.write(" ".join((InputDirectory, OutputDirectory)))

		for File in FileList:
	
			try:
				print "Converting:", File
				if File.endswith('.fits'): ChangeSpec(File)

			except:

				Failures.write("".join((File,'\n')))
				print "Could Not Convert:", File


InputDirectory = 'downloads/SDSS' #Default InputDirectory
OutputDirectory = 'downloads/SDSS' #Default Output Directory
FunctionToRun = DoNothing

if len(sys.argv) > 1: #Command Line argument Handling

	try:
		opts, args = getopt.getopt(sys.argv[1:],"c",["indir=","outdir="])

	except getopt.GetoptError:

		print "Error: GetoptError"
		sys.exit(2)

	for opt, arg in opts:
		
		if opt == "--indir":

			InputDirectory = arg

		if opt == "--outdir":

			OutputDirectory = arg

		if opt == "-c":

			FunctionToRun = ConvertDirectory

#Determine whether or not to overwrite the directory

if InputDirectory == OutputDirectory:

	Overwrite = RemoveExisting

else:

	Overwrite = DoNothing


FunctionToRun() #Runs Whatever the command line tells it to


