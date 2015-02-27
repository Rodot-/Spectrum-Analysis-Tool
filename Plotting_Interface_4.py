from PlottingClasses import *
from matplotlib.widgets import MultiCursor
import DataClasses
import numpy as np
import time
import os
import sys
import eventlet
import Transformations
import DataTables
import Science
import tkFont

if sys.version_info[0] < 3:
        import Tkinter as Tk
else:
        import tkinter as Tk


pool = eventlet.GreenPool(size = 100)

class Window(Tk.Frame): #Example of a window application inside a frame

	def __init__(self, master):

		self.data = DataClasses.Data()
		Tk.Frame.__init__(self, master)

		if len(sys.argv) > 1:
	
				self.data.DataPosition = int(sys.argv[1])

		self.Navigation = Tk.Frame(self)
		self.Manipulation = Tk.Frame(self)
		self.Properties = Tk.Frame(self)


		#########################################
		self.PLOT = PlottingWindow(self)
		self.PLOT.AddSubplot()
		self.PLOT.AddSubplot(self.PLOT.ax[0], combineX = True)

		self.BasicInformation = DataTables.BasicDataDisplay(self.Properties, 4)
		self.BasicInformation.setTitles(['RA:','DEC:','Redshift:','Group ID:'], 10)
		self.Slines = DataTables.BasicDataDisplay(self.Properties, len(Science.Slines_Values))

		self.Slines.setTitles(Science.Slines.dtype.names, 8)

		self.NextButton = Tk.Button(self.Navigation, text = 'Next', command = self.NEXT)
		self.PreviousButton = Tk.Button(self.Navigation, text = 'Previous', command = self.PREV)

		self.ToggleInteresting = Tk.Button(self.Manipulation, text = 'View Interesting', command = self.toggleInteresting)

		self.Toggle2D = Tk.Button(self.Manipulation, text = 'View Subtraction', command = self.toggle2d)

		self.ToggleMark = Tk.Button(self.Manipulation, text = 'Interesting', command = self.toggleMark)

		self.SaveSession = Tk.Button(self.Manipulation, text = 'Save', command = self.data.saveInterestingObjects)

		self.Manipulation.pack(side = Tk.TOP, expand = 0, fill = Tk.X)
		self.Navigation.pack(side = Tk.BOTTOM, expand = 0, fill = Tk.X)
		self.Properties.pack(side = Tk.LEFT, expand = 0, fill = Tk.BOTH)	
		self.PLOT.pack(expand = 1, fill = Tk.BOTH)
		self.BasicInformation.pack(side = Tk.TOP, expand = 0, fill = Tk.BOTH)
		self.Slines.pack(side = Tk.TOP, expand = 0, fill = Tk.BOTH)
		self.NextButton.pack(side = Tk.RIGHT, expand = 1, fill = Tk.X)
		self.PreviousButton.pack(side = Tk.RIGHT, fill = Tk.X, expand = 1)
		self.ToggleInteresting.pack(side = Tk.RIGHT, expand = 1, fill = Tk.X)
		self.ToggleMark.pack(side = Tk.RIGHT, expand = 1, fill = Tk.X)
		self.Toggle2D.pack(side = Tk.RIGHT, expand = 1, fill = Tk.X)
		self.SaveSession.pack(side = Tk.RIGHT, expand = 1, fill = Tk.X)

		self.PLOT.ax[0].set_ylabel(r'$\mathtt{Flux}$')
		self.PLOT.ax[1].set_ylabel(r'$\mathtt{Flux}$')
		self.PLOT.ax[1].set_xlabel(r'$\mathtt{\lambda \/ (\AA)}$')
		self.PLOT.ax[0].set_xlabel(r'$\mathtt{\lambda \/ (\AA)}$')


		self.Transform = []
		self.Transform.append(Transformations.smooth)
		self.Transform.append(Transformations.smooth)

		self.NEXT()

                self.cursor = MultiCursor(self.PLOT.fig.canvas,(self.PLOT.ax[0], self.PLOT.ax[1]), color='#999999', linewidth=1.0 , useblit = True)
	

	def NEXT(self):

		self.data.NextGroup()
		self.UpdatePlots()		

	def PREV(self):

		self.data.PreviousGroup()
		self.UpdatePlots()		

	def plotCurrent(self, ax_index, Transform = None, **kwargs):

		T0 = time.clock()

		if Transform == None: Transform = self.Transform[ax_index]

		self.PLOT.ClearPlot(ax_index)

		DR = Transform(self.data.ReleaseDataPoints(), **kwargs)

		for i in DR: self.PLOT.Plot(i[1], i[0], ax_index)

		print "Plot Lines Time: ", time.clock() - T0
		T0 = time.clock()

		self.PLOT.ax[ax_index].relim()
		self.PLOT.ax[ax_index].autoscale(enable = True)
	
		print "Update Limits Time: ", time.clock() - T0

	def toggleInteresting(self):

		self.data.ToggleInteresting()
		if self.ToggleInteresting["text"] == 'View Interesting':

			self.ToggleInteresting["text"] = 'View All'
			self.UpdatePlots()

		else:
	
			self.ToggleInteresting["text"] = 'View Interesting'
			self.UpdatePlots()

	def toggleMark(self):

		if self.ToggleMark["relief"] == Tk.SUNKEN:

			self.ToggleMark["relief"] = Tk.RAISED
			self.data.MarkAs("Not_Interesting")

		else:

			self.ToggleMark["relief"] = Tk.SUNKEN
			self.data.MarkAs("Interesting")

	def toggle2d(self):

		if self.Toggle2D["text"] == 'View Subtraction':

			self.Toggle2D["text"] = 'View Division'
			self.Transform[1] = Transformations.subtract
			self.UpdatePlots()

		else:
	
			self.Toggle2D["text"] = 'View Subtraction'
			self.Transform[1] = Transformations.divide
			self.UpdatePlots()

	def UpdatePlots(self):

		self.plotCurrent(0)
		if len(self.data.currentData) != 2:
			T = Transformations.smooth
			self.Toggle2D["state"] = Tk.DISABLED
		else:
			T = self.Transform[1]
			self.Toggle2D["state"] = Tk.NORMAL
		self.plotCurrent(1, T)
		self.PLOT.update()
		self.updateFields()

	def updateFields(self):

		T0 = time.time()

		if self.data.currentData[0]['Interesting'] == 'Interesting':

			self.ToggleMark["relief"] = Tk.SUNKEN
		else:
	
			self.ToggleMark["relief"] = Tk.RAISED

		self.BasicInformation.setData([self.data.currentDataArray[self.data.DataPosition][i] for i in ['RA','DEC','REDSHIFT','GroupID']], 12)

		self.Slines.setData(Science.RedShiftSlines(float(self.data.currentDataArray[self.data.DataPosition]['REDSHIFT'])), 12)

		print "Update Fields Time: ", time.time() - T0

class SpectraProperties(Tk.Frame):

	def __init__(self, master):

		Tk.Frame.__init__(self, master)

		


class App(Tk.Tk):
	def __init__(self):

		Tk.Tk.__init__(self)
		self.title("Plotting Interface")
		self.geometry('1200x600-100+100')
		self.protocol("WM_DELETE_WINDOW",self.Quit)
		##########################################

		self.MainWindow = Window(self)
		self.MainWindow.pack(expand = 1, fill = Tk.BOTH)

	def Quit(self):

		self.MainWindow.data.saveInterestingObjects()
		self.after_idle(self.quit)


app = App()
app.mainloop()

