from astropy.io import fits
import os
from Config import bcolors
import Config
import numpy as np
import math
import time
import MatchingFunctions
import fileinput
import sys
from multiprocessing import Pool

BuildFitsList = MatchingFunctions.BuildFitsList
FHV = MatchingFunctions.FindHeaderValue

def GetRaDec(): #Gets a filename, ra and dec of a spectra for matching

	print("Getting Data")

	try:

		temp = np.loadtxt("user/Matches.rep", delimiter=', ',dtype={'names':["GroupID","MJD","PLATEID","FIBERID","RA","DEC","REDSHIFT","FILENAME","Interesting"], 'formats': ["int","int","int","int","float","float","float","<S64","<S64"]})


		if len(temp) == 0:

			raise Exception("File Has No Data")

		else:

	        	CachedTable = set([(math.cos(i['RA']), i['DEC'],i['RA'],i['FILENAME'], i['REDSHIFT'], i['MJD'], i['PLATEID'],i['FIBERID']) for i in temp]) 

	except:

		print("Could not Load Matches.rep")

		temp = np.zeros((0), dtype = [('cos(RA)','<f8'),('DEC','<f8'),('RA','<f8'),('FILENAME', '<S64'),('Z','<f4'),('MJD','<i4'),('PLATE','<i4'),('FIBER','<i4')])
		CachedTable = set()

	print("Looking for New Files")

	FileList = set(os.listdir(Config.PATH)) - set(temp['FILENAME'])

	#if len(set(os.listdir("downloads/SDSS"))) < len(set(temp['FILENAME'])):

	#	raise Exception("Bad Math on FileList")

	FileList = set([i for i in FileList if i.endswith('.fits')])

	nFiles = len(FileList)

	TotalListLength = nFiles + len(CachedTable)

	print(bcolors.HEADER + str(nFiles) + " New Files Found" + bcolors.ENDC)

	print("Extracting Data...")

	RADEC = np.empty((TotalListLength), dtype = [('cos(RA)','<f8'),('DEC','<f8'),('RA','<f8'),('FILENAME', '<S64'),('Z','<f4'),('MJD','<i4'),('PLATE','<i4'),('FIBER','<i4')])

	RADEC[0:len(CachedTable)] = list(CachedTable)

	RADEC_index = len(CachedTable)

	t0 = time.time()
	P = Pool(4)

	RADEC[RADEC_index:] = P.map(BuildFitsList, FileList)

	#for i in map(BuildFitsList, FileList):
	#	RADEC[RADEC_index] = i
	#	RADEC_index += 1
	#	print RADEC_index

	#for i in iter(FileList):
	#	RADEC[RADEC_index] = BuildFitsList(i)
	#	RADEC_index += 1
	#	#print RADEC_index
	
	#RADEC[len(CachedTable):] = [BuildFitsList(i) for i in FileList]

	#print len(RADEC)
	print("Found " + str(TotalListLength) + " files in " + str(time.time()-t0))
	#raise Exception("STOP")

	return RADEC
	
def groupData(): #matches all data, exports to Matches.rep

        X = GetRaDec()
        print bcolors.HEADER + "Starting Matching", bcolors.ENDC
        X = np.sort(X, order = 'DEC')
	t0 = time.time()

        output = open('user/Matches.rep', 'wb')

	output.write('#GroupID, MJD, PLATEID, FIBERID, RA, DEC, REDSHIFT, FILENAME, ARGS, TAGS\n')

        DELTA = (2.0/60.0/60.0)**2 #2 arcseconds in degrees
	delta = 2.0/60.0/60.0 #sqrt(DELTA)
	OBJECTS = len(X)
        groupedObjects = [] #2D array: first entry in each row is an object, following entries are all objects within DELTA
        countdown = 0
        groupID = 0
	PLEASE_SKIP = set()
	def Scribble(obj): #Writes given data to the output file

		output.write(", ".join((str(groupID),str(obj['MJD']),str(obj['PLATE']),str(obj['FIBER']),str(obj['RA']),str(obj['DEC']),str(obj['Z']),obj['FILENAME'], 'Not_Interesting','None\n')))

        for i in xrange(OBJECTS):
                if i in PLEASE_SKIP:
                        PLEASE_SKIP.remove(i)

                else:
                        #singleGroup = [X[i]]
			Scribble(X[i])
                        #compare object at X[i] with X[i - 1] and lower, stop when DEC diff. is larger than DELTA
                        j = i - 1
                        while j >= 0 and X[i]['DEC'] - delta < X[j]['DEC']:
                                if DELTA > (X[i]['cos(RA)']-X[j]['cos(RA)'])**2 + (X[i]['DEC']-X[j]['DEC'])**2:
                                        #singleGroup.append(X[j])
					Scribble(X[j])
                                        PLEASE_SKIP.add(j)
                                j -= 1
                        #repeat, but with X[i + 1] and higher 
                        j = i + 1
                        while j < OBJECTS and X[i]['DEC'] + delta > X[j]['DEC']:
                                if DELTA > (X[i]['cos(RA)']-X[j]['cos(RA)'])**2 + (X[i]['DEC']-X[j]['DEC'])**2:
                                        #singleGroup.append(X[j])
					Scribble(X[j])
                                        PLEASE_SKIP.add(j)
                                j += 1
                        
                        groupID += 1
			#for obj in singleGroup:

			#	output.write(str(groupID) + ', ' + str(obj['MJD'])+', '+str(obj['PLATE'])+', '+str(obj['FIBER'])+', '+str(obj['RA'])+', '+str(obj['DEC'])+', '+str(obj['Z']) + ', ' + obj['FILENAME']+ ', ' + 'Not_Interesting' + '\n')

	output.close()
	print "Done Matching"

	print str(len(X)) + " Objects Matched in " + bcolors.BOLD + str(time.time() - t0) + " Seconds" + bcolors.ENDC


def saveInterestingObjects(DataArray): #Saves the list of interesting objects

	#Get all objects tagged "Interesting"

	InterestingList = [i for i in DataArray if i['Interesting'] == 'Interesting']

	InterestingFile = open('user/InterestingMatches.csv','wb')
        InterestingFile.write("#MJD, PLATEID, FIBERID, RA, DEC, Z, FILENAME, ARGS\n")

	#Saves these objects in the same format as above

	for j in InterestingList:

		InterestingFile.write(str(j['MJD'])+', '+str(j['PLATEID'])+', '+str(j['FIBERID'])+', '+str(j['RA'])+', '+str(j['DEC'])+', '+str(j['REDSHIFT']) + ', ' + j['FILENAME']+ ', ' + 'Interesting' + '\n')

		#InterestingFile.write(str(j[0]) + '\n')
	InterestingFile.close()


	print bcolors.OKGREEN, "Saved", bcolors.ENDC

def getMatchesArray(InterestingFile = 'user/InterestingMatches.csv'): #Parses the MAtches.rep file into an array of matches spectra
	if not os.path.isfile('user/Matches.rep'):

		print bcolors.WARNING
		print "Could not Locate 'Matches.rep'",
		print bcolors.ENDC
		print "Would You Like to Build it From", Config.PATH , "?"
		yn = raw_input("y/N: ").upper()
		if yn == 'Y':
			groupData()
			return getMatchesArray()
		else:
			sys.exit(2)

	try:

		InterestingFlag = np.loadtxt(InterestingFile,delimiter = ', ',usecols = (5,6,8), dtype={'names':['REDSHIFT','FILENAME', 'TAGS'], 'formats': [">f8","<S64","<S128"]})

		if len(InterestingFlag) == 0:
			raise Exception("No Data")

	except:

		try:
			return getMatchesArray('user/Autosave.csv')
		except:
			InterestingFlag = []

	matchList = np.loadtxt("user/Matches.rep", delimiter=', ', dtype={'names':["GroupID","MJD","PLATEID","FIBERID","RA","DEC","REDSHIFT","FILENAME","Interesting", "TAGS"], 'formats': ["int","int","int","int","float","float","float","<S64","<S64","<S256"]})

	print bcolors.OKBLUE,
	print "Text File Loaded", bcolors.ENDC
	print "Number of Interesting Files: ", len(InterestingFlag)
	print "Total Number of Files: ", len(matchList)

	IDlist = dict(zip(matchList['FILENAME'], matchList))
	for i in InterestingFlag:
		IDlist[i['FILENAME']]['TAGS'] = i['TAGS']
		IDlist[i['FILENAME']]['Interesting'] = 'Interesting'		
		IDlist[i['FILENAME']]['REDSHIFT'] = i['REDSHIFT']

	return matchList

def ExportInterestingCoords():
	
	Writer = open("ExportedMatches.csv",'wb')

	Writer.write("#GroupID, MJD, PLATEID, FIBERID, RA, DEC, Z\n")

	Array = getMatchesArray()	

	values = [i for i in Array if i['Interesting'] == "Interesting"]

	for j in values:

		Writer.write(str(j['GroupID'])+', ')
		MJD = j['MJD']
		PLATEID = j['PLATEID']
		FIBERID = j['FIBERID']
		RA = j['RA']
		DEC = j['DEC']
		Z = j['REDSHIFT']
		Writer.write(str(MJD)+', '+str(PLATEID)+', '+str(FIBERID)+', '+str(RA)+', '+str(DEC)+', '+str(Z)+'\n')
	Writer.close()


#ExportInterestingCoords()
#groupData()
#print getMatchesArray()
