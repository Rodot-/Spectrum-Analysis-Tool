from astropy.io import fits
import os
import urllib
import ftplib
import HTTPServerManager as HTTP
import eventlet
from eventlet.green import urllib2

pool = eventlet.GreenPool(200000)

def CheckFiles(): #Checks if the Following Directories Exist, Creats them if not

	if not os.path.isdir("downloads"):

		os.system("mkdir downloads")

	if not os.path.isdir("downloads/BOSS"):

		os.system('mkdir downloads/BOSS')

	if not os.path.isdir("downloads/SDSS"):

		os.system('mkdir downloads/SDSS')

CheckFiles()

def LoadServers(): #Loads in server information from servers.rep
	
	servers = open("servers.rep", 'rb') 

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

	elif server[0] == 'URL': #Checks the server we are using

		temp = urllib.URLopener() #Creats URLopener instance

		FileName = path[path.rfind('/')+1:] #Gets filename

		pool.spawn(temp.retrieve(server[1] + path, "downloads/SDSS/"+FileName)) #Saves the file name


def DownloadFits_All(server, path): #Saves all files in a directory

	if server[0] == 'FTP':

		LOC = ftplib.FTP(server[1],server[2],server[3])

		LOC.cwd(path)

	        DirFiles = LOC.nlst() #Gets a list of files

	        for i in DirFiles:

	                if i.find('.fit') != -1: #Check for fits

	                        if not os.path.isfile("downloads/BOSS/"+i):

					DownloadFits_Single(server,path + i)

	if server[0] == 'URL':

		LOC = HTTP.URL(server[1]+path)
	
		DirFiles = LOC.nlst() #Gets a list of files

		for i in DirFiles:

			if i.find('.fit') != -1: #Check for fits

				if not os.path.isfile("downloads/SDSS/" + i):	

					DownloadFits_Single(server,path + i)	
	
		

S = LoadServers()

#DownloadFits_All(S[0], 'bossredux/v5_7_1/0000/')

#DownloadFits_All(S[1], '1d_26/0266/1d/')

for n in range(278,280):
	DownloadFits_All(S[1], '1d_26/0'+str(n)+'/1d/')



