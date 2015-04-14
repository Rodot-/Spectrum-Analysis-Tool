import ftplib
import sys
import HTTPServerManager as HTTP
from FileManager import DownloadFits_Single, DownloadFits_All
from DataManager import groupData
try: 
	import Tkinter as Tk
except:
	try:
		import tkinter as Tk
	except:
		print "Can't Import Tkinter, Try Updating Python, or Installing Tkinter Manually."
		print "Cannot Continue, Goodbye."
		exit()


BOSS = ['FTP', 'sdssrm.obs.carnegiescience.edu','sdssrm','rev-map'] #FTP Server

SDSS = ['URL','http://das.sdss.org/spectro/']

SDSS12 = ['URL','http://mirror.sdss3.org/sas/dr12/sdss/spectro/redux/26/spectra/']

root = Tk.Tk()
root.wm_title('File Browser')

class Browser: #The Class of interest.  Allows user to browse all files on any ftp server

	def __init__(self,master, serverObject): #Init, obviously

		self.serverObject = serverObject

		self.currentPath = '' #Records the current path
		
		#Determining what kind of server it is and opening it

		if serverObject[0] == 'FTP':

			self.TABLE = ftplib.FTP(serverObject[1], serverObject[2], serverObject[3])

		elif serverObject[0] == 'URL':

			self.TABLE = HTTP.URL(serverObject[1])

		
		frame = Tk.Frame(master, height = 100, width = 50) #sets up frame
		frame.pack(expand = True, fill = Tk.BOTH)


		self.scroller = Tk.Scrollbar(frame, orient = Tk.VERTICAL) #Scrollbar
		self.listbox = Tk.Listbox(frame, yscrollcommand = self.scroller.set, height = 13, width = 42) #List box we use to display files and folders
		self.scroller.config(command = self.listbox.yview) #Configure Scrollbar	
		self.back = Tk.Button(frame, text = 'Back', command = self.Back) #This button takes you up one directory
		self.b = Tk.Button(frame, text = 'Select', command = self.NewDir) # this button allows you to select a file or folder to work with
			
		#Packing Up
		self.scroller.pack(side=Tk.RIGHT, fill = 'y')
		self.listbox.pack(fill = Tk.BOTH, expand = True)
		self.b = Tk.Button(frame, text = 'Select', command = self.NewDir)
		#Runs the matching program
		self.Match = Tk.Button(frame, text = 'Run Matching', command = groupData)

		#Grabs all fits files in the directory, dangerous
		self.GrabAll = Tk.Button(frame, text = 'Grab All', command = self.GrabAllFits)

		self.b.pack(side = Tk.LEFT, expand = True,fill = 'x')
		self.back.pack(side = Tk.LEFT, expand = True,fill = 'x')
		self.Match.pack(side = Tk.RIGHT, expand = True, fill = 'x')		
		self.GrabAll.pack(side = Tk.RIGHT, expand = True, fill = 'x')

		self.update(self.TABLE) #Update the listbox
	
	def update(self, TABLE): #Updates the listbox, makes files have blue text
		self.listbox.delete(0,Tk.END) #delete previous listbox entries
		for item in TABLE.nlst():
			self.listbox.insert(Tk.END, item)
			if item.find('.') != -1: #The color thing
				self.listbox.itemconfig(Tk.END, fg = 'blue')
	def GrabAllFits(self):

		DownloadFits_All(self.serverObject, self.currentPath)

	def NewDir(self): #Go to the selected directory
		try: #Checking if it's a file or folder
			selection = self.listbox.get(self.listbox.curselection())
			self.TABLE.cwd(self.listbox.get(self.listbox.curselection()))

			#Updating the current path
			self.currentPath += selection
	
			if self.currentPath[-1] != '/':

				self.currentPath += '/'

			self.update(self.TABLE)
		except:

			if self.listbox.get(self.listbox.curselection()).find('.fit') != -1:

				print "Current Path:  ",self.currentPath
				#print "Tabel pwd:     ",self.TABLE.pwd()


				DownloadFits_Single(self.serverObject, self.currentPath+self.listbox.get(self.listbox.curselection()))	
			#Go to Some downloader class.  Make sure to get the path right for fits
			#path = self.TABLE.pwd() + '/' +  self.listbox.get(self.listbox.curselection())

				print "Done"


	def Back(self): #Go up one directory
		try:
			self.TABLE.cwd('..')
			self.currentPath = self.currentPath[0:self.currentPath.rfind('/')]
			self.currentPath = self.currentPath[0:self.currentPath.rfind('/')+1]
			self.update(self.TABLE)
		except:
			print "Already at the top"


def check_file(FILENAME, TABLE): #Shitty way to check for a file
	try:
		TABLE.cwd(FILENAME)
		TABLE.cwd('..')
		return True
	except:
		return False


table_browser = Browser(root,SDSS12) #Starts the Browser

Tk.mainloop()





