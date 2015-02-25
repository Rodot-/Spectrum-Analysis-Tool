import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
import sys
from pylab import *
import time

if sys.version_info[0] < 3:
	import Tkinter as Tk
else:
	import tkinter as Tk


class PlottingWindow(Tk.Frame):

	def __init__(self, master, size = [6,3], title = None, xlabel = None, ylabel = None):

		Tk.Frame.__init__(self, master)

		self.fig = figure(figsize = (size[0], size[1]), dpi = 80)
		self.ax = []
		self.lines = [[]]
		self.canvas = FigureCanvasTkAgg(self.fig, master = self)
		toolbar = NavigationToolbar2TkAgg(self.canvas, self)
		toolbar.update()
		self.canvas.get_tk_widget().pack(fill = Tk.BOTH, expand = 1)
		self.canvas._tkcanvas.pack(fill = Tk.BOTH, expand = 1)

	def updateSubplotGeometry(self, direction = 1):
		####################################
		# This function updates the        #
		# geometry of the figure to resize #
		# the subplots correctly           #
		####################################

		n = len(self.fig.axes)
		for i in xrange(n):

			self.fig.axes[i].change_geometry(n+direction, 1, i + 1)

		return n

	def AddSubplot(self, shareX = None, shareY = None, combineX = False):
		####################################
		# This function adds a subplot     #
		# to the last position in the fig  #
		# Optional parameters to share an  #
		# axis with another subplot        #
		####################################

		n = self.updateSubplotGeometry()
		self.ax.append(self.fig.add_subplot(n+1,1,n+1, sharex = shareX, sharey = shareY))
		if combineX:

			self.fig.subplots_adjust(hspace = 0)
			plt.setp([a.get_xticklabels() for a in self.fig.axes[:-1]], visible=False)
	
		self.lines.append([])

	def RemoveSubplot(self, ax_index = -1):
		#####################################
		# This function will delete a       #
		# subplot at the desired index      #
		# Defaults to last subplot          #
		#####################################

		self.lines.remove(self.lines[ax_index])
		self.fig.delaxes(self.ax[ax_index])
		self.ax.remove(self.ax[ax_index])
		self.updateSubplotGeometry(0)

	def Plot(self, x, y, ax_index = 0, pos = 0):
		######################################
		# This funtion will plot equal sized #
		# arrays x and y at the desired      #
		# index                              #
		######################################

		if pos == len(self.lines[ax_index]):

			self.lines[ax_index].append(self.ax[ax_index].plot(x, y)[0])
		elif self.lines[ax_index][pos].get_xdata() == []:
			self.lines[ax_index][pos].set_data(x, y)

		else:

			self.Plot(x, y, ax_index, pos + 1)

	def ClearPlot(self, ax_index = 0):
		######################################
		# This Function Will Clear all Lines #
		# in a Subplot at the Desired Index  #
		######################################

		for i in range(len(self.lines[ax_index])):
			self.lines[ax_index][i].set_data([],[])

	def update(self):
		######################################
		# This function will update the      #
		# entire plotting canvas             #
		######################################

		T0 = time.time()
		self.canvas.draw()
		print "Update Plot Time: ", time.time() - T0

	def HideLine(self, line):
		######################################
		# Makes the desired line invisible   #
		######################################	
	
		line.set_linestyle(None)

	def ShowLine(self, line):
		######################################
		# Makes the desired line visible     #
		######################################

		line.set_linestyle("-")

