#Update Script
#This script is used for updating 
#the structure of the Spectrum Analysis Tool
#This script should be run 
#each time it is downloaded to ensure the 
#most recent version of the tool works correctly

#Version 0.1
#Date: 06/09/2015
#Moves all user files to the user folder
import os, shutil
if __name__ == '__main__':
	files = ['InterestingMatches.csv','Autosave.csv','Matches.rep']
	for f in files:
		if os.path.isfile(f) and not os.path.isfile('user/'+f):
			shutil.move(f,'user/')	

#Connection with the update server
if __name__ == 'updater':
	import socket, sys
	with open('resource/info.txt','rb') as info: #Checking the version number
		for line in info:
			if line.upper().startswith('VERSION'):
				VERSION = line[8:].strip()

	HOST, PORT = '129.25.20.158',8000
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		sock.connect((HOST, PORT))
		sock.sendall(VERSION)
		recieved = sock.recv(1024)
		if recieved == 'GOOD VERSION':
			print "Version",VERSION,'up to Date.'
		else:
			print "Version out of date, please update."
	except:
		print "Update Server Unavailable at this time."

	finally:
		sock.close()

