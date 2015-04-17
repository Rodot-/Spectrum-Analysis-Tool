import sys
import numpy as np
import time
import Browser
from Config import PATH, INFO_FIELDS
import copyTesting as DataClasses
from astropy.io import fits

if sys.version_info[0] < 3:
        import Tkinter as Tk
else:
        import tkinter as Tk

class ServerBrowser(Tk.Frame):

	def __init__(self, master):

		self.master = master
		Tk.Frame.__init__(self, master)
		self.server_list = Browser.LoadServers()
		self.server_listbox = Tk.Listbox(self)
		self.selectButton = Tk.Button(self, text = 'select', command = self.select)
		self.server_listbox.pack(expand = 1, fill = Tk.BOTH)
		self.selectButton.pack(side = Tk.BOTTOM, expand = 0, fill = Tk.X)
		self.populate()

	def populate(self):

		for i in self.server_list.keys():

			self.server_listbox.insert(Tk.END, i)

	def select(self):

		selection = self.server_listbox.get(self.server_listbox.curselection())
		browser = Browser.Browser(self.master, self.server_list[selection])
		browser.pack()	
		self.server_listbox.pack_forget()

class BasicDataDisplay(Tk.LabelFrame): #Class That dispalys n number of labels

	def __init__(self, master, n, w = 0):
	
		Tk.LabelFrame.__init__(self, master)
		self.titles = np.empty(n, dtype = '<S16')
		self.labels = []
		[self.labels.append(Tk.Label(self, width = w, justify = Tk.LEFT, anchor = Tk.W, font = ("TkDefaultFont", 10, 'bold'))) for i in xrange(n)]
		[i.pack(side = Tk.TOP, expand = 0, fill = Tk.BOTH) for i in self.labels]
	def setTitles(self, TitleArray, width=20): #Sets the titles of the labels 

		size = len(TitleArray)

		for t in xrange(size):

			self.titles[t] = self.labels[t]["text"] = FormattedTitle = ('{:<%s}' % width).format(TitleArray[t])

	def setData(self, DataArray, width=20): #Fills the Label; with information

		size = len(DataArray)

		for t in xrange(size):

			self.labels[t]["text"] = "".join((self.titles[t],('{:<%s}' % width).format(str(DataArray[t]))))
		
class AdvancedDataDisplay(Tk.Toplevel):

	Fields = INFO_FIELDS
	#Fields = ['MJD','PLATE','FIBERID','CLASS','SUBCLASS','Z','Z_ERR','SN_MEDIAN_ALL']

	def __init__(self, title, Data):
	
		Tk.Toplevel.__init__(self)
		self.title(title)
		self.basicDataDisplays = []
		self.frame = Tk.Frame(self)
		self.subframe = [Tk.Frame(self.frame) for i in xrange(10)]
		self.data = Data
		self.lastGroupID = 0
		self.updater = Tk.Button(self,text = "Update", command = lambda x=0: self.update()) 
		self.frame.pack(side = Tk.TOP, expand = 1, fill = Tk.BOTH)
		self.updater.pack(side = Tk.BOTTOM, expand = 0, fill = Tk.X)
		#for i in self.subframe: i.pack(side = Tk.LEFT, expand = 0, fill = Tk.BOTH)
	
	def update(self):
		
		Group = self.data()
		if Group.ID == self.lastGroupID:
			self.deiconify()
			return
		self.lastGroupID = Group.ID
		Files = ["/".join((PATH, i['FILENAME'])) for i in Group.sortedReturn()]
		lenFields = len(self.Fields)
		lenFiles = len(Files)
		lenBDD = len(self.basicDataDisplays)
		for i in xrange(lenBDD):
			if i >= lenFiles:
				self.basicDataDisplays[i].pack_forget()
				self.subframe[(i+4)/4].pack_forget()
		for i in xrange(lenFiles):
			if i >= lenBDD:
				self.basicDataDisplays.append(BasicDataDisplay(self.subframe[i/4], lenFields, w = 32))
				self.basicDataDisplays[i].setTitles(self.Fields)
			self.basicDataDisplays[i].pack(side = Tk.TOP, expand = 1, fill = Tk.BOTH)
			self.subframe[i/4].pack(side = Tk.LEFT, expand = 1, fill = Tk.BOTH)
			self.basicDataDisplays[i].setData(self.getFields(Files[i]))	
		self.resizable(True, True)
		self.deiconify()

	
	def getFields(self, Filename):

		currentFile = fits.open(Filename)
		data = [str(currentFile[2].data[i][0]) for i in self.Fields]
		currentFile.close()
		return data 


class BasicCheckDisplay(Tk.LabelFrame): #Class That dispalys n number of checkbuttons

	def __init__(self, master, n, w = 0, asButton = False, Anch = Tk.W):
	
		Tk.LabelFrame.__init__(self, master)
		self.titles = np.empty(n, dtype = '<S16')
		self.buttons = []
		self.w = w
		self.data = np.empty(n, dtype = '<f8')
		self.asButton = asButton
		self.Anch = Anch
		self.endOfTitle = None
		if asButton: self.endOfTitle = -1
		self.buttonvars = [Tk.IntVar() for k in xrange(n)]
		[self.buttons.append(Tk.Checkbutton(self, variable = self.buttonvars[i], width = w, justify = Tk.LEFT, anchor = Anch, font = ("TkDefaultFont", 10, 'bold'), indicatoron = not asButton)) for i in xrange(n)]
		[i.pack(side = Tk.TOP, expand = 0, fill = Tk.BOTH) for i in self.buttons]

	def repack(self, data = None):

		if data is None:

			data = self.data

		for i in self.buttons: i.pack_forget()

		pos = np.lexsort([self.titles, data])

		for i in reversed(pos): self.buttons[i].pack(side = Tk.TOP, expand = 0, fill = Tk.BOTH)

	def setTitles(self, TitleArray, width=20): #Sets the titles of the labels 
		self.wid = width
		size = len(TitleArray)

		for t in xrange(size):

			self.titles[t] = self.buttons[t]["text"] = FormattedTitle = ('{:<%s}' % width).format("".join((" ",TitleArray[t][:self.endOfTitle])))

	def setData(self, DataArray, width=20): #Fills the Label; with information

		self.width = width
		size = len(DataArray)

		for t in xrange(size):

			if DataArray[t] == 0:
				D = ""
			else:
				D = str(DataArray[t])
			self.data[t] = DataArray[t]
			self.buttons[t]["text"] = "".join((self.titles[t],('{:>%s}' % width).format(D)))

	def setCommands(self, commandArray):
	
		size = len(commandArray)

		for t in xrange(size):

			self.buttons[t]["command"] = commandArray[t]

	def setStates(self, maskArray):

		for i in xrange(len(maskArray)):

			if maskArray[i]:
				self.buttons[i].select()
			else:
				self.buttons[i].deselect()
				
	def newCheck(self):

		self.buttonvars.append(Tk.IntVar())		
		self.buttons.append(Tk.Checkbutton(self, variable = self.buttonvars[-1], width = self.w, justify = Tk.LEFT, anchor = self.Anch, font = ("TkDefaultFont", 10, 'bold'), indicatoron = not self.asButton))
		self.buttons[-1].pack(side = Tk.TOP, expand = 0, fill = Tk.BOTH)
		self.titles = list(self.titles)
		self.data = list(self.data)
		self.data.append(0)
		self.titles.append("")
		self.titles = np.array(self.titles)
		self.data = np.array(self.data)

class FullDataTable(Tk.Frame):

	def __init__(self, master, Data):

		Tk.Frame.__init__(self, master)
		self.window = Tk.PanedWindow(self)
		self.window.pack(expand = 1, fill = Tk.BOTH)
		self.lists = Tk.Listbox(self.window, width = 92)
		self.ColumnLengths = {'RA':14,'DEC':14,'REDSHIFT':14}

		print "Populating List"

		self.ListEntries = (self.BuildListEntries(Data[i]) for i in Data.currentData)

		print "Showing Lists"
		
		self.populateList()
		self.window.add(self.lists)		

	def BuildListEntries(self, Row):


		return "|".join(((('{:<%s}' % self.ColumnLengths[i]).format(str(Row[i]))) for i in self.ColumnLengths.keys()))

	def populateList(self):

		for i in self.ListEntries:

			self.lists.insert(Tk.END, i)


#class Window(Tk.Frame): #Example of a window application inside a frame

#        def __init__(self, master):

#                Tk.Frame.__init__(self, master)
                #########################################

#		self.DataTable = FullDataTable(self, DataClasses.Data())
#		self.DataTable.pack(expand = 1, fill = Tk.BOTH, side = Tk.RIGHT)

#		self.Props = BasicDataDisplay(self, 9)
#		self.Props.setTitles(['Spam:','Eggs:','Foo:','Bar:'], 7)
#		self.Props.setData([20.453235,1.345274,0.55212,5524], 10)
#		self.Props.pack(expand = 0, fill = Tk.BOTH, side = Tk.LEFT)


'''
class App(Tk.Tk):
        def __init__(self):

                Tk.Tk.__init__(self)
                self.title("Label Interface")
                self.protocol("WM_DELETE_WINDOW",self.quit)
                ##########################################

                self.MainWindow = Window(self)
                self.MainWindow.pack(expand = 1, fill = Tk.BOTH, side = Tk.BOTTOM)
		button = Tk.Button(text = 'TEXT', command = self.COM)
		button.pack(side = Tk.LEFT)

		print "All Done"
		self.c = 0

	def COM(self):
	
		Titles = ['RA:', 'DEC:', 'Redshift:', 'Group ID:']
		self.MainWindow.Props.setTitles(Titles, 10)
		self.c += 1

app = App()
app.mainloop()
'''

