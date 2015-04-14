from astropy.io import fits
import os
import urllib
import ftplib
import HTTPServerManager as HTTP
import numpy as np
import eventlet
from eventlet.green import urllib2
from SpectralFileConversionTool import ChangeSDSS, ChangeBOSS
from DataManager import groupData
pool = eventlet.GreenPool(size = 1000)

def CheckFiles(): #Checks if the Following Directories Exist, Creats them if not

	if not os.path.isdir("downloads"):

		os.system("mkdir downloads")

	if not os.path.isdir("downloads/BOSS"):

		os.system('mkdir downloads/BOSS')

	if not os.path.isdir("downloads/SDSS"):

		os.system('mkdir downloads/SDSS')

CheckFiles()

def LoadServers(): #Loads in server information from servers.rep
	
	servers = open("resource/servers.rep", 'rb') 

	serverlist = []

	for line in servers:

		if line[0] == '@': #Checks for a new entry
	
			serverlist.append([line[line.find(' ')+1:len(line)-1]])
	
		elif line[0] == '#': #Checks fro entry data

			serverlist[len(serverlist)-1].append(line[line.find(' ')+1:len(line)-1])

	servers.close()

	return serverlist


def DownloadFits_Single(server, path): #Downloads a single fits file

	if server[0] == 'FTP': #Checks what kind of server we are looking at

		LOC = ftplib.FTP(server[1],server[2],server[3])

		LOC.cwd(path[0:path.rfind('/')]) #Adjusts the current directory

		FileName = path[path.rfind('/')+1:] #Gets a file name

		temp = open("downloads/BOSS/"+FileName,'wb')

		LOC.retrbinary('RETR %s' % FileName, temp.write) #Saves the File

		temp.close()

		#Check for the target_fibermap.fits file and tries to get it

		if not os.path.isfile('downloads/target_fibermap.fits'):

			temp2 = open("downloads/target_fibermap.fits", 'wb')

			LOCtemp = ftplib.FTP(server[1], server[2], server[3])

			LOCtemp.cwd('bossredux')
	
			LOCtemp.retrbinary('RETR %s' % 'target_fibermap.fits', temp2.write)
			temp2.close()

		try:
			print "Updating"
			ChangeBOSS("downloads/BOSS/"+FileName)
		except:
			os.system("rm downloads/BOSS/"+FileName)
			print "Can't Use That One"

		if os.path.isfile('downloads/BOSS/'+FileName):
			os.system("rm downloads/BOSS/"+FileName)



	elif server[0] == 'URL': #Checks the server we are using

		#print server[1]

		temp = urllib.URLopener() #Creats URLopener instance

		return

		FileName = path[path.rfind('/')+1:] #Gets filename

		pool.spawn(temp.retrieve(server[1] + path, "downloads/SDSS/"+FileName)) #Saves the file name

		try:
			print "Updating"	
			ChangeSDSS("downloads/SDSS/"+FileName)

		except:
			os.system("rm downloads/SDSS/"+FileName)
			print "Can't Use That One"
	
		#if os.path.isfile('downloads/SDSS/'+FileName):
		#	os.system("rm downloads/SDSS/"+FileName)



def DownloadFits_All(server, path): #Saves all files in a directory

	if server[0] == 'FTP':

		LOC = ftplib.FTP(server[1],server[2],server[3])

		LOC.cwd(path)

	        DirFiles = LOC.nlst() #Gets a list of files

	        for i in DirFiles:

	                if i.find('.fit') != -1: #Check for fits

	                        if not os.path.isfile("downloads/BOSS/"+i):

					print "Getting", i
					DownloadFits_Single(server,path + i)


	if server[0] == 'URL':

		LOC = HTTP.URL(server[1]+path)
	
		DirFiles = LOC.nlst() #Gets a list of files

		############

		URLlist = [server[1] + path + i for i in DirFiles if i.find('.fit') != -1 and not os.path.isfile("downloads/SDSS/" + i)]

		def fetch(url):
			body = eventlet.green.urllib2.urlopen(url).read()
			a = open("downloads/SDSS/" + url[url.rfind('/')+1:], 'wb')
			a.write(body)
			a.close()
                        try:
                        	print "Updating"
                                ChangeSDSS("downloads/SDSS/"+url[url.rfind('/')+1:])

                        except:
                                os.system("rm downloads/SDSS/"+url[url.rfind('/')+1:])
                                print "Can't Use That One"

			return url[url.rfind('/')+1:]			


		for i in pool.imap(fetch, URLlist):
			print i

			#return temp, url[url.rfind('/')+1:]

		#for temp, FileName in pool.imap(fetch, URLlist):
		#	print FileName		
	
		#	#open("downloads/SDSS/" + FileName, 'wb').write(temp)

	        # #       try:
        	##              print "Updating"
                #	        ChangeSDSS("downloads/SDSS/"+FileName)

                #	except:
                #        	os.system("rm downloads/SDSS/"+FileName)
                #        	print "Can't Use That One"

	
		#####################

	print "Done Grabbing.  You Sure Are Greedy."	

S = LoadServers()

#DownloadFits_All(S[0], 'bossredux/v5_7_1/0000/')

#DownloadFits_All(S[1], '1d_26/0269/1d/')
'''
for n in range(266,2975):

	try:
		DownloadFits_All(S[1], '1d_26/0'+str(n)+'/1d/')
	except:
		try:
			DownloadFits_All(S[1], '1d_26/' + str(n) + '/1d/')
		except:

			print "No Available Data Here"

	print str((n - 266.0)/(2975-266.0))+"%"

'''

