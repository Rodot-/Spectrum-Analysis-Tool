'''
This Program can read in a table of MJD,PLATE,FIBER values and look for the appropriate spectra file


'''
from FileManager import *
import sys
import eventlet
import os
import math

Gpool = eventlet.GreenPool(size = 100)

FileName = sys.argv[1]

LocationList = open(FileName,'rb')
URLlist = []

def GetDR7Directory(MJD,PLATE,FIBER):

	server = S[1][1]
	PLATEZeros = ''
	FIBERZeros = ''
	for i in range(3 - int(math.log(int(PLATE),10))):
		PLATEZeros += '0'
	for i in range(2 - int(math.log(int(FIBER),10))):
		FIBERZeros += '0'
	if int(PLATE) == 1000:
		PLATEZeros = ''
	
	FileName = 'spSpec-' + MJD + '-' + PLATEZeros + PLATE + '-' +  FIBERZeros + FIBER + '.fit'
	DirectoryName = server + '1d_26/' + PLATEZeros + PLATE + '/1d/' + FileName
	return [DirectoryName, FileName]


def GetDR10Directory(MJD,PLATE,FIBER):

	server = S[2][1]
	Zeros = ''

	for i in range(3 - int(math.log(int(FIBER),10))):
		Zeros += '0'
	if int(FIBER) == 1000:
		Zeros = ''


	FileName = 'spec-' + PLATE + '-' + MJD + '-' + Zeros + FIBER + ".fits"
	DirectoryName = server + '/' + PLATE + '/' + FileName
	return [DirectoryName, FileName]


for line in LocationList:

	MJD = line[0:line.find(',')]
	PLATE = line[line.find(',')+1: line.find(',',line.find(',')+1)]
	FIBER = line[line.rfind(',')+1:len(line)-1]

	if int(MJD) < 55000:

		Info = GetDR7Directory(MJD,PLATE,FIBER)

	else:
		Info = GetDR10Directory(MJD,PLATE,FIBER)	

	Name = Info[1]
	Directory = Info[0]

	
	if Name.find('.fit') != -1 and not os.path.isfile("downloads/SDSS/" + Name):

		URLlist.append(Directory)

#print eventlet.green.urllib2.urlopen(URLlist[0]).read()
def fetch(url):
	try:
		body = eventlet.green.urllib2.urlopen(url).read()
		a = open("downloads/SDSS/" + url[url.rfind('/')+1:], 'wb')
		a.write(body)
		a.close()
		try:
			print "Updating"
			ChangeSDSS("downloads/SDSS/"+url[url.rfind('/')+1:])
		except:
			os.system("rm downloads/SDSS/" + url[url.rfind('/')+1:])
			print "Can't Use That One"
		return url[url.rfind('/')+1:]
	except:
	
		print "Bad URL:"
		return url

	
for i in Gpool.imap(fetch, URLlist):
	print i



	



