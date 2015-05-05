import sys
import numpy as np
import time
import Browser
from Config import PATH, INFO_FIELDS
import copyTesting as DataClasses
from astropy.io import fits
import Transformations

if sys.version_info[0] < 3:
        import Tkinter as Tk
else:
        import tkinter as Tk

class AutoEntry(Tk.Entry):

	def __init__(self, master, default_text, dtype):

		Tk.Entry.__init__(self, master)
		self.dtype = dtype
		self.default_text = default_text
		self.bind('<Button-1>', lambda event: self.stopReplacing())
		self.bind('<FocusOut>', lambda event: self.replaceText())
		self.replaceText()

	def replaceText(self):

		if self.get() == "" and not self.selection_present(): self.insert(0, self.default_text)

	def stopReplacing(self):

		if self.get() == self.default_text:
			self.delete(0,Tk.END)

	def getSelection(self):

		value = self.get()
		if value == self.default_text:
			return None
		elif value == "":
			self.replaceText()
			return None

		try:
			result = self.dtype(value)
			return result

		except ValueError:

			ErrorMsg = Tk.Toplevel()
			label = Tk.Label(ErrorMsg, text = "Invalid Value")
			label.pack()

class DataMangler(Tk.Toplevel):

	def __init__(self, master, TAGS):

		Tk.Toplevel.__init__(self)
		self.title("Data Mangler")
		self.master = master
		self.smoothing = SmoothingManager(self)
		self.transforming = TransformationManager(self)
		self.normalizing = NormalizeManager(self, TAGS)

		self.smoothing.pack(side = Tk.RIGHT, expand = 1, fill = Tk.BOTH)
		self.transforming.pack(side = Tk.LEFT, expand = 1, fill = Tk.BOTH)
		self.normalizing.pack(side = Tk.TOP, expand = 1, fill = Tk.BOTH) 
		self.plotLabels = {Transformations.divide:'Ratio', Transformations.subtract:'Difference', Transformations.reflexive:'Flux'}

	def smoothReturn(self, version, params):

		self.master.MainWindow.smoothing = version
		self.master.MainWindow.smoothingargs = params
		self.master.MainWindow.UpdatePlots()
	
	def transformReturn(self, version):

		self.master.MainWindow.Transform[1] = version
		self.master.MainWindow.PLOT.ax[1].set_ylabel(self.plotLabels[version])
		self.master.MainWindow.UpdatePlots()

	def normalizeReturn(self, version, params):

		self.master.MainWindow.normalize = version
		self.master.MainWindow.normargs = params
		self.master.MainWindow.UpdatePlots()

class NormalizeManager(Tk.LabelFrame):

	def __init__(self, master, TAGS):

		Tk.LabelFrame.__init__(self, master)
		self['text'] = "Normalizations"
		self.TAGS = TAGS
		self.master = master
		self.types = {1:None,2:Transformations.normalize_int,3:Transformations.normalize_wave}
		self.params = {1:{},2:{},3:{}}
		self.selection = Tk.IntVar()
		self.none = Tk.Radiobutton(self, text = "None", variable = self.selection, value = 1, command = self.accept, justify = Tk.LEFT, anchor = Tk.W)
		self.Int = Tk.Radiobutton(self, text = "Area", variable = self.selection, value = 2, command = self.accept, justify = Tk.LEFT, anchor = Tk.W)
		self.Wave = Tk.Radiobutton(self, text = "Wavelength", variable = self.selection, value = 3, command = self.accept, justify = Tk.LEFT, anchor = Tk.W)
		self.wave_length = Tk.Listbox(self)
	
		self.Int.pack(side = Tk.TOP, expand = 0, fill = Tk.X)
		self.Wave.pack(side = Tk.TOP, expand = 0, fill = Tk.X)	
		self.none.pack(side = Tk.TOP, expand = 0, fill = Tk.X)
		self.wave_length.bind('<Button-1>', lambda event: self.after_idle(self.getWave))
		self.none.select()

	def setupWave(self):

		self.wave_length.pack(side = Tk.BOTTOM, expand = 0, fill = Tk.BOTH)
		self.wave_length.delete(0,Tk.END)
		for i in self.TAGS.items():
			if i[1] > 0:
				self.wave_length.insert(Tk.END, i[0])
	
	def getWave(self): #What a mess

		try:
			index = self.wave_length.curselection()[0]
			wave = [i for i in self.TAGS.values() if i > 0][index]*(1+self.master.master.MainWindow.data()['REDSHIFT'])
			print wave
			self.params[3] = {'wavelength':wave}
			self.master.normalizeReturn(self.types[self.selection.get()], self.params[self.selection.get()])	 
		except Tk.TclError:
			return
	
	def accept(self, *args):

		if self.selection.get() == 3:

			return self.setupWave()
		else:
		
			self.wave_length.pack_forget()
		self.master.normalizeReturn(self.types[self.selection.get()], self.params[self.selection.get()])	 

class TransformationManager(Tk.LabelFrame):

	def __init__(self, master):

		Tk.LabelFrame.__init__(self, master)
		self['text'] = "Transformations"
		self.master = master
		self.types = {1:Transformations.divide,2:Transformations.subtract,3:Transformations.reflexive}
		self.selection = Tk.IntVar()
		self.divide = Tk.Radiobutton(self, text = "Divide", variable = self.selection, value = 1, command = self.accept, justify = Tk.LEFT, anchor = Tk.W)
		self.subtract = Tk.Radiobutton(self, text = "Subtract", variable = self.selection, value = 2, command = self.accept, justify = Tk.LEFT, anchor = Tk.W)
		self.none = Tk.Radiobutton(self, text = "None", variable = self.selection, value = 3, command = self.accept, justify = Tk.LEFT, anchor = Tk.W)

		self.divide.pack(side = Tk.TOP, expand = 0, fill = Tk.X)
		self.subtract.pack(side = Tk.TOP, expand = 0, fill = Tk.X)
		self.none.pack(side = Tk.TOP, expand = 0, fill = Tk.X)
		self.none.select()

	def accept(self):

		self.master.transformReturn(self.types[self.selection.get()])

		


class SmoothingManager(Tk.LabelFrame):

	def __init__(self, master):

		Tk.LabelFrame.__init__(self, master)
		self.master = master
		self['text'] = "Smoothing"
		self.types = {1:Transformations.smooth_,2:Transformations.smoothSavgol}
		self.param = {1:{'N':10},2:{'N':11,'order':2}}		
		self.type_selection = Tk.LabelFrame(self, text = 'Method')
		###################################
		self.selection = Tk.IntVar()
		self.Savgol = Tk.Radiobutton(self.type_selection, text = "Savitzky-Golay", variable = self.selection, value = 2, command = self.savgolSetup)
		self.boxcar = Tk.Radiobutton(self.type_selection, text = "Box Car", variable = self.selection, value = 1, command = self.boxcarSetup)	
		###################################
		self.params = Tk.Frame(self)
		###################################
		self.length = AutoEntry(self.params, 'Length (odd int)', self.oddInt) 	
		self.order = AutoEntry(self.params, 'Order (int)', int)
		###################################
		self.acceptButton = Tk.Button(self, text = 'Accept', command = self.accept)
		self.boxcar.pack(side = Tk.LEFT, expand = 0, fill = Tk.X)
		self.Savgol.pack(side = Tk.RIGHT, expand = 0, fill = Tk.X)
		self.length.pack(side = Tk.LEFT, expand = 1, fill = Tk.X)
		self.acceptButton.pack(side = Tk.BOTTOM, expand = 0, fill = Tk.X)
		self.type_selection.pack(side = Tk.TOP, expand = 1, fill = Tk.X)
		self.params.pack(side = Tk.TOP, expand = 1, fill = Tk.X)
		self.order.pack(side = Tk.RIGHT, expand = 1, fill = Tk.X)
		self.order['state'] = Tk.DISABLED
		self.boxcar.select()

	def oddInt(self, x):

		x = int(x)
		if not x % 2:
			x += 1
		return x 

	def accept(self):

		var = self.selection.get()
		N = self.length.getSelection()
		if N:
			self.param[var]['N'] = self.length.getSelection()
			if var == 2:
				order = self.order.getSelection()
				if order:
					self.param[var]['order'] = self.order.getSelection()
					self.master.smoothReturn(self.types[var], self.param[var])
			else: self.master.smoothReturn(self.types[var], self.param[var])
	
	def savgolSetup(self):

		self.order['state'] = Tk.NORMAL
		self.order.replaceText()
		self.length.replaceText()

	def boxcarSetup(self):	

		self.order['state'] = Tk.DISABLED
		self.length.replaceText()

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
		msg = Tk.Label(self, text = "".join(("Loading ",selection)))
		msg.pack(expand = 1, fill = Tk.BOTH)
		self.server_listbox.pack_forget()
		self.selectButton.pack_forget()
		self.update()
		browser = Browser.Browser(self, self.server_list[selection])
		msg.pack_forget()
		browser.pack(expand = 1, fill = Tk.BOTH)


class OverrideData(Tk.LabelFrame):

	def __init__(self, master, Data, field = 'REDSHIFT'):

		Tk.LabelFrame.__init__(self, master)
		self.master = master
		self.group = Data()
		self.field = field
		old_value = self.group[field]
		self.dtype = type(old_value)
		if self.dtype is int:self.dtype = float
		self.msgField = Tk.Label(self, text = " ".join(('Adjusting', field)))
		self.msgValue = Tk.Label(self, text = " ".join(('Old Value:', str(old_value))))
		self.entry = AutoEntry(self, str(self.dtype), self.dtype)
		self.warn = Tk.Label(self, text = "Warning: Overrides will not be saved.")
		self.go = Tk.Button(self, text = 'GO', command = self.adjustData) 
		self.msgField.pack(side = Tk.TOP, expand = 0, fill = Tk.BOTH)
		self.msgValue.pack(side = Tk.TOP, expand = 0, fill = Tk.BOTH)
		self.entry.pack(side = Tk.TOP, expand = 0, fill = Tk.BOTH)
		self.warn.pack(side = Tk.TOP, expand = 0, fill = Tk.BOTH)
		self.go.pack(side = Tk.BOTTOM, expand = 0, fill = Tk.X)

	def adjustData(self):

		result = self.entry.getSelection()
		if result:
			self.group.Data[self.field] = result
			for i in self.group.sortedReturn():
				i.Data[self.field] = result
			self.destroy()
			self.master.withdraw()	



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

