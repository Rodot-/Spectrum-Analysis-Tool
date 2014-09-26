import matplotlib
matplotlib.use('TkAgg')
import time


from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
import sys
from pylab import *

if sys.version_info[0] < 3:
        import Tkinter as Tk
else:
        import tkinter as Tk




#################################
from random import random, randint
def append_mult(list, items):
        for i in range(len(items)):
                list.append(items[i])
        return list

DATA = []
for i in range(10):
        DATA.append([])
        for j in range(30):
                #DATA[i].append([])
                DATA[i].append(['PLOT '+str(i) + '-' + str(j), 1, [k + random() for k in range(30)], [randint(0,10)/100.0 for k in range(30)]])

for i in range(len(DATA)):
        for j in range(len(DATA[i])):
                DATA[i][j] = append_mult(DATA[i][j],[random() * 100 ,random() * 10,randint(50000,60000),randint(0,1000),randint(0,100)])
####################################





root = Tk.Tk()
root.wm_title('Plotting Interface')
root.geometry('1200x600-100+100')

#Available Line Colors

colorcode = ['#FF0000','#00FF00','#0000FF','#FFFF00','#00FFFF','#FF00FF','#FFAA00','#AAFF00','#00AAFF','#FF00AA','#00FFAA','#AA00FF','#AA0000','#00AA00','#0000AA','#AAAA00','#00AAAA','#AA00AA','#AA4400','#44AA00','#0044AA','#AA0044','#00AA44','#4400AA','#440000','#004400','#000044','#444400','#004444','#440044','#DD8800','#88DD00','#0088DD','#DD0088','#00DD88','#8800DD']


class Interface: #The Main Plotting Window

	def __init__(self, master, data):

		self.master = master
		self.data = data
		self.iter = 0
		self.zoomState = 0 #Default, zoom is off		

		#Set Up All Frames

		self.MainPlotFrame = Tk.Frame(master, height = 500)
		self.PlotFrameLeft = Tk.Frame(self.MainPlotFrame)
		self.PlotFrameRight = Tk.Frame(self.MainPlotFrame)
		self.ButtonFrame = Tk.Frame(master)

		#Set up Plots
		
		self.plots = [PlottingWindow(self.PlotFrameLeft), PlottingWindow(self.PlotFrameLeft), PlottingWindow(self.PlotFrameRight,size = [1,1]), PlottingWindow(self.PlotFrameRight,size = [1,1])]

		#Set Up Buttons		
		
		self.QUIT = Tk.Button(master = self.ButtonFrame, text = "Quit", command = self.MainPlotFrame.quit)

		self.zoomButton = Tk.Button(master = self.ButtonFrame, text = "Zoom", command = self.changeZoomState)

		#Packing Up
	
		self.MainPlotFrame.pack(expand = 1, fill = Tk.BOTH, side = Tk.TOP)
		self.PlotFrameLeft.pack(expand = 1, fill = Tk.BOTH, side = Tk.LEFT)
		self.ButtonFrame.pack(expand = 0, fill = Tk.BOTH, side = Tk.BOTTOM)
		self.QUIT.pack(side = Tk.LEFT)
		
		self.zoomButton.pack(side = Tk.LEFT)

		#Plotting the data

		for i in range(30):
			self.plots[0](self.data[1][i][2], self.data[1][i][3])
			self.plots[2](self.data[1][i][2], self.data[1][i][3])

		self.zoomManager1 = ZoomManager(self.plots[0],self.plots[2])
		self.MainPlotFrame.update()
		###Test Stuff
	
	def changeZoomState(self):
		
		if self.zoomState == 0: #Checks if zooming, if not, zooms

			self.zoomState = 1
		
			self.PlotFrameRight.pack(expand = 1, fill = Tk.BOTH, side = Tk.RIGHT)
                	self.zoomButton.config(relief = Tk.SUNKEN)
                	self.zoomManager1.zoomOn()
		
		else: #If already zooming, unzooms

			self.zoomState = 0

	                self.PlotFrameRight.pack_forget()
        	        self.zoomButton.config(relief = Tk.RAISED)
			self.zoomManager1.zoomOff()


		###End Test stuff

class PlottingWindow: #A class that creates a plotting window

	def __init__(self, master, size = [6,1]):

		self.frame = master #create the frame

		#Setting up the plot with matplotlib

		self.fig = figure(figsize = (size[0], size[1]), dpi = 80)
		self.ax = self.fig.add_subplot(111)
		self.canvas = FigureCanvasTkAgg(self.fig, master = self.frame)
		self.canvas.get_tk_widget().pack(fill = Tk.BOTH, expand = 1)
		self.canvas._tkcanvas.pack(fill = Tk.BOTH, expand = 1)

		if size != [6,1]:

			self.ax.set_xlim((4,6))
			self.ax.set_ylim((0.04,0.06))

		self.lines = [] #Allow for multiple lines

	def __call__(self,Xdata, Ydata): #Plots and given data

		colors = colorcode

		line, = self.ax.plot(Xdata, Ydata, color = colors[len(self.lines)-1])	

		self.lines.append(line)

	def set_axes(self, pos = [0,0]): #Sets the postion, needs reworking

		ylim = self.ax.get_ylim()
		xlim = self.ax.get_xlim()
		
		self.ax.set_ylim(pos[1] - (ylim[1]-ylim[0])/2.0, pos[1] + (ylim[1] - ylim[0])/2.0)
		self.ax.set_xlim(pos[0] - (xlim[1]-xlim[0])/2.0, pos[0] + (xlim[1] - xlim[0])/2.0)

		self.fig.canvas.draw()

	def zoom(self, z = 0.0): #zoom in on plot, want to rewrite
		
		if z < 0.0:
	
			z = 2.0**0.5

		else:
			z = 0.5**0.5

		y = self.ax.get_ylim()
		x = self.ax.get_xlim()

		self.ax.set_ylim(y[0]+(1-z)*(y[1]-y[0])/2.0, y[0] + (1+z)*(y[1]-y[0])/2.0) 
		self.ax.set_xlim(x[0]+(1-z)*(x[1]-x[0])/2.0,x[0] + (1+z)*(x[1]-x[0])/2.0) 



		self.fig.canvas.draw()
	
class ZoomManager: #Manages the zoom function between a Main Plot and it's zoom

	def __init__(self, MainPlot, ZoomPlot):

		self.MainPlot = MainPlot
		self.ZoomPlot = ZoomPlot

	def scrollZoom(self, event): #Use scrollbar to zoom

		if event.inaxes != self.MainPlot.ax: return
		self.ZoomPlot.zoom(event.step)

	def setZoomPos(self,event): #Sets the position in the zoom plot

		if event.inaxes != self.MainPlot.ax: return
		self.ZoomPlot.set_axes(pos = [event.xdata,event.ydata])	

	def zoomOn(self): #Connects the getMousePos function

		self.activeZoom = self.MainPlot.fig.canvas.mpl_connect('motion_notify_event', self.setZoomPos)

		self.ScrollZoom = self.MainPlot.fig.canvas.mpl_connect('scroll_event', self.scrollZoom)

	def zoomOff(self): #Disconnects said function

		self.MainPlot.fig.canvas.mpl_disconnect(self.activeZoom)

		self.MainPlot.fig.canvas.mpl_disconnect(self.ScrollZoom)

interface = Interface(root, DATA)

Tk.mainloop()


