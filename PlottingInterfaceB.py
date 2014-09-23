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
                DATA[i].append(['PLOT '+str(i) + '-' + str(j), 1, [k + random() for k in range(10)], [randint(0,10)/100.0 for k in range(10)]])

for i in range(len(DATA)):
        for j in range(len(DATA[i])):
                DATA[i][j] = append_mult(DATA[i][j],[random() * 100 ,random() * 10,randint(50000,60000),randint(0,1000),randint(0,100)])
####################################





root = Tk.Tk()
root.wm_title('Plotting Interface')
root.geometry('1200x600-100+100')

class Interface: #The Main Plotting Window

	def __init__(self, master, data):

		self.master = master
		self.data = data
		self.iter = 0

		#Set Up All Frames

		self.MainPlotFrame = Tk.Frame(master, height = 500)
		self.PlotFrameLeft = Tk.Frame(self.MainPlotFrame)
		self.PlotFrameRight = Tk.Frame(self.MainPlotFrame)
		self.ButtonFrame = Tk.Frame(master)

		#Set up Plots
		
		self.plots = [PlottingWindow(self.PlotFrameLeft), PlottingWindow(self.PlotFrameLeft), PlottingWindow(self.PlotFrameRight,size = [1,1]), PlottingWindow(self.PlotFrameRight,size = [1,1])]

		#Set Up Buttons		
		
		self.QUIT = Tk.Button(master = self.ButtonFrame, text = "Quit", command = self.MainPlotFrame.quit)

		self.AddPlot = Tk.Button(master = self.ButtonFrame, text = "Zoom Plot", command = self.zoom_plot)

		self.NoAddPlot = Tk.Button(master = self.ButtonFrame, text = "Remove Zoom", command = self.no_zoom_plot)

		#Packing Up
	
		self.MainPlotFrame.pack(expand = 1, fill = Tk.BOTH, side = Tk.TOP)
		self.PlotFrameLeft.pack(expand = 1, fill = Tk.BOTH, side = Tk.LEFT)
		self.ButtonFrame.pack(expand = 0, fill = Tk.BOTH, side = Tk.BOTTOM)
		self.QUIT.pack(side = Tk.LEFT)
		
		self.AddPlot.pack(side = Tk.LEFT)

		#Plotting the data

		self.plots[0](self.data, self.iter)
		self.plots[2](self.data, self.iter)

		self.MainPlotFrame.update()

	def zoom_plot(self): #Shows a set of Zoomed Plots
		
		self.PlotFrameRight.pack(expand = 1, fill = Tk.BOTH, side = Tk.RIGHT)
		self.AddPlot.pack_forget()
		self.NoAddPlot.pack(side = Tk.LEFT)

	def no_zoom_plot(self): #Removes Zoomed Plots

		self.PlotFrameRight.pack_forget()
		self.NoAddPlot.pack_forget()
		self.AddPlot.pack(side = Tk.LEFT)

	
class PlottingWindow: #A class that creates a plotting window

	def __init__(self, master, size = [6,1]):

		self.frame = master #create the frame

		#Setting up the plot with matplotlib

		self.fig = figure(figsize = (size[0], size[1]), dpi = 80)
		self.ax = self.fig.add_subplot(111)
		self.canvas = FigureCanvasTkAgg(self.fig, master = self.frame)
		self.canvas.get_tk_widget().pack(fill = Tk.BOTH, expand = 1)
		self.canvas._tkcanvas.pack(fill = Tk.BOTH, expand = 1)

		self.lines = [] #Allow for multiple lines

	def __call__(self, data, iter):

		colors = colorcode(data[iter])
		print colors

		for i in range(len(data[iter])):

			line, = self.ax.plot(data[iter][i][2], data[iter][i][3], color = colors[i])	

			self.lines.append(line)
			

		
def colorcode(data):

	colors = []

	for i in range(len(data)):

		colors.append(hex(i * 16777215/len(data))[2:])
		for n in range(6-len(colors[i])):
			colors[i] += '0'
		colors[i] = '#' + colors[i]


	return colors


interface = Interface(root, DATA)

Tk.mainloop()
