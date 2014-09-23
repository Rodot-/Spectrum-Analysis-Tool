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

root = Tk.Tk()
root.wm_title('Plotting Interface')

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
		DATA[i].append(['PLOT '+str(i) + '-' + str(j), Tk.BooleanVar(), [randint(0,10) + random() for k in range(10)], [randint(0,2) + random() for k in range(10)]])

for i in range(len(DATA)):
	for j in range(len(DATA[i])):
		DATA[i][j] = append_mult(DATA[i][j],[random() * 100 ,random() * 10,randint(50000,60000),randint(0,1000),randint(0,100)])
####################################



class Interface: #Overall Interface

	def __init__(self, master, data):
		
		self.data = data

		PLOT = Tk.Frame(master)
		AXES = _plot(PLOT, self.data)
		PLOT.pack(side = Tk.TOP, fill = Tk.BOTH, expand = 1)

		frame = Tk.Frame(master)
		frame.pack(expand = 1, fill = Tk.BOTH, side = Tk.TOP)

		self.QUIT = Tk.Button(master = frame, text = "Quit", command = frame.quit)
		self.NEXT = Tk.Button(master = frame, text = "Next", command = ChangePlot(AXES, 'next'))
		self.PREVIOUS = Tk.Button(master = frame, text = "Previous", command = ChangePlot(AXES, 'previous'))

	
		self.QUIT.pack(side = Tk.LEFT)
		self.NEXT.pack(side = Tk.LEFT)
		self.PREVIOUS.pack(side = Tk.LEFT)
		frame.update()	

class _plot: #The Physical Canvas
	
	def __init__(self, master, data):
		self.frame = Tk.Frame(master)
		self.frame.pack(expand = 1, fill = Tk.BOTH, side = Tk.LEFT)

		self.data = data
		self.iter = 0

		self.fig = figure(figsize = (12, 4), dpi = 80)
		self.ax = []
		self.ax.append(self.fig.add_subplot(111))
		self.canvas = FigureCanvasTkAgg(self.fig, master = self.frame)
		self.canvas.get_tk_widget().pack(side = Tk.LEFT, fill = Tk.BOTH, expand = 1)
		self.canvas._tkcanvas.pack(side = Tk.LEFT, fill = Tk.BOTH, expand = 1)
		self.top = Tk.Toplevel()
		#self.BUTTONS = PlotButtons(self.frame, self)
	
		self.plotting = PlotThis(self)
		self.update()
		self.good = 0
	

	def update(self):

		self.canvas.draw()

	def clearCanvas(self):

		if self.good == 0:

			self.good += 1

			self.plotting.labels.kill()
			self.plotting = PlotThis(self)
			self.update()

			self.good = 0
	
class PlotButtons: #Buttons and Options

	def __init__(self, master, parent):

		self.frame = Tk.Frame(master)
		self.frame.pack(expand = 1, fill = Tk.BOTH)

		self.QUIT = Tk.Button(master = self.frame, text = "QUIT", command = self.frame.quit)
		self.PLOTRAND = Tk.Button(master = self.frame, text = "Plot Random", command = Add_Plot(parent.ax[-1]))

		self.QUIT.pack(expand = 1)
		self.PLOTRAND.pack(expand = 1)

class PlotThis: #Plots the selected data

	def __init__(self, parent):

		self.iter = parent.iter
		self.Plot = parent.ax[-1]
		self.data = parent.data
		self.linelist = []

		for i in range(len(self.data[self.iter])):
			colorcode = "#"
			for n in range(int(i/5)):
				colorcode += str(mod(i,7))
			colorcode += "f"
			for n in range(7-len(colorcode)):
				colorcode += "8"

			line, = self.Plot.plot(self.data[self.iter][i][2], self.data[self.iter][i][3], color = colorcode)	
			self.linelist.append(line)
		self.top = parent.top	
		self.labels = PlotLabels(self.top, parent, self.linelist) 				


class PlotLabels: #Labels the data, allows you to hide or show data

	def __init__(self, master, parent, lines):

		self.frame = Tk.Frame(master)
		self.frame.pack(expand = 1, side = Tk.LEFT, fill = Tk.BOTH)
		self.data = parent.data
		self.iter = parent.iter
		self.checks = []
		self.descr = []
		self.plots = lines
		self.Plot = parent.ax[-1]
		for i in range(len(self.plots)):

			Text = self.data[self.iter][i][0] + " | " + str(self.data[self.iter][i][6]) + ", " + str(self.data[self.iter][i][7]) + ", " + str(self.data[self.iter][i][8]) 
			
			self.checks.append(Tk.Checkbutton(master = self.frame, text = Text, variable = self.data[self.iter][i][1], command = self.hide, bg = getp(self.plots[i],'color'), justify = Tk.LEFT))
			self.checks[-1].select()
			self.checks[-1].pack(expand = 1, side = Tk.TOP, anchor = Tk.W, fill = Tk.BOTH)
		self.frame.update()	

		self.hide()	

	def hide(self): 
		
		for i in range(len(self.plots)):
			
			if not self.data[self.iter][i][1].get() and self.plots[i].get_linestyle != "None":
			
				self.plots[i].set_linestyle("None")
			elif self.data[self.iter][i][1].get() and self.plots[i].get_linestyle != '-':
				self.plots[i].set_linestyle('-')
	
		self.plots[i].figure.canvas.draw()
		self.frame.update()


	def kill(self):

		for i in range(len(self.plots)):
			self.checks[-1].destroy()
			self.checks.remove(self.checks[-1])
			self.plots.remove(self.plots[-1])
			del(self.Plot.lines[-1])
			self.frame.destroy()
'''
class PlotInfo:

	def __init__(self, master):
'''

class ChangePlot: #Changes to the next set of data

	def __init__(self, parent, command):

			
		self.iter = parent.iter
		self.parent = parent
		self.command = command
		self.length = len(parent.data)

	def __call__(self):
		
			

		if self.command == 'next':

			if self.iter < self.length - 1:
		
				self.iter += 1

			else:
				
				self.iter = 0

		elif self.command == 'previous':

			if self.iter > 0:

				self.iter -= 1

			else:
		
				self.iter = self.length - 1
		self.parent.iter = self.iter	
		self.parent.clearCanvas()			

class Add_Plot:
	
	def __init__(self, Plot):
		self.Plot = Plot
	
	def __call__(self):
		self.line, = self.Plot.plot([random(),random(),random()])
		self.line.figure.canvas.draw()
	


def _quit():
	root.quit()
	root.destroy()	


interface = Interface(root, DATA)

Tk.mainloop()
