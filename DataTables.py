import sys
import numpy as np
import time
import DataClasses
import eventlet

pool = eventlet.GreenPool(size = 10)

if sys.version_info[0] < 3:
        import Tkinter as Tk
else:
        import tkinter as Tk

'''PATH = 'downloads/SDSS/'

Fdata = DataClasses.Data()
data = Fdata.MainDataArray
print "Data Imported"
'''


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

		

		

class FullDataTable(Tk.Frame):

	def __init__(self, master, Data):

		Tk.Frame.__init__(self, master)
		self.Headers = Data[0].dtype.names
		self.window = Tk.PanedWindow(self)
		self.window.pack(expand = 1, fill = Tk.BOTH)
		self.lists = Tk.Listbox(self.window, width = 92)
		self.ColumnLengths = {'RA':14,'DEC':14,'MJD':6,'PLATEID':5,'FIBERID':5,'REDSHIFT':14,'GroupID':6,'Interesting':18}

		print "Populating List"

		self.ListEntries = (self.BuildListEntries(i) for i in Data)

		print "Showing Lists"
		
		self.populateList()
		self.window.add(self.lists)		

	def BuildListEntries(self, Row):


		return "|".join(((('{:<%s}' % self.ColumnLengths[i]).format(str(Row[i]))) for i in self.Headers if i != 'FILENAME'))

	def populateList(self):

		try:
			self.lists.insert(Tk.END, self.ListEntries.next())
			self.after(1 ,self.populateList)
	
		except StopIteration:

			pass
		


class Window(Tk.Frame): #Example of a window application inside a frame

        def __init__(self, master):

                Tk.Frame.__init__(self, master)
                #########################################

		self.DataTable = FullDataTable(self, data)
		self.DataTable.pack(expand = 1, fill = Tk.BOTH, side = Tk.RIGHT)

		self.Props = BasicDataDisplay(self, 9)
		self.Props.setTitles(['Spam:','Eggs:','Foo:','Bar:'], 7)
		self.Props.setData([20.453235,1.345274,0.55212,5524], 10)
		self.Props.pack(expand = 0, fill = Tk.BOTH, side = Tk.LEFT)


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
		Data = [data[self.c][i] for i in ('RA','DEC','REDSHIFT','GroupID')]
	
		self.MainWindow.Props.setTitles(Titles, 10)
		self.MainWindow.Props.setData(Data,12) 
		self.c += 1

app = App()
app.mainloop()
'''
