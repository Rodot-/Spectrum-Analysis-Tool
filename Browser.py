import ftplib
import sys
import HTTPServerManager as HTTP


try: 
	import Tkinter as Tk
except:
	try:
		import tkinter as Tk
	except:
		print "Can't Import Tkinter, Try Updating Python, or Installing Tkinter Manually."
		print "Cannot Continue, Goodbye."
		exit()


BOSS = ftplib.FTP('sdssrm.obs.carnegiescience.edu','sdssrm','rev-map') #FTP Server

SDSS = HTTP.URL('http://das.sdss.org/spectro')

root = Tk.Tk()
root.wm_title('File Browser')

class Browser: #The Class of interest.  Allows user to browse all files on any ftp server

	def __init__(self,master,TABLE): #Init, obviously
		self.TABLE = TABLE #Get's the FTP object we want to check out
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
		self.b.pack(side = Tk.LEFT, expand = True,fill = 'x')
		self.back.pack(side = Tk.RIGHT, expand = True,fill = 'x')
		
		self.update(TABLE) #Update the listbox
	
	def update(self, TABLE): #Updates the listbox, makes files have blue text
		self.listbox.delete(0,Tk.END) #delete previous listbox entries
		for item in TABLE.nlst():
			self.listbox.insert(Tk.END, item)
			if item.find('.') != -1: #The color thing
				self.listbox.itemconfig(Tk.END, fg = 'blue')

	def NewDir(self): #Go to the selected directory
		try: #Checking if it's a file or folder
			self.TABLE.cwd(self.listbox.get(self.listbox.curselection()))
			self.update(self.TABLE)
		except:

			#DownloadFits_Single(self.listbox.get(self.listbox.curselection()))	
			#Go to Some downloader class.  Make sure to get the path right for fits
			#path = self.TABLE.pwd() + '/' +  self.listbox.get(self.listbox.curselection())

			print "Downloadable File",self.listbox.get(self.listbox.curselection())	

	def Back(self): #Go up one directory
		try:
			self.TABLE.cwd('..')
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


table_browser = Browser(root,SDSS) #Starts the Browser

Tk.mainloop()




