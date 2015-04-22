from PlottingClasses import *
from matplotlib.widgets import MultiCursor
from Config import PATH
import copyTesting as DataClasses
import numpy as np
import time
import os
import sys
import Science
import DataTables
from DataTables import Transformations
import tkFont

try:
	import thread
except ImportError:
	import dummy_thread

if sys.version_info[0] < 3:
        import Tkinter as Tk
else:
        import tkinter as Tk


class PlottingInterface(Tk.Frame): #Example of a window application inside a frame

	def __init__(self, master, Data):

		self.data = Data
		Tk.Frame.__init__(self, master)
		if len(sys.argv) > 1:

			try:

				print int(sys.argv[1])	
				self.data.DataPosition = list(self.data.currentData).index(int(sys.argv[1])) - 1
		
			except ValueError:

				with open(sys.argv[1], 'rb') as groupList:

					self.data.currentData = np.array(map(int, groupList.read().split()))
		#Frames

		self.Navigation = Tk.Frame(self)

		##################
		self.Views = Tk.Toplevel()
		self.Views.title("Tag Views")
		self.Views.protocol("WM_DELETE_WINDOW", self.Views.withdraw)
		self.Views.withdraw()
		##################


		#self.Manipulation = Tk.Frame(self)
		self.Properties = Tk.Frame(self)
		self.PLOT = PlottingWindow(self)
		self.PLOT.AddSubplot()
		self.PLOT.AddSubplot(self.PLOT.ax[0], combineX = True)

		self.BasicInformation = DataTables.BasicDataDisplay(self.Properties, 4)
		self.BasicInformation.setTitles(['RA:','DEC:','Redshift:','Group ID:'], 10)

		#Buttons

		######## Mark Buttons

		SciSize = len(Science.TAGS)
		self.ViewWindowState = False

		self.ToggleSlineMark = DataTables.BasicCheckDisplay(self.Properties, SciSize)

		self.ToggleSlineView = DataTables.BasicCheckDisplay(self.Views, SciSize, Anch = Tk.CENTER)

		Skeys = Science.TAGS.keys()

		width = max((len(i) for i in Science.TAGS.keys()))
		self.ToggleSlineMark.setTitles(Skeys, width)
		self.ToggleSlineView.setTitles([i[0:-1] for i in Skeys], width)

		MarkCommands = []
		ViewCommands = []
		for i,j,k,l,m in zip(Skeys, self.ToggleSlineView.buttons, self.ToggleSlineView.buttonvars, self.ToggleSlineMark.buttons, self.ToggleSlineMark.buttonvars):
			MarkCommands.append(lambda x=i, y=l, z=m: self.toggleMark(x,y,z))
			ViewCommands.append(lambda x=i, y=j, z=k: self.toggleSline(x,y,z))
			

		self.ToggleSlineMark.setCommands(MarkCommands)

		self.ToggleSlineView.setCommands(ViewCommands)

		########

		self.NextButton = Tk.Button(self.Navigation, text = 'Next', command = self.NEXT)
		self.PreviousButton = Tk.Button(self.Navigation, text = 'Previous', command = self.PREV)

		#self.Toggle2D = Tk.Button(self.Manipulation, text = 'View Subtraction', command = self.toggle2d)

		#self.SaveSession = Tk.Button(self.Manipulation, text = 'Save', command = self.data.saveInterestingObjects)

		#Packing

		#self.Manipulation.pack(side = Tk.TOP, expand = 0, fill = Tk.X)
		self.Navigation.pack(side = Tk.BOTTOM, expand = 0, fill = Tk.X)
		self.Properties.pack(side = Tk.LEFT, expand = 0, fill = Tk.BOTH)
		#self.Views.pack(side = Tk.RIGHT, expand = 0, fill = Tk.BOTH)	
		self.PLOT.pack(expand = 1, fill = Tk.BOTH)
		self.BasicInformation.pack(side = Tk.TOP, expand = 0, fill = Tk.BOTH)
		self.ToggleSlineMark.pack(side = Tk.TOP, expand = 0, fill = Tk.BOTH)
		self.NextButton.pack(side = Tk.RIGHT, expand = 1, fill = Tk.X)
		self.PreviousButton.pack(side = Tk.RIGHT, fill = Tk.X, expand = 1)
		self.ToggleSlineView.pack(side = Tk.TOP, expand = 0, fill = Tk.BOTH)
		#self.Toggle2D.pack(side = Tk.RIGHT, expand = 1, fill = Tk.X)
		#self.SaveSession.pack(side = Tk.RIGHT, expand = 1, fill = Tk.X)

		#Plot Properties

		self.PLOT.ax[0].set_ylabel(r'$\mathtt{Flux}$')
		self.PLOT.ax[1].set_ylabel(r'$\mathtt{Flux}$')
		self.PLOT.ax[1].set_xlabel(r'$\mathtt{\lambda \/ (\AA)}$')
		self.PLOT.ax[0].set_xlabel(r'$\mathtt{\lambda \/ (\AA)}$')

		#Default Transformations

		self.Transform = []
		self.smoothing = Transformations.smooth_
		self.smoothingargs = {'N':10}
		self.normalize = None
		self.normargs = {}	
		self.Transform.append(Transformations.reflexive)
		self.Transform.append(Transformations.reflexive)

		self.UpdatePlots()		

		self.ToggleSlineMark.repack()
		self.ToggleSlineView.repack(self.ToggleSlineMark.data)
		#Cursor

                self.cursor = MultiCursor(self.PLOT.fig.canvas,(self.PLOT.ax[0], self.PLOT.ax[1]), color='#999999', linewidth=1.0 , useblit = True)
	
		self.backgroundTasks(0)

	def showViews(self):

		self.Views.deiconify()

	def NEXT(self):

		self.data.next()
		self.UpdatePlots()		

	def PREV(self):

		self.data.prev()
		self.UpdatePlots()		

	def plotCurrent(self, ax_index, Transform = None, **kwargs):

		T0 = time.clock()

		if Transform == None: 

			Transform = self.Transform[ax_index]

		Transform = Transformations.fsmooth(Transform, method = self.smoothing, **self.smoothingargs)

		if self.normalize is not None:

			Transform = Transformations.normalize(Transform, self.normalize, **self.normargs)

		self.PLOT.ClearPlot(ax_index)

		DR = Transform([i.getSpectrum() for i in self.data().sortedReturn()], **kwargs)

		for i in DR: self.PLOT.Plot(i[1], i[0], ax_index)

		print "Plot Lines Time: ", time.clock() - T0
		T0 = time.clock()

		self.PLOT.ax[ax_index].relim()
		self.PLOT.ax[ax_index].autoscale(enable = True)
	
		print "Update Limits Time: ", time.clock() - T0

	def toggleSline(self, tag, button, var, merge = 'u'):

		tag = str(tag)
		if tag not in self.data.tagList.keys():

			self.data.addTag(tag)
			button.deselect()
			return

		elif var.get():

			if len(self.data[tag]) == 0:

				button.deselect()
				return

			else:

				self.data.appendTagState((tag,merge))

		else:

			self.data.removeTagState((tag,merge))

		self.data.update()
		self.UpdatePlots()

	def backgroundTasks(self, n = 0):

		if n < len(self.data.currentData) and n < self.data.DataPosition + 32:
			for i in self.data[self.data.FullData[n]].getMembers(): 

				thread.start_new_thread(i.loadSpectrum,())
			self.after(3000,self.backgroundTasks, n+1)
		else:

			print "Idle"
			self.after(60000, self.backgroundTasks, self.data.DataPosition+1)
			thread.start_new_thread(self.saveData,('Autosave.csv',))


	def toggleMark(self, tag, button, var):

		if var.get():

			self.data.appendTag(tag)

		else:

			self.data.removeTag(tag) 	

		self.updateFields()	

	#def toggle2d(self):

	#	if self.Toggle2D["text"] == 'View Subtraction':

	#		self.Toggle2D["text"] = 'View Division'
	#		self.Transform[1] = Transformations.subtract
	#		self.UpdatePlots()

	#	else:
	
	#		self.Toggle2D["text"] = 'View Subtraction'
	#		self.Transform[1] = Transformations.divide
	#		self.UpdatePlots()

	def UpdatePlots(self):

		self.plotCurrent(0)
		if len(self.data()) < 2:
			T = Transformations.reflexive
			#self.Toggle2D["state"] = Tk.DISABLED
		else:
			T = self.Transform[1]
			#self.Toggle2D["state"] = Tk.NORMAL
		self.plotCurrent(1, T)
		self.PLOT.update()
		self.updateFields()

	def updateFields(self):

		T0 = time.time()

		self.BasicInformation.setData([self.data().Data[i] for i in ['RA','DEC','REDSHIFT','GroupID']], 12)

		width = max((len(i) for i in Science.TAGS.keys()))
		self.ToggleSlineMark.setData(Science.RedShiftSlines(float(self.data().Data['REDSHIFT'])), width)

		tags = self.data.getCurrentTagNames()

		Marked = [(i in tags) for i in Science.TAGS.keys()]

		self.ToggleSlineMark.setStates(Marked)

		print "Update Fields Time: ", time.time() - T0

	def toggleButtonRelief(self, Button, Bool):

		if Bool:

			Button['relief'] = Tk.SUNKEN

		else:

			Button['relief'] = Tk.RAISED

	def saveData(self, Filename = "InterestingMatches.csv"):

		T0 = time.time()
		fields = ['MJD','PLATEID','FIBERID','RA','DEC','REDSHIFT','FILENAME','Interesting']

		MarkedObjects = np.array([])

		for i in self.data.tagList.keys():

			if i != "None":

                                MarkedObjects = np.union1d(MarkedObjects,np.array([j() for j in self.data[i].getMembers()]))
	
		InterestingFile = open(Filename,'wb')
		InterestingFile.write('#MJD, PLATEID, FIBERID, RA, DEC, Z, FILENAME, ARGS, TAGS\n')


		for i in MarkedObjects:	

			for j in self.data[i].getMembers():	

				InterestingFile.write(", ".join([str(j[k]) for k in fields]))

				InterestingFile.write(", ")

				InterestingFile.write(" ".join([k.name for k in self.data[i].getTags()]))

				InterestingFile.write('\n')

		InterestingFile.close()

		with open('resource/tags.conf','wb') as tagFile: 
			for i in Science.TAGS.items(): tagFile.write("".join((" ".join((str(i[0]),str(i[1]))),'\n')))

		print "Save Time: ", time.time() - T0

class App(Tk.Tk):

	def __init__(self):

		Tk.Tk.__init__(self)

		msgBox = Tk.Toplevel(self)
		msgBox.overrideredirect(True)
		msgBox.wm_geometry("200x50-583+334")
		msgFrame = Tk.LabelFrame(msgBox, padx = 5, pady = 5)
		msgname = Tk.Label(msgFrame, text = "Spectrum Analysis Tool")
		msg = Tk.Label(msgFrame, text = "Loading Spectra...")
		msgname.pack(side = Tk.TOP, expand = 1, fill = Tk.BOTH)
		msg.pack(side = Tk.BOTTOM, expand = 1, fill = Tk.BOTH)
		msgFrame.pack(expand = 1, fill = Tk.BOTH)
		self.withdraw()
		msgBox.update()

		self.title("Plotting Interface")
		self.geometry('1200x600-100+100')
		self.protocol("WM_DELETE_WINDOW",self.Quit)
		##########################################

		self.Info = None
		self.Mangler = None
		self.menubar = Tk.Menu(self)
		self.views = Tk.Menu(self.menubar)
		self.new = Tk.Menu(self.menubar)
		self.tools = Tk.Menu(self.menubar)
		SpectraData = DataClasses.Data()
		msg['text'] = "Loading Interface..."
		msgBox.update()
		self.MainWindow = PlottingInterface(self, SpectraData)
		msg['text'] = "Ready!"
		msgBox.update()
		self.MainWindow.pack(expand = 1, fill = Tk.BOTH)

		self.new.add_command(label = "Tag", command = self.newTag)
		self.views.add_command(label="Tags", command=self.tagSelection)
		self.views.add_command(label="Info", command=self.viewObjectInfo)
		self.tools.add_command(label="Download", command = self.browseServer)
		self.tools.add_command(label="Override Redshift", command = self.changeZ)
		self.tools.add_command(label="Transform Data", command = self.mangle)
	
		self.tools.add_command(label="Run Matching", command = self.runMatching)
		self.tools.add_command(label="Reload Data", command = self.reloadData)
		self.menubar.add_cascade(label = "View", menu = self.views)
		self.menubar.add_cascade(label = "New", menu = self.new)
		self.menubar.add_cascade(label = "Tools", menu = self.tools)

		self.config(menu = self.menubar)
		msgBox.withdraw()
		self.deiconify()

	def reloadData(self):

		msgBox = Tk.Toplevel()
		msg = Tk.Label(msgBox, text = "Reloading Data...\n\nThis Will Take a Few Seconds.")
		msg.pack()
		msgBox.update()
		self.MainWindow.data = DataClasses.Data()
		self.MainWindow.data.DataPosition = 0
		self.MainWindow.UpdatePlots()
		msg['text'] = "Done Loading"
		msgBox.update()

	def runMatching(self):

		msgBox = Tk.Toplevel()
		msg = Tk.Label(msgBox, text = "Matching Data in Background\n\nRestart or Reload Required\n\nFor Changes To Take Effect")
		msg.pack()
		thread.start_new_thread(DataClasses.groupData,())
		msgBox.update()

	def mangle(self):

		if self.Mangler == None:
			self.Mangler = DataTables.DataMangler(self, Science.TAGS)
			self.Mangler.protocol("WM_DELETE_WINDOW", self.Mangler.withdraw)
		else:
			self.Mangler.deiconify()
		self.Mangler.update()

	def changeZ(self):

		window = Tk.Toplevel(self)
		window.title("Change Redshift")
		frame = DataTables.OverrideData(window, self.MainWindow.data)
		frame.pack()
		try:
			self.wait_window(frame.entry)
			self.MainWindow.data.update()
			self.MainWindow.updateFields()
		except Tk.TclError:
			print "Weird Bug Encountered"		


	def browseServer(self):

		window = Tk.Toplevel(self)
		window.title("Spectrum Search")
		browser = DataTables.ServerBrowser(window)
		browser.pack(expand = 1, fill = Tk.BOTH)

	def viewObjectInfo(self):

		if self.Info == None:
			self.Info = DataTables.AdvancedDataDisplay("Information", self.MainWindow.data)
			self.Info.protocol("WM_DELETE_WINDOW", self.Info.withdraw)
		self.Info.update()

	def newTag(self):

		Dbox = Tk.Toplevel()
		DboxFrame = Tk.Frame(Dbox)
		Name = Tk.Entry(DboxFrame)
		Value = Tk.Entry(DboxFrame)

		def ReplaceText(EntryAndText):

			if EntryAndText[0].get() == "" and not EntryAndText[0].selection_present(): EntryAndText[0].insert(0, EntryAndText[1])
			#DboxFrame.after(100,ReplaceText,EntryAndText) 	

		def StopReplacing(EntryAndText):
			global ReplaceText
			if EntryAndText[0] == None: return
			if EntryAndText[0].get() == EntryAndText[1]:
				EntryAndText[0].delete(0,Tk.END)
			if EntryAndText[0] == Name and Value.get() == "":
				Value.insert(0, "Value (Float)")
			elif EntryAndText[0] == Value and Name.get() == "":
				Name.insert(0, "Name (String)")
			elif Name.get() and EntryAndText[0] != Name == "":
				Name.insert(0, "Name (String)")
			elif Value.get() == "" and EntryAndText[0] != Value:
				Value.insert(0, "Value (Float)")

		Name.bind('<Button-1>',lambda event: StopReplacing([Name, "Name (String)"])) 
		Value.bind('<Button-1>',lambda event: StopReplacing([Value, "Value (Float)"])) 

		ReplaceText([Name, "Name (String)"])
		ReplaceText([Value, "Value (Float)"])

		def getSelection():

			name = Name.get()
			value = Value.get()
			try:
				if value == "Value (Float)": value = 0
				if name.find(" ")+1: raise ValueError
				value = float(value)
				name = "".join((name,":"))
				Science.TAGS.setdefault(name, value)
				self.MainWindow.ToggleSlineMark.newCheck()
				self.MainWindow.ToggleSlineView.newCheck()
				width = max((len(i) for i in Science.TAGS.keys()))
				self.MainWindow.ToggleSlineMark.setTitles(Science.TAGS.keys(), width)
				self.MainWindow.ToggleSlineView.setTitles([i[0:-1] for i in Science.TAGS.keys()], width)
				self.MainWindow.ToggleSlineMark.setCommands([lambda x=i,y=j,z=k: self.MainWindow.toggleMark(x,y,z) for i,j,k in zip(Science.TAGS.keys(), self.MainWindow.ToggleSlineMark.buttons, self.MainWindow.ToggleSlineMark.buttonvars)])	
				self.MainWindow.ToggleSlineView.setCommands([lambda x=i,y=j,z=k: self.MainWindow.toggleSline(x,y,z) for i,j,k in zip(Science.TAGS.keys(), self.MainWindow.ToggleSlineView.buttons, self.MainWindow.ToggleSlineView.buttonvars)])	
				self.MainWindow.data.appendTag(name)
				Dbox.withdraw()
				self.MainWindow.updateFields()
				self.MainWindow.ToggleSlineMark.repack()
				self.MainWindow.ToggleSlineView.repack(self.MainWindow.ToggleSlineMark.data)
	
			except ValueError:
				ErrorMsg = Tk.Toplevel()
				label = Tk.Label(ErrorMsg, text = "Invalid Value")
				label.pack()

		GO = Tk.Button(DboxFrame,text = 'Create Tag', command = getSelection)
		GO.pack(side = Tk.BOTTOM, expand = 0, fill = Tk.BOTH)
		Name.pack(side = Tk.LEFT, expand = 0, fill = Tk.BOTH)
		Value.pack(side = Tk.RIGHT, expand = 0, fill = Tk.BOTH)
		DboxFrame.pack()	
		GO.bind('<Button-1>',lambda event: StopReplacing([None,None])) 
		
	def tagSelection(self):

		self.MainWindow.showViews()

	def Quit(self):

		self.MainWindow.saveData()
		self.update_idletasks()
		self.after_idle(self.quit)
		self.after_idle(self.destroy)

app = App()
app.mainloop()

