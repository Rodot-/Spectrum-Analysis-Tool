import ftplib
import sys
import HTTPServerManager as HTTP
from FileManager import DownloadFits_Single, LoadServers

try: 
	import Tkinter as Tk
except:
	try:
		import tkinter as Tk
	except:
		print "Can't Import Tkinter, Try Updating Python, or Installing Tkinter Manually."
		print "Cannot Continue, Goodbye."
		exit()

class Browser(Tk.Frame): #The Class of interest.  Allows user to browse all files on any ftp server

	def __init__(self, master, serverObject): #Init, obviously

		Tk.Frame.__init__(self,master,  height = 100, width = 50)

		self.serverObject = serverObject

		self.currentPath = '' #Records the current path
		
		#Determining what kind of server it is and opening it

		if serverObject[0] == 'FTP':

			self.TABLE = ftplib.FTP(serverObject[1], serverObject[2], serverObject[3])

		elif serverObject[0] == 'URL':

			self.TABLE = HTTP.URL(serverObject[1])

		self.scroller = Tk.Scrollbar(self, orient = Tk.VERTICAL) #Scrollbar
		self.listbox = Tk.Listbox(self, yscrollcommand = self.scroller.set, height = 13, width = 42) #List box we use to display files and folders
		self.scroller.config(command = self.listbox.yview) #Configure Scrollbar	
		self.back = Tk.Button(self, text = 'Back', command = self.Back) #This button takes you up one directory
		self.b = Tk.Button(self, text = 'Select', command = self.NewDir) # this button allows you to select a file or folder to work with
		#Runs the matching program
		#Packing Up
		self.scroller.pack(side=Tk.RIGHT, fill = 'y')
		self.listbox.pack(fill = Tk.BOTH, expand = True)

		self.b.pack(side = Tk.RIGHT, expand = True,fill = 'x')
		self.back.pack(side = Tk.LEFT, expand = True,fill = 'x')
		self.update(self.TABLE) #Update the listbox
	
	def update(self, TABLE): #Updates the listbox, makes files have blue text
		self.listbox.delete(0,Tk.END) #delete previous listbox entries
		for item in TABLE.nlst():
			self.listbox.insert(Tk.END, item)
			if item.find('.') + 1: #The color thing
				if item.find('.fit') + 1:
					if item.find('spec-') + 1:
						self.listbox.itemconfig(Tk.END, fg = 'green')
					else:
						self.listbox.itemconfig(Tk.END, fg = 'red')
				else:
					self.listbox.itemconfig(Tk.END, fg = 'blue')
	def NewDir(self): #Go to the selected directory
		try: #Checking if it's a file or folder
			selection = self.listbox.get(self.listbox.curselection())
			self.TABLE.cwd(self.listbox.get(self.listbox.curselection()))

			#Updating the current path
			self.currentPath += selection
	
			if self.currentPath[-1] != '/':

				self.currentPath = "".join((self.currentPath,'/'))
			self.update(self.TABLE)

		except (ftplib.error_perm, IOError):

			if self.listbox.get(self.listbox.curselection()).find('.fit') != -1:

				print "Current Path:  ",self.currentPath

				DownloadFits_Single(self.serverObject, self.currentPath+self.listbox.get(self.listbox.curselection()))	

				print "Done"


	def Back(self): #Go up one directory
		try:
			self.TABLE.cwd('..')
			self.currentPath = self.currentPath[0:self.currentPath.rfind('/')]
			self.currentPath = self.currentPath[0:self.currentPath.rfind('/')+1]
			self.update(self.TABLE)
		except:
			print "Already at the top"
'''
server_list = LoadServers()

SDSS = server_list['DR7']
SDSS12 = server_list['DR12_SDSS']

root = Tk.Tk()
root.wm_title('File Browser')

table_browser = Browser(root,server_list['Rev-Map']) #Starts the Browser
table_browser.pack()

Tk.mainloop()
'''




