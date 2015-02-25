from PlottingClasses import *
from matplotlib.widgets import MultiCursor
import DataClasses
import numpy as np
import time
import os
import sys
import eventlet
import Transformations

if sys.version_info[0] < 3:
        import Tkinter as Tk
else:
        import tkinter as Tk


class Window(Tk.Frame): #Example of a window application inside a frame

	def __init__(self, master):

		self.data = DataClasses.Data()
		Tk.Frame.__init__(self, master)

		self.Navigation = Tk.Frame(self)
		self.Manipulation = Tk.Frame(self)

		#########################################
		self.PLOT = PlottingWindow(self)
		self.PLOT.AddSubplot()
		self.PLOT.AddSubplot(self.PLOT.ax[0], combineX = True)


		self.NextButton = Tk.Button(self.Navigation, text = 'Next', command = self.NEXT)
		self.PreviousButton = Tk.Button(self.Navigation, text = 'Previous', command = self.PREV)

		self.ToggleInteresting = Tk.Button(self.Manipulation, text = 'View Interesting', command = self.toggleInteresting)

		self.Toggle2D = Tk.Button(self.Manipulation, text = 'View Subtraction', command = self.toggle2d)

	
		self.Manipulation.pack(side = Tk.TOP, expand = 0, fill = Tk.X)
		self.Navigation.pack(side = Tk.BOTTOM, expand = 0, fill = Tk.X)
		self.PLOT.pack(expand = 1, fill = Tk.BOTH)
		self.NextButton.pack(side = Tk.RIGHT, expand = 1, fill = Tk.X)
		self.PreviousButton.pack(side = Tk.RIGHT, fill = Tk.X, expand = 1)
		self.ToggleInteresting.pack(side = Tk.RIGHT, expand = 0, fill = Tk.X)
		self.Toggle2D.pack(side = Tk.RIGHT, expand = 0, fill = Tk.X)

		self.PLOT.ax[0].set_ylabel(r'$\mathtt{Flux}$')
		self.PLOT.ax[1].set_ylabel(r'$\mathtt{Flux}$')
		self.PLOT.ax[1].set_xlabel(r'$\mathtt{\lambda \/ (\AA)}$')
		self.PLOT.ax[0].set_xlabel(r'$\mathtt{\lambda \/ (\AA)}$')


		self.Transform = []
		self.Transform.append(Transformations.smooth)
		self.Transform.append(Transformations.smooth)

		self.NEXT()

                self.cursor = MultiCursor(self.PLOT.fig.canvas,(self.PLOT.ax[0], self.PLOT.ax[1]), color='black', linewidth=0.2 , useblit = True)
	

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

		[self.PLOT.Plot(i[1], i[0], ax_index) for i in DR]

		print "Plot Lines Time: ", time.clock() - T0
		T0 = time.clock()

		self.PLOT.ax[ax_index].relim()
		self.PLOT.ax[ax_index].autoscale_view(True, True, True)
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
		else:
			T = self.Transform[1]
		self.plotCurrent(1, T)
		self.PLOT.update()

class App(Tk.Tk):
	def __init__(self):

		Tk.Tk.__init__(self)
		self.title("Plotting Interface")
		self.protocol("WM_DELETE_WINDOW",self.quit)
		##########################################

		self.MainWindow = Window(self)
		self.MainWindow.pack(expand = 1, fill = Tk.BOTH)

		#self.MainWindow.plotCurrent(0)
		#self.MainWindow.plotCurrent(1)

app = App()
app.mainloop()

