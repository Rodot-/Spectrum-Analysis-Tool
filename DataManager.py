from astropy.io import fits
import os
import numpy as np
import math
import eventlet
import time

pool = eventlet.GreenPool(size = 2000000)

def BuildFitsList(path):

	try:

		fitsHeader = fits.open("downloads/SDSS/" + path)[0].header
		direct = "downloads/SDSS/"
	
	except:
		
		fitsHeader = fits.open("downloads/BOSS/" + path)[0].header
		direct = "downloads/BOSS/"

	try:
		
		#print "Good Path:",path

		RA = fitsHeader['RAOBJ']

		DEC = fitsHeader['DECOBJ']

		MJD = fitsHeader['MJD']
	
		PLATE = fitsHeader['PLATEID']

		FIBER = fitsHeader['FIBERID']
	
		Z = fitsHeader['Z']

	except:

		print "Bad File, Deleting"
		os.system("rm " + direct + path)
		return

	return (math.cos(RA), DEC, RA,  path, Z, MJD, PLATE, FIBER)

def GetRaDec(): #Gets a filename, ra and dec of a spectra for matching

	print "Getting Data"

        RADEC = []

	print "Looking For Files in downloads/SDSS..."

	for i in pool.imap(BuildFitsList, os.listdir("downloads/SDSS")):
		RADEC.append(i)
		print i[2]

	print "Looking For Files in downloads/BOSS..."

	for i in pool.imap(BuildFitsList, os.listdir("downloads/BOSS")):
		RADEC.append(i)
		print i

	print "Done Getting Data"
        return np.array(RADEC,dtype = [('cos(RA)','<f8'),('DEC','<f8'),('RA','<f8'),('FILENAME', '<S64'),('Z','<f4'),('MJD','<i4'),('PLATE','<i4'),('FIBER','<i4')] )

def groupData(): #matches all data, exports to Matches.rep

        X = GetRaDec()
        print "Starting Matching"
        X = np.sort(X, order = 'DEC')

	t0 = time.time()

        output = open('Matches.rep', 'w')

	output.write('#GroupID, MJD, PLATEID, FIBERID, RA, DEC, REDSHIFT, FILENAME, ARGS\n')

        DELTA = 2.0/60.0/60.0 #2 arcseconds in degrees
        groupedObjects = [] #2D array: first entry in each row is an object, following entries are all objects within DELTA
        countdown = 0
        groupID = 0
        for i in range(len(X)):
                if countdown < 0:
                        countdown = 0
			print "Negative Countdown Warning!"

                if countdown == 0:
                        countdown += 1
                        singleGroup = []
                        singleGroup.append(X[i])
                        #compare object at X[i] with X[i - 1] and lower, stop when RA diff. is larger than DELTA
                        j = i - 1
                        while j >= 0 and X[i]['DEC'] - DELTA < X[j]['DEC']:
                                if DELTA > math.sqrt((X[i]['cos(RA)']-X[j]['cos(RA)'])**2 + (X[i]['DEC']-X[j]['DEC'])**2):
                                        singleGroup.append(X[j])
                                        countdown += 1
                                j -= 1
                        #repeat, but with X[i + 1] and higher 
                        j = i + 1
                        while j < len(X) and X[i]['DEC'] + DELTA > X[j]['DEC']:
                                if DELTA > math.sqrt((X[i]['cos(RA)']-X[j]['cos(RA)'])**2 + (X[i]['DEC']-X[j]['DEC'])**2):
                                        singleGroup.append(X[j])
                                        countdown += 1
                                j += 1
                        
                        groupID += 1
			for obj in singleGroup:

				output.write(str(groupID) + ', ' + str(obj['MJD'])+', '+str(obj['PLATE'])+', '+str(obj['FIBER'])+', '+str(obj['RA'])+', '+str(obj['DEC'])+', '+str(obj['Z']) + ', ' + obj['FILENAME']+ ', ' + 'Not_Interesting' + '\n')

		countdown -= 1

	output.close()
	print "Done Matching"

	print str(len(X)) + " Objects Matched in " + str(time.time() - t0) + " Seconds"


def saveInterestingObjects(DataArray): #Saves the list of interesting objects

	#Get all objects tagged "Interesting"

	InterestingList = [i for i in DataArray if i['Interesting'] == 'Interesting']

	InterestingFile = open('InterestingMatches.rep','wb')
        InterestingFile.write("#MJD, PLATEID, FIBERID, RA, DEC, Z, FILENAME, ARGS\n")

	#Saves these objects in the same format as above

	for j in InterestingList:

		InterestingFile.write(str(j['MJD'])+', '+str(j['PLATEID'])+', '+str(j['FIBERID'])+', '+str(j['RA'])+', '+str(j['DEC'])+', '+str(j['REDSHIFT']) + ', ' + j['FILENAME']+ ', ' + 'Interesting' + '\n')

		#InterestingFile.write(str(j[0]) + '\n')
	InterestingFile.close()


	print "Saved"

def getMatchesArray(): #Parses the MAtches.rep file into an array of matches spectra

	#Matches = open('Matches.rep','rb')

	try:

		InterestingFile = np.loadtxt('InterestingMatches.rep',delimiter = ', ', dtype={'names':['MJD','PLATEID','FIBERID','RA','DEC','REDSHIFT'], 'formats': ["int","int","int","float","float","float"]})

		InterestingFlag = [str(i['MJD']) + str(i['PLATEID']) + str(i['FIBERID']) for i in InterestingFile]


	except:

		InterestingFlag = []

	#matchList = []

	matchList = np.loadtxt("Matches.rep", delimiter=', ', dtype={'names':["GroupID","MJD","PLATEID","FIBERID","RA","DEC","REDSHIFT","FILENAME","Interesting"], 'formats': ["int","int","int","int","float","float","float","<S64","<S64"]})

	for i in matchList:

		if str(i['MJD'])+str(i['PLATEID'])+str(i['FIBERID']) in InterestingFlag:

			i['Interesting'] = 'Interesting'


	#for line in Matches:

	#	matchList.append(line.split(', '))


	#for line in Matches:

	#	matchList.append([])
		
	#	matchList[-1].append(int(line[0:line.find(',')])) #gets the group id
	#	matchList[-1].append([])	

	#	while pos+24 < len(line): #lists all the file names
	#		matchList[-1][-1].append(line[line.find('{',pos)+1:line.find('},',pos)])
	#		pos = line.find('},',pos)+2

	#	matchList[-1].append(len(matchList[-1][-1]))

	#	if matchList[-1][0] in InterestingFlag:		

	#		matchList[-1].append('Interesting')
		
	#	else:
	
	#		matchList[-1].append('Not_Interesting')


	#	matchList[-1].append(float(line[line.rfind('@')+1:line.rfind(',')]))

	#Matches.close()

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
