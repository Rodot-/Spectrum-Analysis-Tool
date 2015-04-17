'''
This Program can read in a table of MJD,PLATE,FIBER values and look for the appropriate spectra file
'''
from FileManager import LoadServers
import sys
from Config import PATH
import eventlet
from eventlet.green import urllib2
import os
import math

def GetDirectory(MJD, PLATE, FIBER):

	server = S['DR12_SDSS'][1]
	Zeros = ''
	ZerosP = ''

	for i in range(3 - int(math.log(int(FIBER), 10))):
		Zeros = "".join((Zeros,'0'))
	if int(FIBER) == 1000:
		Zeros = ''

	for i in range(3 - int(math.log(int(PLATE), 10))):
		ZerosP = "".join((ZerosP,'0'))
	if int(PLATE) == 1000:
		ZerosP = ''

	FileName = "".join(('spec-' , ZerosP, PLATE , '-' , MJD , '-' , Zeros , FIBER , ".fits"))
	DirectoryName = "".join((server , ZerosP, PLATE , '/' , FileName))
	return [DirectoryName, FileName]

def fetch(url):
	try:
		body = eventlet.green.urllib2.urlopen(url).read()
		with open("downloads/" + url[url.rfind('/')+1:], 'wb') as a:
			a.write(body)
		return url[url.rfind('/')+1:]

	except urllib2.HTTPError:	
		print "Bad URL:"
		return url

if __name__ == '__main__':

	Gpool = eventlet.GreenPool(size = 100)
	FileName = sys.argv[1]
	LocationList = open(FileName,'rb')
	URLlist = []
	S = LoadServers()

	for line in LocationList:

		MJD,PLATE,FIBER = line[:-1].split(',')

		Info = GetDirectory(MJD, PLATE, FIBER)

		Name = Info[1]
		Directory = Info[0]

		URLlist.append(Directory)

	
	for i in Gpool.imap(fetch, URLlist):
		print i

	LocationList.close()

	



