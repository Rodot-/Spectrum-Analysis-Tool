#from astropy.io import fits
#import os
#import HTTPServerManager as HTTP
#import numpy as np
import math
import os
import time
import fileinput
#import eventlet
#from FileManager import LoadServers
#import resource
#import time
#import sys
INFO = ['DECOBJ','RAOBJ','Z','MJD','PLATEID','FIBERID']
#S = LoadServers()

#TotalTransfers = 0
#AttemptedTransfers = 0
#POOL_SIZE = 8
#INDOORPOOL_SIZE = 1000

#resource.setrlimit(resource.RLIMIT_NOFILE, (2048,2048))

#pool = eventlet.GreenPool(size = 200000)
#indoorPool = eventlet.GreenPool(size = INDOORPOOL_SIZE)
def FileInputList(FILELIST):

	for x in fileinput.input(FILELIST):

		BODY = x.read()

		x.close()

		Header = [FindHeaderValue(raw, BODY) for raw in INFO]



def BuildFitsList(path):

	info = INFO

	READ = os.read

	with open("".join(('downloads/SDSS/',path)),'rb') as FILE:

		fd = FILE.fileno()

		BODY = READ(fd, 1024)

        	Header = [FindHeaderValue(raw,BODY) for raw in info]
	
	return (math.cos(Header[1]), Header[0], Header[1], path, Header[2], Header[3], Header[4], Header[5])

'''
def writeFitsHeader(body):

	global TotalTransfers

	for raw in INFO:

		Matches.write(str(FindHeaderValue(raw, body)) + ',')

	Matches.write(DATE + '\n')

	TotalTransfers += 1
'''

def FindHeaderValue(TEXT, body):

	pos = body.find(TEXT)

	start = body.find("=",pos)+1

	end = body.find("                                              ", start)

	raw = body[start:end]

	StringTest = raw.find("'")
	
	if StringTest == -1:

		if raw.find('.') != -1:

			return float(raw)

		else:

			return int(raw)
	
	else:		
		
		return raw[StringTest+1:raw.find(" ",1)]
'''
def Crawl(url):

	try:

		writeFitsHeader(eventlet.green.urllib2.urlopen(url).read())

		print "Successfully Connected to Server" 

	except:

		#print "Could Not Connect to Server.  Try taking in a bit slower."
		return url	

	return 'None'


def BuildFileList(server, path):

	LOC = HTTP.URL(server[1]+path)

	DirFiles = LOC.nlst()

	return [server[1] + path + i for i in DirFiles if i.endswith('.fits')]

def BuildFullFileList(Limits):

	FullList = []

	extension = '0'

	for n in range(Limits[0], Limits[1]):

		if n >= 1000:

			extension = ''
		try:

			#FullList += BuildFileList(S[1], '1d_26/' + extension + str(n) + '/1d/')

			FullList += BuildFileList(S[2], '/' + str(n) + '/')

			#print 'Full List Length:', len(FullList)

		except:

			print "Invalid URL"

	return FullList

def getTheData(Limits):

		pool = eventlet.GreenPool(size = POOL_SIZE)

		global AttemptedTransfers

		FailedURLs = []

		FullFileList = BuildFullFileList(Limits)

		print "Got File List"
	
		AttemptedTransfers += len(FullFileList)

		for i in pool.imap(Crawl, FullFileList):

			#print i
			'None'
			if i != 'None':
				FailedURLs.append(i)

	
		#print len(FailedURLs)

		while len(FailedURLs) > 0:

			FullFileList = [ n for n in FailedURLs ]

			FailedURLs = []
		
			for i in pool.imap(Crawl, FullFileList):

				'None'
				if i != 'None':
					FailedURLs.append(i)


			print len(FailedURLs), 'Failed URLs'

'''

