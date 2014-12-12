print "Importing Packages"
print "Importing matplotlib"
import matplotlib
matplotlib.use('TkAgg')
print "Importing Time"
import time
print "Importing eventlet"
import eventlet
print "Importing DataManager"
import DataManager
print "Importing astropy.io.fits"
from astropy.io import fits
print "Importing mpl backends"
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
import sys
print "Importing Pylab"
from pylab import *

if sys.version_info[0] < 3:
        import Tkinter as Tk
else:
        import tkinter as Tk



pool = eventlet.GreenPool(size = 1000)
#root = Tk.Tk()
#root.wm_title('Plotting Interface')
#root.geometry('1200x600-100+100')

Window = Tk.Tk()
Window.wm_title('Plotting Interface')
Window.geometry('1200x600-100+100')

#Available Line Colors

colorcode0 = ['#FF0000','#00FF00','#0000FF','#FFFF00','#00FFFF','#FF00FF','#FFAA00','#AAFF00','#00AAFF','#FF00AA','#00FFAA','#AA00FF','#AA0000','#00AA00','#0000AA','#AAAA00','#00AAAA','#AA00AA','#AA4400','#44AA00','#0044AA','#AA0044','#00AA44','#4400AA','#440000','#004400','#000044','#444400','#004444','#440044','#DD8800','#88DD00','#0088DD','#DD0088','#00DD88','#8800DD']


colorcode6 = ['#FF0000','#AAAA00','#00FF00','#00AAAA','#0000FF','#AA00AA']

colorcode = ['#FF0000','#EE1000','#DD2000','#CC3000','#BB3900','#AA4000','#994400','#885500','#776600','#667700','#558800','#449900','#40AA00','#39BB00','#30CC00','#20DD00','#10EE00','#00FF00','#00EE10','#00DD20','#00CC30','#00BB39','#00AA40','#009944','#008855','#007766','#006677','#005588','#004499','#0040AA','#0039BB','#0030CC','#0020DD','#0010EE','#0000FF']


class Interface: #The Main Plotting Window

	def __init__(self, master):

		print "Initializing Interface"

		self.master = master
		self.iter = 0
		self.zoomState = 0 #Default, zoom is off		

		print "Setting Up All Frames"

		self.MainPlotFrame = Tk.Frame(master, height = 500)
		self.PlotFrameLeft = Tk.Frame(self.MainPlotFrame)
		self.PlotFrameRight = Tk.Frame(self.MainPlotFrame)
		self.ButtonFrame = Tk.Frame(master)
		self.InfoFrame = Tk.Frame(master)
		#self.DataFrame = Tk.Toplevel()

		self.Info = LabelWindow(self.InfoFrame)

                self.Info.addColumn('REDSHIFT',[])
                self.Info.addColumn('RIGHT ASCENSION',[])
                self.Info.addColumn('DECLINATION',[])
                self.Info.addColumn('MARK',[])
                self.Info.addColumn('GROUP SIZE',[])
                self.Info.addColumn('GROUP ID',[])


		print "Setting up Plots"
		
		self.plots = [PlottingWindow(self.PlotFrameLeft), PlottingWindow(self.PlotFrameLeft), PlottingWindow(self.PlotFrameRight), PlottingWindow(self.PlotFrameRight)]

                self.Spectra = PlotManager(self.plots[0], self.plots[2], self.plots[1], self.plots[3], DataManager.getMatchesArray())

		print "Seting Up Buttons"		
		
		self.QUIT = Tk.Button(master = self.ButtonFrame, text = "Quit", command = self.MainPlotFrame.quit)

		self.zoomButton = Tk.Button(master = self.ButtonFrame, text = "Zoom", command = self.changeZoomState)

		self.NextData = Tk.Button(master = self.ButtonFrame, text = "Next", command = self.NEXT)

		self.PrevData = Tk.Button(master = self.ButtonFrame, text = "Previous", command = self.PREV)

		self.MarkInteresting = Tk.Button(master = self.ButtonFrame, text = 'Mark', command = self.MARK_INTERESTING)

		self.UnmarkInteresting = Tk.Button(master = self.ButtonFrame, text = 'Unmark', command = self.UNMARK_INTERESTING)

		self.SaveInteresting = Tk.Button(master = self.ButtonFrame, text = 'Save Marked', command = self.Spectra.saveInteresting)

		self.ViewInteresting = Tk.Button(master = self.ButtonFrame, text = 'View Interesting', command = self.Spectra.SwitchToInteresting)

		self.JumpAhead = Tk.Button(master = self.ButtonFrame, text = 'Jump 1000', command = self.Jump1000)

		self.JumpAheadALittle = Tk.Button(master = self.ButtonFrame, text = 'Jump 100', command = self.Jump100)

		self.AnimatePlot = Tk.Button(master = self.ButtonFrame, text = 'Animate', command = self.Spectra.Animate)

		print "Packing Up"
	
		self.InfoFrame.pack(expand = 0, fill = Tk.BOTH, side = Tk.TOP)

		self.MainPlotFrame.pack(expand = 1, fill = Tk.BOTH, side = Tk.TOP)
		self.PlotFrameLeft.pack(expand = 1, fill = Tk.BOTH, side = Tk.LEFT)
		self.ButtonFrame.pack(expand = 0, fill = Tk.BOTH, side = Tk.BOTTOM)

		self.QUIT.pack(side = Tk.LEFT)

		self.AnimatePlot.pack(side = Tk.LEFT)
		
		self.zoomButton.pack(side = Tk.LEFT)

		self.PrevData.pack(side = Tk.LEFT)

		self.NextData.pack(side = Tk.LEFT)

		self.JumpAhead.pack(side = Tk.LEFT)

		self.JumpAheadALittle.pack(side = Tk.LEFT)

		self.MarkInteresting.pack(side = Tk.LEFT)

		self.UnmarkInteresting.pack(side = Tk.LEFT)

		self.SaveInteresting.pack(side = Tk.LEFT)

		self.ViewInteresting.pack(side = Tk.LEFT)

		#self.DataFrame.pack(side = Tk.RIGHT, expand = 1, fill = Tk.BOTH)

		print "Plotting data"

		self.UPDATE_PLOTS()


		#self.Spectra.PlotAllSpectra(S = 10)

		#self.Spectra.replotAllSpectra(plot = 'sub', S = 1)		

		#for i in range(30):
		#	self.plots[0](self.data[1][i][2], self.data[1][i][3])
		#	self.plots[2](self.data[1][i][2], self.data[1][i][3])

		#Adding in some Columns
	
		#self.DataInfo.addColumn('MJD', [self.data[1][k][4] for k in range(30)])
		#self.DataInfo.addColumn('Plate', [self.data[1][j][5] for j in range(30)])
		#self.DataInfo.addColumn('Fiber', [self.data[1][l][6] for l in range(30)])
		
		print "Setting Up Tools"

		self.zoomManager1 = ZoomManager(self.plots[0],self.plots[2])
		self.zoomManager2 = ZoomManager(self.plots[1],self.plots[3])
		self.zoomManager3 = ZoomManager(self.plots[0],self.plots[3])
		#self.zoomManager4 = ZoomManager(self.plots[1],self.plots[2])



		print "Populating Information"
		
		self.populateInfo()	

		self.MainPlotFrame.update()

		self.NEXT()
		###Test Stuff
	
		print "Interface Initialized Normally"

	def changeZoomState(self):
		
		if self.zoomState == 0: #Checks if zooming, if not, zooms

			self.zoomState = 1
		
			self.PlotFrameRight.pack(expand = 1, fill = Tk.BOTH, side = Tk.LEFT)
                	self.zoomButton.config(relief = Tk.SUNKEN)
                	self.zoomManager1.zoomOn()
			self.zoomManager2.zoomOn()
			self.zoomManager3.zoomOn()
			#self.zoomManager4.zoomOn()
		
		else: #If already zooming, unzooms

			self.zoomState = 0

	                self.PlotFrameRight.pack_forget()
        	        self.zoomButton.config(relief = Tk.RAISED)
			self.zoomManager1.zoomOff()
			self.zoomManager2.zoomOff()
			self.zoomManager3.zoomOff()
			#self.zoomManager4.zoomOff()

	def populateInfo(self):

		newInfo = self.Spectra.InformationReturn()

		self.Info.updateColumn(0,[newInfo[0]])
		self.Info.updateColumn(1,[newInfo[1]])
		self.Info.updateColumn(2,[newInfo[2]])
		self.Info.updateColumn(3,[newInfo[3]])
		self.Info.updateColumn(4,[newInfo[4]])
		self.Info.updateColumn(5,[newInfo[5]])


	def NEXT(self): #Goes to the next plot

		self.Spectra.NextData()
		self.UPDATE_PLOTS()

	def PREV(self): #Goes to the Previous Plot

		self.Spectra.PrevData()
		self.UPDATE_PLOTS()

	def UPDATE_PLOTS(self):

		print "Updating Plots"
		self.Spectra.PlotAllSpectra(S = 10)

		if len(self.Spectra.DataArray) < 3:
			self.Spectra.plotDifference(plot = 'sub', S = 10)

		else:
			self.Spectra.replotAllSpectra(plot = 'sub',S = 1)

		self.Info.Clear()
		self.populateInfo()

	def Jump1000(self):

		self.Spectra.iteration += 1000
		self.NEXT()


	def Jump100(self):

		self.Spectra.iteration += 100
		self.NEXT()

	def MARK_INTERESTING(self):
		self.Spectra.markInteresting()
		self.Spectra.ClearPlot()
		self.UPDATE_PLOTS()

	def UNMARK_INTERESTING(self):
		self.Spectra.unmarkInteresting()
		self.Spectra.ClearPlot()
		self.UPDATE_PLOTS()

		###End Test stuff

class PlottingWindow: #A class that creates a plotting window

	def __init__(self, master, size = [6,1]):

		self.frame = master #create the frame

		#Setting up the plot with matplotlib

		self.fig = figure(figsize = (size[0], size[1]), dpi = 80)
		self.fig.subplotpars.top = 0.95
		self.fig.subplotpars.bottom = 0.15
		self.fig.subplotpars.left = 0.12
		self.fig.subplotpars.right = 0.98

		self.ax = self.fig.add_subplot(111)
		self.canvas = FigureCanvasTkAgg(self.fig, master = self.frame)
		self.canvas.get_tk_widget().pack(fill = Tk.BOTH, expand = 1)
		self.canvas._tkcanvas.pack(fill = Tk.BOTH, expand = 1)
		#plt.tight_layout()

		#if size != [6,1]:

		#self.ax.set_xlim((3.578,3.966))
		#self.ax.set_ylim((-150,150))

		self.lines = [] #Allow for multiple lines

	def __call__(self, Xdata, Ydata, colors = colorcode): #Plots and given data
		line, = self.ax.plot(Xdata, Ydata, color = colors[len(self.lines)], lw = 0.5)	

		self.lines.append(line)

	def Hide(self, line):

		line.set_linestyle("None")

	def Show(self, line):

		line.set_linestyle('-')

	def Clear(self):

		for i in range(len(self.lines)):

			self.lines.remove(self.lines[-1])
			del(self.ax.lines[-1])

	def set_axes(self, pos = [0,0]): #Sets the postion, needs reworking

		ylim = self.ax.get_ylim()
		xlim = self.ax.get_xlim()
		
		self.ax.set_ylim(pos[1] - (ylim[1]-ylim[0])/2.0, pos[1] + (ylim[1] - ylim[0])/2.0)
		self.ax.set_xlim(pos[0] - (xlim[1]-xlim[0])/2.0, pos[0] + (xlim[1] - xlim[0])/2.0)

		self.fig.canvas.draw()

	def zoom(self, z = 0.0): #zoom in on plot, want to rewrite
		
		if z < 0.0:
	
			zy = 2.0**0.5
			zx = 2.0**0.5

		else:
			zy = 0.5**0.5
			zx = 1.0/2**0.5
	

		y = self.ax.get_ylim()
		x = self.ax.get_xlim()

		self.ax.set_ylim(y[0]+(1-zy)*(y[1]-y[0])/2.0, y[0] + (1+zy)*(y[1]-y[0])/2.0) 
		self.ax.set_xlim(x[0]+(1-zx)*(x[1]-x[0])/2.0,x[0] + (1+zx)*(x[1]-x[0])/2.0) 

		if y[1] - y[0] < 0.01 or x[1] - x[0] < 0.01:self.zoom(z = -1)

		elif y[1]-y[0] > 1000000 or x[1] - x[0] > 100000: self.zoom(z = 1)

		self.fig.canvas.draw()
	
class ZoomManager: #Manages the zoom function between a Main Plot and it's zoom

	def __init__(self, MainPlot, ZoomPlot):

		self.MainPlot = MainPlot
		self.ZoomPlot = ZoomPlot

	def scrollZoom(self, event): #Use scrollbar to zoom

		if event.inaxes != self.MainPlot.ax: return
		self.ZoomPlot.zoom(event.step)

	def setZoomPos(self,event): #Sets the position in the zoom plot

		if event.inaxes != self.MainPlot.ax or event.button != 1: return
		self.ZoomPlot.set_axes(pos = [event.xdata,event.ydata])	

	def zoomOn(self): #Connects the getMousePos function

		self.activeZoom = self.MainPlot.fig.canvas.mpl_connect('motion_notify_event', self.setZoomPos)

		self.ScrollZoom = self.MainPlot.fig.canvas.mpl_connect('scroll_event', self.scrollZoom)

	def zoomOff(self): #Disconnects said function

		self.MainPlot.fig.canvas.mpl_disconnect(self.activeZoom)

		self.MainPlot.fig.canvas.mpl_disconnect(self.ScrollZoom)

class LabelWindow:

	def __init__(self, master, height = 1):
		
		self.frame = master
		self.columns = []
		self.columnFrames = []
		self.height = height	

	def addColumn(self, title, rows, color = 'None', w = 0, Command = None, State = Tk.DISABLED):

		self.columnFrames.append(Tk.Frame(self.frame))
		self.columns.append([Tk.Button(self.columnFrames[-1], text = title, command = Command, relief = Tk.RIDGE, state = State, disabledforeground = '#000000', width = w),Tk.Listbox(self.columnFrames[-1], width = 1, height = self.height)])
		n = 0
		for item in rows:
			self.columns[-1][1].insert(Tk.END, str(item))
			if color != 'None':
				self.columns[-1][1].itemconfig(Tk.END, bg = color[n])	
			n += 1
		self.columnFrames[-1].pack(side = Tk.LEFT, expand = 1, fill = Tk.BOTH)
		self.columns[-1][0].pack(side = Tk.TOP, expand = 0, fill = Tk.X)
		self.columns[-1][1].pack(side = Tk.BOTTOM, expand = 1, fill = Tk.BOTH)
		#self.columnFrames[-1].bind("<Enter>", self.GetFrame)

	def updateColumn(self, position, rows, color = 'None'):
	
		n = 0
	
		for item in rows:

			self.columns[position][1].insert(Tk.END, str(item))

			if color != 'None':

				self.columns[position][1].itemconfig(Tk.END, bg = color[n])

			n += 1
		
	def set_focus(self):

		self.columnFrames[-1].focus_set()

	def Clear(self):

		for i in self.columns:
			i[1].delete(0,Tk.END)



	#	print 'set'

	
	#def ChangeSelection(self, columnNum):

		#self.columnFrames[columnNum].bind("Double-Button-1", )

	#def GetFrame(self,event):

		#print 'words', event.widget.lift(self.frame)

#root.bind("<Key>", GetFrame)
	

class PlotManager:

	def __init__(self, PlottingWindow, ZoomWindow, SubPlottingWindow, SubZoomWindow, Data):

		print "Initializing Plot Management"

		self.plotter = PlottingWindow
		self.zoomer = ZoomWindow

		self.subplotter = SubPlottingWindow
		self.subzoomer = SubZoomWindow

		self.iteration = 0

		print "Sorting and Clipping Data"

		TempData = [i for i in Data if i['REDSHIFT'] > 0]

		#self.Fulldata = sorted(TempData, key = lambda Group: Group[4])

		self.Fulldata = np.sort(TempData, order = 'REDSHIFT')

		self.data = self.Fulldata

		#print [i[4] for i in self.Fulldata if i[4] < 1]

		templateSpectra = self.data[self.iteration]

		self.currentData = self.data[self.data['GroupID'] == templateSpectra['GroupID']]
		self.DataArray = []

		print "Setting Up Data Information Frames"

		self.DataFrame = Tk.Toplevel()
                self.DataInfo = LabelWindow(self.DataFrame, height = 30)
		self.InterestingDataFlag = 0 #Determines which data we view

		#Initialize the ListBoxes

		self.DataInfo.addColumn('MJD',[''], w = 2)

                self.DataInfo.addColumn('PLATE',[''], w = 2)
                self.DataInfo.addColumn('FIBER',[''], w = 2)
                self.DataInfo.addColumn('',[''], w = 0)
                self.DataInfo.addColumn('',[''], w = 0, Command = self.ChangeAllMain, State = Tk.NORMAL)
		self.DataInfo.addColumn('',[''], w = 0, Command = self.ChangeAllSub, State = Tk.NORMAL)
                self.DataInfo.columns[-2][1].bind("<<ListboxSelect>>", self.ChangeSelectionPrimary)

		self.DataInfo.columns[-1][1].bind("<<ListboxSelect>>", self.ChangeSelectionSecondary)

		print "Plot Manager Initialized Normally"

	def PlotAllSpectra(self, plot = 'normal', S = 10):

		print "Current Plot:", plot

		dataFiles = self.currentData['FILENAME']
		self.DataArray = []

		if plot == 'normal':

			plotter = self.plotter
			zoomer = self.zoomer

		elif plot == 'sub':

			plotter = self.subplotter
			zoomer = self.subzoomer

		if len(dataFiles) <= 6:

			col = colorcode6

		else:

			col = colorcode

		#fileName[0].data['flux/LogLambda']
		MJD = []
		PLATE = []
		FIBER = []
		COLS = []
		for File in dataFiles:

			print File

			try:

				spSpec = fits.open('downloads/SDSS/' + File)
			
			except:
			
				spSpec = fits.open('downloads/BOSS/' + File)
			
			#
			#if spSpec[0].header['MJD'] < 56720:

			#	spSpec.close()
			#	continue	
			#

			self.DataArray.append([])
			self.DataArray[-1].append(10**np.array(spSpec[1].data['LogLambda'])[np.logical_and(10**np.array(spSpec[1].data['LogLambda']) > 3850, 10**np.array(spSpec[1].data['LogLambda']) < 9200)])
			self.DataArray[-1].append(self.Smooth(np.array(spSpec[1].data['flux'])[np.logical_and(10**np.array(spSpec[1].data['LogLambda']) > 3850, 10**np.array(spSpec[1].data['LogLambda']) < 9200)],S))
			spSpec.close()
			plotter(self.DataArray[-1][0], self.DataArray[-1][1], colors = col)
			zoomer(self.DataArray[-1][0], self.DataArray[-1][1],colors = col)
			COLS.append(self.plotter.lines[-1].get_color())
	

		plotter.ax.set_xlabel('Lambda')
		plotter.ax.set_ylabel('Flux')
		zoomer.ax.set_xlabel('Lambda')
		zoomer.ax.set_ylabel('Flux')

		self.DataInfo.updateColumn(0, self.currentData['MJD'].tolist())
		self.DataInfo.updateColumn(1, self.currentData['PLATEID'].tolist())
		self.DataInfo.updateColumn(2, self.currentData['FIBERID'].tolist())
		self.DataInfo.updateColumn(3, [' ' for i in range(len(COLS))], COLS)
		self.DataInfo.updateColumn(4, ['[O]' for i in range(len(COLS))])	
		
		#self.DataInfo.columns[-1][1].bind("<<ListboxSelect>>", self.ChangeSelection)

		print "LISTBOX:",self.DataInfo.columns[-1][1]

		plotter.ax.relim()
		zoomer.ax.relim()
		#self.plotter.ax.set_aspect('auto')
		plotter.ax.autoscale_view(True, True, True)
		zoomer.ax.set_ylim(plotter.ax.get_ylim())
		zoomer.ax.set_xlim(plotter.ax.get_xlim())
		zoomer.ax.autoscale_view(True, True, True)
		plotter.fig.canvas.draw()
		zoomer.fig.canvas.draw()

			
                #self.zoomer.ax.set_ylim((np.array(self.DataArray[-1][1]).min()-5,np.array(self.DataArray[-1][1]).max()+5))

	#The following is a test for differnt plat types from the data

	#This function allows you to replot the DataArray information for all spcetra.  It also allows you to slightly edit the plot, or plot it on a different window

	def replotAllSpectra(self, plot = 'normal', S = 1):

		print "Selected Plot:", plot

		if plot == 'normal':

			plotter = self.plotter
			zoomer = self.zoomer

		elif plot == 'sub':

			plotter = self.subplotter
			zoomer = self.subzoomer

		if len(self.DataArray) <= 6:

			col = colorcode6

		else:
		
			col = colorcode

		plotter.Clear()
		zoomer.Clear()

		for i in self.DataArray:

			Ydata = self.Smooth(i[1],S)

			Xdata = i[0]

			plotter(Xdata, Ydata, colors = col)
			zoomer(Xdata, Ydata, colors = col)

		self.DataInfo.updateColumn(5, ['[O]' for i in range(len(plotter.lines))])
	        plotter.ax.set_xlabel('Lambda')
        	plotter.ax.set_ylabel('Flux')
                zoomer.ax.set_xlabel('Lambda')
                zoomer.ax.set_ylabel('Flux')

		plotter.ax.relim()
                zoomer.ax.relim()
                plotter.ax.autoscale_view(True, True, True)
                zoomer.ax.autoscale_view(True, True, True)
                zoomer.ax.set_ylim(plotter.ax.get_ylim())
                zoomer.ax.set_xlim(plotter.ax.get_xlim())
                plotter.fig.canvas.draw()
                zoomer.fig.canvas.draw()
	
	def plotSpectraStd(self, plots = 'normal'): 

		if plots == 'sub':

			plotter = self.subplotter
			zoomer = self.subzoomer

		else:

			plotter = self.plotter
			zoomer = self.zoomer



		dataFiles = self.currentData['FILENAME']

		Xdata = self.DataArray[0][0]

		Ydata = [i[1] for i in self.DataArray]

		Ydata = np.std(Ydata, 0)

		Ydata = Ydata
                	
	        self.plotter(Xdata, Ydata)
	        self.zoomer(Xdata, Ydata)
        	self.plotter.ax.set_xlabel('Lambda')
                self.plotter.ax.set_ylabel('Standard Deviation Flux')
                self.zoomer.ax.set_xlabel('Lambda')
                self.zoomer.ax.set_ylabel('Standard Deviation Flux')

                self.plotter.ax.relim()
                self.zoomer.ax.relim()
                #self.plotter.ax.set_aspect('auto')
                #self.plotter.ax.set_xlim((3.578, 3.966))
                self.plotter.ax.autoscale_view(True, True, True)
                self.zoomer.ax.autoscale_view(True, True, True)
	 	
		self.plotter.fig.canvas.draw()
                self.zoomer.fig.canvas.draw()

	def plotDifference(self, plot = 'normal', S = 0):


		if plot == 'sub':

			plotter = self.subplotter
			zoomer = self.subzoomer

		else:

			plotter = self.plotter
			zoomer = self.zoomer

                if len(self.DataArray) <= 6:

                        col = colorcode6

                else:

                        col = colorcode

                plotter.Clear()
                zoomer.Clear()

		Ydata = self.Smooth(np.asarray(self.DataArray[0][1])/np.asarray(self.DataArray[1][1]),S)

		Ydata = [i if abs(i) < 10 else 0 for i in Ydata]
		Xdata = self.DataArray[0][0]

		plotter(Xdata,Ydata, colors = col)
		zoomer(Xdata,Ydata, colors = col)

                plotter.ax.set_xlabel('Lambda')
                plotter.ax.set_ylabel('Flux Ratio')
                zoomer.ax.set_xlabel('Lambda')
                zoomer.ax.set_ylabel('Flux Ratio')

		self.DataInfo.updateColumn(5, ['[O]' for i in range(len(plotter.lines))])

                plotter.ax.relim()
                plotter.ax.autoscale_view(True, True, True)
		zoomer.ax.set_ylim(plotter.ax.get_ylim())
		zoomer.ax.set_xlim(plotter.ax.get_xlim())
		zoomer.ax.relim()
                zoomer.ax.autoscale_view(True, True, True)
                plotter.fig.canvas.draw()
                zoomer.fig.canvas.draw()

	def ClearPlot(self):

		print "Clearing Plot"

		self.DataArray = []

		self.plotter.Clear()
		self.zoomer.Clear()
		self.subplotter.Clear()
		self.subzoomer.Clear()
		self.DataInfo.Clear()

		print "Plot Cleared"

	def NextData(self):

		print "Next Plot"

		if self.iteration < len(self.data) - 1:

			self.iteration += 1

		else:

			self.iteration = 1

		templateSpectra = self.data[self.iteration]

		self.currentData = self.data[self.data['GroupID'] == templateSpectra['GroupID']]

		print "Current Iteration Value:", self.iteration

		if len(self.currentData) < 2 or self.data[self.iteration]['GroupID'] == self.data[self.iteration - 1]['GroupID']:

			self.NextData()

		self.ClearPlot()

	def PrevData(self):

		print "Previous Plot"

		if self.iteration > 1:

			self.iteration -= 1

		else:

			self.iteration = len(self.data) - 1

		templateSpectra = self.data[self.iteration]
	
		self.currentData = self.data[self.data['GroupID'] == templateSpectra['GroupID']]

		print "Current Iteration Value:", self.iteration

		if len(self.currentData) < 2 or (self.iteration != len(self.data) - 1 and self.data[self.iteration]['GroupID'] == self.data[self.iteration+1]['GroupID']):

			self.PrevData()
		
		self.ClearPlot()

	def markInteresting(self):

		for i in self.data:

			if i in self.currentData:

				i['Interesting'] = 'Interesting'

		print "Marked as Interesting"
	
	def unmarkInteresting(self):

                for i in self.data:

                        if i in self.currentData:

                                i['Interesting'] = 'Not_Interesting'

		print "Removed Marked as Interesting"

	def saveInteresting(self):

		DataManager.saveInterestingObjects(self.data)

	def SwitchToInteresting(self):

		print "Switching Data Set"


		self.InterestingDataFlag = (self.InterestingDataFlag + 1) % 2


		if self.InterestingDataFlag:

			self.data = self.Fulldata[self.Fulldata['Interesting'] == 'Interesting']

			print "Set to Interesting"

		else:

			self.data = self.Fulldata

			print "Set to Full Data"


		if len(self.data) == 0:

			self.SwitchToInteresting()

			return 0


		if len(self.data) < self.iteration:

			self.iteration = 1

		self.currentData = self.data[self.iteration]

		self.NextData()

	def InformationReturn(self):

		print "Returning Current Data Information"

		#Spec = fits.open(self.currentData[1][-1])
	
		templateSpectra = self.data[self.iteration]

		Z = templateSpectra['REDSHIFT']

		RA = templateSpectra['RA']

		DEC = templateSpectra['DEC']

		Marked = templateSpectra['Interesting']

		Matches = len(self.currentData)

		ID = templateSpectra['GroupID']

		#Spec.close()

		Information = [Z,RA,DEC,Marked,Matches,ID]

		print Information
		
		return Information

	def Smooth(self, y, N):

		#print "Interpolating"

		return np.convolve(y, np.ones((N,))/N)[(N-1):]
		
	def ChangeSelectionPrimary(self, selection):

		print "Selection Changed:", self.DataInfo.columns[-2][1].curselection()[0]

		a =  self.DataInfo.columns[-2][1].curselection()[0]

		print "Location Selected:", a

		print self.plotter.lines[a].get_linestyle()

		if self.plotter.lines[a].get_linestyle() == '-':

			self.plotter.lines[a].set_linestyle('None')
			self.zoomer.lines[a].set_linestyle('None')
			self.DataInfo.columns[-2][1].delete(a)
			self.DataInfo.columns[-2][1].insert(a,'[X]')

		else:

			self.plotter.lines[a].set_linestyle('-')
			self.zoomer.lines[a].set_linestyle('-')
			self.DataInfo.columns[-2][1].delete(a)
			self.DataInfo.columns[-2][1].insert(a,'[O]')



		self.plotter.fig.canvas.draw()
		self.zoomer.fig.canvas.draw()

	def ChangeSelectionSecondary(self, selection):

                print "Selection Changed:", self.DataInfo.columns[-1][1].curselection()[0]

                a =  self.DataInfo.columns[-1][1].curselection()[0]

                print "Location Selected:", a

                print self.subplotter.lines[a].get_linestyle()

                if self.subplotter.lines[a].get_linestyle() == '-':

                        self.subplotter.lines[a].set_linestyle('None')
                        self.subzoomer.lines[a].set_linestyle('None')
                        self.DataInfo.columns[-1][1].delete(a)
                        self.DataInfo.columns[-1][1].insert(a,'[X]')

                else:

                        self.subplotter.lines[a].set_linestyle('-')
                        self.subzoomer.lines[a].set_linestyle('-')
                        self.DataInfo.columns[-1][1].delete(a)
                        self.DataInfo.columns[-1][1].insert(a,'[O]')



                self.subplotter.fig.canvas.draw()
                self.subzoomer.fig.canvas.draw()

	def ChangeAllMain(self):

		self.ChangeAllVisible(plots = 'normal')

	def ChangeAllSub(self):

		self.ChangeAllVisible(plots = 'sub')

	def ChangeAllVisible(self, plots = 'normal'):

		print "Changing Visible Lines"

		currentState = 0

		if plots == 'sub':

			plotter = self.subplotter
			zoomer = self.subzoomer
			pos = -1

		else:
	
			plotter = self.plotter
			zoomer = self.zoomer
			pos = -2

                for i in plotter.lines:

                        if i.get_linestyle() == '-':

                                currentState = 1
                                break

		if not currentState:

                	for i in range(len(self.plotter.lines)):

                        	plotter.lines[i].set_linestyle('-')
                        	zoomer.lines[i].set_linestyle('-')
                        	self.DataInfo.columns[pos][1].delete(i)
                        	self.DataInfo.columns[pos][1].insert(i,'[O]')
                        	plotter.fig.canvas.draw()
                        	zoomer.fig.canvas.draw()

		else:

                	for i in range(len(self.plotter.lines)):
	
	                        plotter.lines[i].set_linestyle('None')
	                        zoomer.lines[i].set_linestyle('None')
	                        self.DataInfo.columns[pos][1].delete(i)
	                        self.DataInfo.columns[pos][1].insert(i,'[X]')
				plotter.fig.canvas.draw()
				zoomer.fig.canvas.draw()

		print "Done"

	def Animate(self):

		print "Animating"

		for i in range(len(self.plotter.lines)):

			self.plotter.lines[i].set_linestyle('None')
			self.zoomer.lines[i].set_linestyle('None')
			self.DataInfo.columns[-1][1].delete(i)
			self.DataInfo.columns[-1][1].insert(i,'[X]')

		#self.plotter.fig.canvas.draw()
		#self.zoomer.fig.canvas.draw()

		for i in range(len(self.plotter.lines)):

			print " Plot:", i
			self.plotter.lines[i].set_linestyle('-')
			self.zoomer.lines[i].set_linestyle('-')
			self.DataInfo.columns[-1][1].delete(i)
			self.DataInfo.columns[-1][1].insert(i,'[O]')
			self.plotter.fig.canvas.draw()
			self.zoomer.fig.canvas.draw()
			time.sleep(0.05)
			self.plotter.lines[i].set_linestyle('None')
			self.zoomer.lines[i].set_linestyle('None')
			self.DataInfo.columns[-1][1].delete(i)
			self.DataInfo.columns[-1][1].insert(i,'[X]')

		print "Going Back To Normal"

                #for i in range(len(self.plotter.lines)):

                #        self.plotter.lines[i].set_linestyle('-')
                #        self.zoomer.lines[i].set_linestyle('-')
                #        self.DataInfo.columns[-1][1].delete(i)
                #        self.DataInfo.columns[-1][1].insert(i,'[O]')

		print "Back To Normal"	
	
		self.plotter.fig.canvas.draw()
		self.zoomer.fig.canvas.draw()


interface = Interface(Window)

Tk.mainloop()


