from astropy.io import fits
import os
import urllib2
import ftplib
import HTTPServerManager as HTTP
import numpy as np
from DataManager import groupData
from Config import PATH
import sys
import datetime

FOLDERS = "downloads user resource debug".split()
DATE = str(datetime.date.today())

def CreateFolder(path):

	if not os.path.isdir(path): os.system(" ".join(("mkdir",path)))

def CheckFiles(): #Checks if the Following Directories Exist, Creats them if not

	for folder in FOLDERS: CreateFolder(folder)
	for debug_file in os.listdir('debug'):	
		if DATE not in debug_file:
			os.system("rm debug/"+debug_file)

CheckFiles()

DEBUG = "".join(('debug/Debug_log_',DATE,'.txt'))
sys.stderr = open(DEBUG,'a')
sys.stderr.write('\n===============================\nProgram Started on'+DATE+'\n\n===============================\n')

def LoadServers(): #Loads in server information from servers.rep
	
	#See servers.rep for more information
	with open("resource/servers.rep", 'rb') as servers:
		data = (line.split('\n') for line in servers.read().split('\n\n') if line[0:2] != r'//') #Load the groups of information
	return dict([(i[0],i[1:]) for i in data if len(i) > 2]) #Return Dict of the Data


def DownloadFits_Single(server, path): #Downloads a single fits file

	file_name = path[path.rfind('/')+1:]

	if server[0] == 'FTP': #Checks what kind of server we are looking at

		LOC = ftplib.FTP(server[1],server[2],server[3])

		LOC.cwd(path[0:path.rfind('/')]) #Adjusts the current directory

		with open("/".join((PATH,file_name)),'wb') as temp:

			LOC.retrbinary('RETR %s' % file_name, temp.write) #Saves the File

	elif server[0] == 'URL': #Checks the server we are using

		temp = urllib2.urlopen("".join((server[1], path)))

		body = temp.read()
	
		temp.close()

		with open("/".join((PATH, file_name)), 'wb') as download:

			download.write(body)


