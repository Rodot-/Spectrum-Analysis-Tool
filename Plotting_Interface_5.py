from PlottingClasses import *
from astropy.coordinates import SkyCoord, Angle
from astropy.units import degree
from matplotlib.widgets import MultiCursor
from Config import bcolors
import Config
import copyTesting as DataClasses
import numpy as np
import time
import os
import sys
import Science
import DataTables
from DataTables import Transformations
import tkFont
import _console
from multiprocessing import Process, Pipe

try:
	import thread
except ImportError:
	import dummy_thread

if sys.version_info[0] < 3:
        import Tkinter as Tk
else:
        import tkinter as Tk


class PlottingInterface(Tk.Frame): #Example of a window application inside a frame
	"""
	This Main Plotting Interface.  \nManages graphics, data manipulation, and \nacts as the first abstraction layer\n for accessing the Data class.  \nThis class also handles save files \nand helps manage data loading.

	"""
	def __init__(self, master, Data):

		self.data = Data
		Tk.Frame.__init__(self, master)
		if len(sys.argv) > 1:

			try:

				print int(sys.argv[1])	
				self.data.DataPosition = list(self.data.currentData).index(int(sys.argv[1])) - 1
		
			except ValueError:

				with open(sys.argv[1], 'rb') as groupList:

					self.data.currentData = np.array(map(int, groupList.read().split()))
		#Frames

		self.Navigation = Tk.Frame(self)
		self.scroll_frame = Tk.Frame(self)
		##################
		self.Views = Tk.Toplevel()
		self.Views.title("Tag Views")
		self.Views.protocol("WM_DELETE_WINDOW", self.Views.withdraw)
		self.Views.withdraw()
		##################


		#self.Manipulation = Tk.Frame(self)
		self.Properties = Tk.Frame(self)
		self.PLOT = PlottingWindow(self)
		self.PLOT.AddSubplot()
		self.PLOT.AddSubplot(self.PLOT.ax[0], combineX = True)

		self.BasicInformation = DataTables.BasicDataDisplay(self.Properties, 4)
		self.BasicInformation.setTitles(['RA:','DEC:','Redshift:','Group ID:'], 10)

		#Buttons

		######## Mark Buttons

		SciSize = len(Science.TAGS)
		self.ViewWindowState = False

		self.ToggleSlineMark = DataTables.BasicCheckDisplay(self.Properties, SciSize)

		self.ToggleSlineView = DataTables.BasicCheckDisplay(self.Views, SciSize, Anch = Tk.CENTER)

		Skeys = Science.TAGS.keys()

		width = max((len(i) for i in Science.TAGS.keys()))
		self.ToggleSlineMark.setTitles(Skeys, width)
		self.ToggleSlineView.setTitles([i[0:-1] for i in Skeys], width)

		MarkCommands = []
		ViewCommands = []
		for i,j,k,l,m in zip(Skeys, self.ToggleSlineView.buttons, self.ToggleSlineView.buttonvars, self.ToggleSlineMark.buttons, self.ToggleSlineMark.buttonvars):
			MarkCommands.append(lambda x=i, y=l, z=m: self.toggleMark(x,y,z))
			ViewCommands.append(lambda x=i, y=j, z=k: self.toggleSline(x,y,z))
			

		self.ToggleSlineMark.setCommands(MarkCommands)

		self.ToggleSlineView.setCommands(ViewCommands)

		########

		self.NextButton = Tk.Button(self.Navigation, text = 'Next', command = self.NEXT)
		self.PreviousButton = Tk.Button(self.Navigation, text = 'Previous', command = self.PREV)

		#self.Toggle2D = Tk.Button(self.Manipulation, text = 'View Subtraction', command = self.toggle2d)

		#self.SaveSession = Tk.Button(self.Manipulation, text = 'Save', command = self.data.saveInterestingObjects)

		#Packing

		#self.Manipulation.pack(side = Tk.TOP, expand = 0, fill = Tk.X)
		self.scroll_frame.pack(side = Tk.RIGHT, expand = 0, fill = Tk.Y)
		self.Navigation.pack(side = Tk.BOTTOM, expand = 0, fill = Tk.X)
		self.Properties.pack(side = Tk.LEFT, expand = 0, fill = Tk.BOTH)
		#self.Views.pack(side = Tk.RIGHT, expand = 0, fill = Tk.BOTH)	
		self.PLOT.pack(expand = 1, fill = Tk.BOTH)
		self.BasicInformation.pack(side = Tk.TOP, expand = 0, fill = Tk.BOTH)
		self.ToggleSlineMark.pack(side = Tk.TOP, expand = 0, fill = Tk.BOTH)
		self.NextButton.pack(side = Tk.RIGHT, expand = 1, fill = Tk.X)
		self.PreviousButton.pack(side = Tk.RIGHT, fill = Tk.X, expand = 1)
		self.ToggleSlineView.pack(side = Tk.TOP, expand = 0, fill = Tk.BOTH)
		#self.Toggle2D.pack(side = Tk.RIGHT, expand = 1, fill = Tk.X)
		#self.SaveSession.pack(side = Tk.RIGHT, expand = 1, fill = Tk.X)

		#Plot Properties

		self.PLOT.ax[0].set_ylabel('Flux')
		self.PLOT.ax[1].set_ylabel('Flux')
		self.PLOT.ax[1].set_xlabel(r'$\lambda \/ (\AA)$')
		#self.PLOT.ax[0].set_xlabel(r'$\mathrm{\lambda \/ (\AA)}$')

		#Default Transformations

		self.Transform = []
		self.smoothing = Transformations.smooth_
		self.smoothingargs = {'N':10}
		self.normalize = None
		self.normargs = {}	
		self.Transform.append(Transformations.reflexive)
		self.Transform.append(Transformations.reflexive)
		self.annotations = dict()
		self.animVar = Tk.IntVar()

		self.UpdatePlots()		

		self.ToggleSlineMark.repack()
		self.ToggleSlineView.repack(self.ToggleSlineMark.data)
		#Cursor

                self.cursor = MultiCursor(self.PLOT.fig.canvas,(self.PLOT.ax[0], self.PLOT.ax[1]), color='#999999', linewidth=1.0 , useblit = True)
	
		self.backgroundTasks(0)

		#self.add_ticks()
		self.on_move_id = self.PLOT.fig.canvas.mpl_connect('motion_notify_event', self.on_move)
		self.on_resize_id = self.PLOT.fig.canvas.mpl_connect('draw_event', self.on_draw)
		self.annotate_ticks()

		self.anim_switch = Tk.Checkbutton(self.scroll_frame, text = '',variable = self.animVar, command = lambda x=self.animVar: self.animation_init() if x.get() else self.animation_end())
		self.scroller = Tk.Scrollbar(self.scroll_frame, command = self.scroll_animate)
		self.scroller.pack(side = Tk.BOTTOM, expand = 1, fill = Tk.Y)
		self.anim_switch.pack(expand = 0, fill = Tk.X, side = Tk.TOP)
		self.scroller.set(0, 1)
		self.bg2 = None
		####

	def animate(self):

		self.animation_init()
		line = self.PLOT.lines
		l0 = len(line[0])	
		l1 = len(line[1])	
		i = j = 0
		for k in xrange(100):
			i,j = l0*k/100-1, l1*k/100-1
			if i > 0:
				line[0][i-1].set_visible(False)
			if j > 0:
				line[1][j-1].set_visible(False)
			line[0][i].set_visible(True)
			line[0][i+1].set_visible(True)
			line[1][j].set_visible(True)
			if i != l0*(k-1)/100-1 or j != l1*(k-1)/100-1:
				self.PLOT.canvas.restore_region(self.bg2)
				self.PLOT.ax[0].draw_artist(line[0][i])
				self.PLOT.ax[0].draw_artist(line[0][i+1])
				self.PLOT.ax[1].draw_artist(line[1][j])
				self.PLOT.canvas.blit(self.PLOT.fig.bbox)
				self.cursor.background = self.PLOT.canvas.copy_from_bbox(self.PLOT.fig.bbox)
				time.sleep(0.02)
	
	def scroll_animate(self, *args):
		
		if not self.animVar.get(): #Disabled when not animating
			return 'break'	
		l0 = self.data().size()
		pos = float(args[1]) #Mouse position in scroll bar
		m = 1 - 1.0/(l0-1) #Scroll bar interval
		lo = pos if m > pos > 0 else 0.0 if pos < m else m
		result = int(lo/(m+0.001)*(l0-1))
		lo = result*1.0/(l0-1) #lower scroll position
		hi = lo + 1 - m #Higher scroll Position
		self.scroller.set(lo, hi) #Set scrollbar position
		self.animate_index(result) #Animate the resulting index	

	def animate_index(self, index):
	
		line = self.PLOT.lines #Lines we are working with
		if self.bg2 is None:self.animation_init()
		visibility_changed = False #To check if we need updates
		diff = self.Transform[0] != self.Transform[1]
		for i in xrange(self.data().size()): #Make everything invisible if it needs to be
			if i != index and i != index + 1:
				if line[0][i].get_visible():
					line[0][i].set_visible(False)
					visibility_changed = True
				if i <= self.data().size() - diff - 1:
					if line[1][i].get_visible():
						line[1][i].set_visible(False)
						visibility_changed = True
		if not line[0][index+1].get_visible() or not line[0][index].get_visible(): #check which lines need to become visible
			visibility_changed = True
			line[0][index].set_visible(True)
			line[0][index+1].set_visible(True)
			line[1][index].set_visible(True)
			if not diff:
				line[1][index+1].set_visible(True)
		if visibility_changed: #Draw and update the canvas
			self.PLOT.canvas.restore_region(self.bg2)
			self.PLOT.ax[0].draw_artist(line[0][index])
			self.PLOT.ax[0].draw_artist(line[0][index+1])
			self.PLOT.ax[1].draw_artist(line[1][index])	
			if not diff:
				self.PLOT.ax[1].draw_artist(line[1][index+1])	
			self.PLOT.canvas.blit(self.PLOT.fig.bbox)
			self.cursor.background = self.PLOT.canvas.copy_from_bbox(self.PLOT.fig.bbox)
			self.bg = None #Set the bg to default.  Prevents update troubles

	def animation_init(self):

		for ax in self.PLOT.ax: #Make all the lines invisible
			for line in ax.lines:
				line.set_visible(False)
		self.PLOT.canvas.draw() #Update the blank canvas to get a bg
		self.bg2 = self.PLOT.canvas.copy_from_bbox(self.PLOT.fig.bbox)
		#self.scroller.pack(side = Tk.BOTTOM, expand = 1, fill = Tk.X)
		self.scroller.config(bg = 'red')
		self.scroll_animate(0,0) #do the first animation

	def animation_end(self):

		visibility_changed = False
		for ax in self.PLOT.ax: #Make sure all lines are visible again
			for line in ax.lines:
				if not line.get_visible():
					visibility_changed = True
					line.set_visible(True)
		if visibility_changed:
			self.PLOT.canvas.draw() #Redraw everything if they are not
			self.cursor.background = self.PLOT.canvas.copy_from_bbox(self.PLOT.fig.bbox)
		self.bg = None #Set the bg back to default	
		self.scroller.set(0,1)
		self.scroller.config(bg = 'grey')
		#self.scroller.pack_forget() #get rid of the scroller

	def on_draw(self, event):
	
		self.bg = None #Used for the on_move event with axes resizing.
		self.bg2 = None #Used for animation axes recovery

	def on_move(self,event):#http://stackoverflow.com/questions/11537374/matplotlib-basemap-popup-box/11556140#11556140

		visibility_changed = False
		if not event.inaxes:return
		if self.bg is None:
			self.bg = self.cursor.background
		#Copies the cursors background for reference.
		annotations = self.annotations.values()
		for annotation in annotations:
			ex = event.x #X mouse position
			x, y = self.PLOT.ax[0].transData.transform(annotation.xy)
			#Transform Data to Figure coords
			should_be_visible = abs(x-ex) < 25 #Threshold
			if should_be_visible != annotation.get_visible():
				visibility_changed = True
				annotation.set_visible(should_be_visible)
				#Make annotations visible
		if visibility_changed:
			self.PLOT.fig.canvas.restore_region(self.bg)
			#Restore the background region
			for annotation in annotations: #Draw the annotations
				if annotation.get_visible():
					self.PLOT.ax[0].draw_artist(annotation)
			#draw the annotations and update the cursors background to prevent overwrites
			self.PLOT.canvas.blit(self.PLOT.fig.bbox)
			self.cursor.background = self.PLOT.canvas.copy_from_bbox(self.PLOT.fig.bbox)

	def annotate_ticks(self): #Create tick labels for hover

		scale = 1 + self.data()['REDSHIFT']
		specs = sorted([i for i in Science.TAGS.items() if i[1]], key = lambda x: x[1])
		lastx = 0
		trans = self.PLOT.ax[0].get_xaxis_transform()
		xs = self.PLOT.ax[0].get_xlim()
		for line in specs:
			wave = line[1] * scale
			k = 0.05 if wave-lastx < 500 else 0
			if line[0] not in self.annotations:
				if xs[0] < wave < xs[1]:
					Label = line[0].replace('\xce\xb1',r'\alpha',1).replace('\xce\xb2',r'\beta',1)
					Label = r"".join(('$',Label[:-1],'$'))
					self.annotations[line[0]] = self.PLOT.ax[0].annotate(Label, xy = (wave, -1.0), xytext = (wave, 1.05 + k), visible = False, arrowprops = dict(arrowstyle = '-', lw = 1.0), ha = 'center', fontsize = 10, xycoords = trans, animated = True)	
			else:
				self.annotations[line[0]].xy = (wave, -1.0)
				self.annotations[line[0]].xyann = (wave,1.05 + k)
			lastx = wave

	def to_SDSSName(self):

		ra, dec =  str(SkyCoord(ra = self.data()['RA']*degree, dec = self.data()['DEC']*degree, equinox = 'J2000').to_string('hmsdms')).translate(None, 'hmsd').split()
		ra = ra[0:9]
		dec = dec[0:10]
		return "".join(("SDSS J",ra,dec))
		 

	def showViews(self):

		self.Views.deiconify()

	def NEXT(self):

		self.data.next()
		self.UpdatePlots()		

	def PREV(self):

		self.data.prev()
		self.UpdatePlots()		

	def plotCurrent(self, ax_index, Transform = None, **kwargs):

		print "Plotting to axis",ax_index
		if Transform == None: 

			Transform = self.Transform[ax_index]

		Transform = Transformations.fsmooth(Transform, method = self.smoothing, **self.smoothingargs)

		if self.normalize is not None:

			Transform = Transformations.normalize(Transform, self.normalize, **self.normargs)

		self.PLOT.ClearPlot(ax_index)

		DR = Transform([i.getSpectrum() for i in self.data().sortedReturn()], **kwargs)

		for i in DR: self.PLOT.Plot(i[1], i[0], ax_index)

		self.PLOT.ax[ax_index].relim()
		self.PLOT.ax[ax_index].autoscale(enable = True)

	def toggleSline(self, tag, button, var, merge = 'u'):

		tag = str(tag)
		if tag not in self.data.tagList.keys():

			self.data.addTag(tag)
			button.deselect()
			return

		elif var.get():

			if len(self.data[tag]) == 0:

				button.deselect()
				return

			else:

				self.data.appendTagState((tag,merge))

		else:

			self.data.removeTagState((tag,merge))

		self.data.update()
		self.UpdatePlots()

	def backgroundTasks(self, n = 0):

		if n < len(self.data.currentData) and n < self.data.DataPosition + Config.FILES_AHEAD:
			for i in self.data[self.data.currentData[n]].getMembers(): 

				thread.start_new_thread(i.ploadSpectrum,())
				#i.ploadSpectrum()
			if self.data[self.data.currentData[n]].size() > 2:
				t = 200*self.data[self.data.currentData[n]].size()
			else:
				t = 100
			self.after(t,self.backgroundTasks, n+1)
		else:

			print bcolors.OKBLUE,"Auto",bcolors.ENDC,
			self.after(60000, self.backgroundTasks, self.data.DataPosition+1)
			thread.start_new_thread(self.saveData,('user/Autosave.csv',))


	def toggleMark(self, tag, button, var):

		if var.get():

			self.data.appendTag(tag)

		else:

			self.data.removeTag(tag) 	

		self.updateFields()	


	def UpdatePlots(self):

		self.updateFields()
		self.plotCurrent(0)
		if len(self.data()) < 2:
			T = Transformations.reflexive
		else:
			T = self.Transform[1]
		self.plotCurrent(1, T)
		self.PLOT.fig.suptitle(self.to_SDSSName())
		if self.animVar.get(): 
			self.animation_end()
			self.anim_switch.deselect()
		self.PLOT.update()
		self.annotate_ticks()
		self.bg = None
		print "Updated to",self.data()

	def updateFields(self):

		self.BasicInformation.setData([self.data().Data[i] for i in ['RA','DEC','REDSHIFT','GroupID']], 12)

		width = max((len(i) for i in Science.TAGS.keys()))
		self.ToggleSlineMark.setData(Science.RedShiftSlines(float(self.data().Data['REDSHIFT'])), width)

		tags = self.data.getCurrentTagNames()

		Marked = [(i in tags) for i in Science.TAGS.keys()]

		self.ToggleSlineMark.setStates(Marked)

	def toggleButtonRelief(self, Button, Bool):

		if Bool:

			Button['relief'] = Tk.SUNKEN

		else:

			Button['relief'] = Tk.RAISED

	def saveData(self, Filename = "user/InterestingMatches.csv"):

		fields = ['MJD','PLATEID','FIBERID','RA','DEC','REDSHIFT','FILENAME','Interesting']

		MarkedObjects = np.array([])

		for i in self.data.tagList.keys():

			if i != "None":

                                MarkedObjects = np.union1d(MarkedObjects,np.array([j() for j in self.data[i].getMembers()]))

		InterestingFile = open(Filename,'wb')
		InterestingFile.write('#MJD, PLATEID, FIBERID, RA, DEC, Z, FILENAME, ARGS, TAGS\n')


		for i in MarkedObjects:	

			for j in self.data[i].getMembers():

				InterestingFile.write(", ".join([str(j[k]) for k in fields]))

				InterestingFile.write(", ")

				InterestingFile.write(" ".join([k.name for k in self.data[i].getTags()]))
				InterestingFile.write('\n')

		InterestingFile.close()

		with open('resource/tags.conf','wb') as tagFile: 
			for i in Science.TAGS.items(): tagFile.write("".join((" ".join((str(i[0]),str(i[1]))),'\n')))

		print bcolors.OKGREEN, "Saved", bcolors.ENDC

class SearchTool(Tk.Toplevel):

	def __init__(self, master, data):

		Tk.Toplevel.__init__(self, master)
		self.title('Search Tool')
		self.data = data
		self.master = master

		self.search_params = dict(zip(['RA','DEC','MJD','PLATEID','FIBERID','GroupID','REDSHIFT'],[None]*8))

		self.spec = Tk.LabelFrame(self)
		self.coordinates = Tk.LabelFrame(self)
		self.misc = Tk.LabelFrame(self)

		self.MJD = DataTables.AutoEntry(self.spec, 'MJD (int)', int)
		self.PLATE = DataTables.AutoEntry(self.spec, 'PLATE (int)', int)
		self.FIBER = DataTables.AutoEntry(self.spec, 'FIBER (int)', int)
		self.RA = DataTables.AutoEntry(self.coordinates, 'RA (deg, h:m:s, h m s)', str)
		self.DEC = DataTables.AutoEntry(self.coordinates, 'DEC (deg, d:m:s, d m s)', str)
		self.GroupID = DataTables.AutoEntry(self.misc, 'Group ID (int)', int)
		self.Redshift = DataTables.AutoEntry(self.misc, 'Redshift (float)', float)
		self.accept = Tk.Button(self, text = 'Search', command = self.search)
		self.RA.pack(side = Tk.TOP, expand = 0, fill = Tk.X)
		self.DEC.pack(side = Tk.TOP, expand = 0, fill = Tk.X)
		self.MJD.pack(side = Tk.LEFT, expand = 0, fill = Tk.X)
		self.PLATE.pack(side = Tk.LEFT, expand = 0, fill = Tk.X)
		self.FIBER.pack(side = Tk.LEFT, expand = 0, fill = Tk.X)
		self.Redshift.pack(side = Tk.TOP, expand = 0, fill = Tk.X)	
		self.GroupID.pack(side = Tk.TOP, expand = 0, fill = Tk.X)	
	
		self.accept.pack(side = Tk.BOTTOM, expand = 0, fill = Tk.X)
		self.spec.pack(side = Tk.TOP, expand = 1, fill = Tk.BOTH)
		self.coordinates.pack(side = Tk.LEFT, expand = 1, fill = Tk.BOTH)
		self.misc.pack(side = Tk.RIGHT, expand = 1, fill = Tk.BOTH)

	def __call__(self):
	
		for i in (self.RA, self.DEC, self.MJD, self.FIBER, self.PLATE):
			i.replaceText()

	def search(self):

		self.search_params['RA'] = self.RA.getSelection()
		self.search_params['DEC'] = self.DEC.getSelection()
		self.search_params['MJD'] = self.MJD.getSelection()
		self.search_params['PLATEID'] = self.PLATE.getSelection()
		self.search_params['FIBERID'] = self.FIBER.getSelection()
		self.search_params['GroupID'] = self.GroupID.getSelection()
		self.search_params['REDSHIFT'] = self.Redshift.getSelection()
				

		search_dict = dict()
		for i in self.search_params.items():
			error = None
			if i[1] is not None:
				if i[0] == 'RA':
					term = self.parseRaDec(i[1], 'hms')
					s = str(term)
					error = 1.0/10**(len(s[s.find('.'):])-1)
				elif i[0] == 'DEC':
					term = self.parseRaDec(i[1], 'dms')
					s = str(term)
					error = 1.0/10**(len(s[s.find('.'):])-1)
				elif i[0] == 'REDSHIFT':
					term = i[1]		
					s = str(term)
					error = 1.0/10**(len(s[s.find('.'):])-1)
				else:
					term = i[1]
				if error is None:
					item = term
				else:
					item = (term, error)
				search_dict.setdefault(i[0],item)

		result = self.data.search(self.data.currentData, **search_dict)
		print search_dict
		print result
		if len(result) == 1:
			self.data.DataPosition = np.where(self.data.currentData == result[0])[0][0]
			self.master.MainWindow.UpdatePlots()
		elif len(result) > 1:
	
			print "Multiple Results Found:"
			for i in result:
				group = self.data[i]
				print '   RA:',group['RA'],"DEC:",group['DEC'] 
				for j in group.getMembers():
					print '      MJD:',j['MJD'],'PLATE:',j['PLATEID'],'FIBER:',j['FIBERID']
		else:

			print "No Results Found"


	def parseRaDec(self, coord, units): #Parses Ra, Dec input

		coord = coord.strip()
		if coord.count(' ') == 2 or coord.count(':') == 2:	
			separator = ' ' if coord.find(' ')+1 else ':'
			coord = "".join((coord, ' '))
			for i in units:
				coord = coord.replace(separator, i, 1)
			coord = float(Angle(coord).to_string('deg',decimal = True))
		else:
			coord = float(coord)
		return coord
	
class LoadingScreen(Tk.Toplevel):

	def __init__(self,conn = None, master = None):

		Tk.Toplevel.__init__(self)
		self.conn = conn
		self.master = master
		self.overrideredirect(True)
		self.filename = 'resource/spectra.gif'
		self.images = [Tk.PhotoImage(file = self.filename, format = "gif -index "+str(i)) for i in xrange(35)]
		self.wm_geometry("192x158-583+334")
		self.borderFrame = Tk.LabelFrame(self, borderwidth = 5)
		self.messageFrame = Tk.Frame(self.borderFrame, padx = 5, pady = 5)
		self.imageFrame = Tk.Frame(self.borderFrame)
		self.photo = Tk.Label(self.imageFrame, image = self.images[0])
		self.head = Tk.Label(self.messageFrame, text = 'Spectrum Analysis Tool')
		self.state = Tk.Label(self.messageFrame, text = 'Loading Spectra...')
		self.borderFrame.pack(fill = Tk.BOTH, expand = 1)
		self.imageFrame.pack(side = Tk.TOP, fill = Tk.BOTH, expand = 0)
		self.messageFrame.pack(side = Tk.BOTTOM, fill = Tk.BOTH, expand = 1)
		self.photo.pack(side = Tk.TOP, fill = Tk.BOTH, expand = 1)
		self.head.pack(side = Tk.TOP, fill = Tk.BOTH, expand = 1)
		self.state.pack(side = Tk.BOTTOM, fill = Tk.BOTH, expand = 1)

		self.update()
		self.after(100, self.cycle_image, 0)
		self.after(200, self.checkPipe)	


	def set_state(self, string):
		
		self.state['text'] = string
		self.update()
		
	def cycle_image(self, i):

		i = i % len(self.images)
		if self.state['text'] != 'Ready!':
			self.photo.configure(image = self.images[i])
			self.after(100,self.cycle_image,(i+1))

	def checkPipe(self):

		if not self.conn.poll():
			self.after(100, self.checkPipe)
		else:
			result = self.conn.recv()
			if result == 'withdraw':
				self.withdraw()
				self.after_idle(self.conn.close)
				self.after_idle(self.master.quit)
				self.after_idle(self.master.destroy)
			else: 
				self.set_state(result)	
				self.after(100, self.checkPipe)

def start_loader(conn):

	small_root = Tk.Tk()
	small_root.withdraw()
	loader = LoadingScreen(conn, small_root)
	small_root.mainloop()		

class App(Tk.Tk):

	def __init__(self):

		Tk.Tk.__init__(self)
		self.withdraw()
		self.title("Plotting Interface")
		self.geometry('1200x600-100+100')
		self.protocol("WM_DELETE_WINDOW",self.Quit)
		##########################################
		self.Info = None
		self.Mangler = None
		self.SearchBar = None
		self.menubar = Tk.Menu(self)
		self.views = Tk.Menu(self.menubar)
		self.new = Tk.Menu(self.menubar)
		self.tools = Tk.Menu(self.menubar)
		SpectraData = DataClasses.Data()
		OUT.send('Loading Interface...')
		self.MainWindow = PlottingInterface(self, SpectraData)
		OUT.send('Ready!')
		self.MainWindow.pack(expand = 1, fill = Tk.BOTH)

		self.new.add_command(label = "Tag", command = self.newTag)
		self.views.add_command(label="Tags", command=self.tagSelection)
		self.views.add_command(label="Info", command=self.viewObjectInfo)
		self.tools.add_command(label="Download", command = self.browseServer)
		self.tools.add_command(label="Override Redshift", command = self.changeZ)
		self.tools.add_command(label="Transform Data", command = self.mangle)
	
		self.tools.add_command(label="Run Matching", command = self.runMatching)
		self.tools.add_command(label="Reload Data", command = self.reloadData)
		self.tools.add_command(label="Search", command = self.searchTool)
		self.tools.add_command(label="Console", command = self.console)
	
		self.tools.add_command(label="Config", command = self.config_settings)
		self.menubar.add_cascade(label = "View", menu = self.views)
		self.menubar.add_cascade(label = "New", menu = self.new)
		self.menubar.add_cascade(label = "Tools", menu = self.tools)

		self.config(menu = self.menubar)
		OUT.send('withdraw')
		self.deiconify()

	def loadData(self, q):

		result = DataClasses.Data()	
		q.put(result, False)
		q.close()
		
	def config_settings(self):

		box = Tk.Toplevel()
		editor = DataTables.ConfigEditor(box, self.MainWindow.data, self.reloadData)
		editor.pack(expand = 1, fill = Tk.BOTH)
		box.title('Configuration')
		box.update()

	def console(self): #Opens a python console 
		"""
		Hints: 
		|
		| interface
		|    The main GUI.  Higher level data manipulation and graphics.
		| 
		| data
		|    The data managing class.  Lower level data manipulation.
		|
		| hints
		|    This page.
		|
		| Science
		|    View and edit tags and spectral lines.
		|
		| app
		|    Highest level GUI.
		|
		| quit
		|    Exit normally.
		|
		| exit
		|    Exit without saving.  
		|
		"""

		box = Tk.Toplevel()
		var = self.MainWindow.__dict__.copy()
		var.update(globals())
		var.update({'interface':self.MainWindow})
		var.update({'hints':(lambda *args:help(self.console))})
		#var.update(locals())
		var.update({'quit':self.Quit})
		console = _console.console(box, var)
		console.write(' Type "hints()" for hints.\n\n')
		console.write(console.ps(console.incomplete))
		console.pack(expand = 1, fill = Tk.BOTH)
		box.update()

	def searchTool(self):

		if self.SearchBar is None:

			self.SearchBar = SearchTool(self, self.MainWindow.data)
			self.SearchBar.protocol("WM_DELETE_WINDOW", self.SearchBar.withdraw)
		else:
			self.SearchBar.deiconify()
		self.SearchBar()
		self.SearchBar.update()

	def reloadData(self):

		msgBox = Tk.Toplevel()
		msg = Tk.Label(msgBox, text = "Reloading Data...\n\nThis Will Take a Few Seconds.")
		msg.pack()
		msgBox.update()
		self.MainWindow.data = DataClasses.Data()
		self.MainWindow.data.DataPosition = 0
		self.MainWindow.UpdatePlots()
		msg['text'] = "Done Loading"
		msgBox.update()

	def runMatching(self):

		msgBox = Tk.Toplevel()
		msg = Tk.Label(msgBox, text = "Matching Data in Background\n\nRestart or Reload Required\n\nFor Changes To Take Effect")
		msg.pack()
		thread.start_new_thread(DataClasses.groupData,())
		msgBox.update()

	def mangle(self):

		if self.Mangler == None:
			self.Mangler = DataTables.DataMangler(self, Science.TAGS)
			self.Mangler.protocol("WM_DELETE_WINDOW", self.Mangler.withdraw)
		else:
			self.Mangler.deiconify()
		self.Mangler.update()

	def changeZ(self):

		window = Tk.Toplevel(self)
		window.title("Change Redshift")
		frame = DataTables.OverrideData(window, self.MainWindow.data)
		frame.pack()
		try:
			self.wait_window(frame.entry)
			self.MainWindow.data.update()
			self.MainWindow.updateFields()
		except Tk.TclError:
			print "Weird Bug Encountered"		


	def browseServer(self):

		window = Tk.Toplevel(self)
		window.title("Spectrum Search")
		browser = DataTables.ServerBrowser(window)
		browser.pack(expand = 1, fill = Tk.BOTH)

	def viewObjectInfo(self):

		if self.Info == None:
			self.Info = DataTables.AdvancedDataDisplay("Information", self.MainWindow.data)
			self.Info.protocol("WM_DELETE_WINDOW", self.Info.withdraw)
		self.Info.update()

	def newTag(self):

		Dbox = Tk.Toplevel()
		DboxFrame = Tk.Frame(Dbox)
		Name = Tk.Entry(DboxFrame)
		Value = Tk.Entry(DboxFrame)

		def ReplaceText(EntryAndText):

			if EntryAndText[0].get() == "" and not EntryAndText[0].selection_present(): EntryAndText[0].insert(0, EntryAndText[1])
			#DboxFrame.after(100,ReplaceText,EntryAndText) 	

		def StopReplacing(EntryAndText):
			global ReplaceText
			if EntryAndText[0] == None: return
			if EntryAndText[0].get() == EntryAndText[1]:
				EntryAndText[0].delete(0,Tk.END)
			if EntryAndText[0] == Name and Value.get() == "":
				Value.insert(0, "Value (Float)")
			elif EntryAndText[0] == Value and Name.get() == "":
				Name.insert(0, "Name (String)")
			elif Name.get() and EntryAndText[0] != Name == "":
				Name.insert(0, "Name (String)")
			elif Value.get() == "" and EntryAndText[0] != Value:
				Value.insert(0, "Value (Float)")

		Name.bind('<Button-1>',lambda event: StopReplacing([Name, "Name (String)"])) 
		Value.bind('<Button-1>',lambda event: StopReplacing([Value, "Value (Float)"])) 

		ReplaceText([Name, "Name (String)"])
		ReplaceText([Value, "Value (Float)"])

		def getSelection():

			name = Name.get()
			value = Value.get()
			try:
				if value == "Value (Float)": value = 0
				if name.find(" ")+1: name = "_".join(name.split())
				value = float(value)
				name = "".join((name,":"))
				Science.TAGS.setdefault(name, value)
				self.MainWindow.ToggleSlineMark.newCheck()
				self.MainWindow.ToggleSlineView.newCheck()
				width = max((len(i) for i in Science.TAGS.keys()))
				self.MainWindow.ToggleSlineMark.setTitles(Science.TAGS.keys(), width)
				self.MainWindow.ToggleSlineView.setTitles([i[0:-1] for i in Science.TAGS.keys()], width)
				self.MainWindow.ToggleSlineMark.setCommands([lambda x=i,y=j,z=k: self.MainWindow.toggleMark(x,y,z) for i,j,k in zip(Science.TAGS.keys(), self.MainWindow.ToggleSlineMark.buttons, self.MainWindow.ToggleSlineMark.buttonvars)])	
				self.MainWindow.ToggleSlineView.setCommands([lambda x=i,y=j,z=k: self.MainWindow.toggleSline(x,y,z) for i,j,k in zip(Science.TAGS.keys(), self.MainWindow.ToggleSlineView.buttons, self.MainWindow.ToggleSlineView.buttonvars)])	
				self.MainWindow.data.appendTag(name)
				Dbox.withdraw()
				self.MainWindow.updateFields()
				self.MainWindow.ToggleSlineMark.repack()
				self.MainWindow.ToggleSlineView.repack(self.MainWindow.ToggleSlineMark.data)
	
			except ValueError:
				ErrorMsg = Tk.Toplevel()
				label = Tk.Label(ErrorMsg, text = "Invalid Value")
				label.pack()

		GO = Tk.Button(DboxFrame,text = 'Create Tag', command = getSelection)
		GO.pack(side = Tk.BOTTOM, expand = 0, fill = Tk.BOTH)
		Name.pack(side = Tk.LEFT, expand = 0, fill = Tk.BOTH)
		Value.pack(side = Tk.RIGHT, expand = 0, fill = Tk.BOTH)
		DboxFrame.pack()	
		GO.bind('<Button-1>',lambda event: StopReplacing([None,None])) 
		
	def tagSelection(self):

		self.MainWindow.showViews()

	def Quit(self):

		self.MainWindow.saveData()
		self.update_idletasks()
		self.after_idle(self.quit)
		self.after_idle(self.destroy)

if __name__ == '__main__':

	IN, OUT = Pipe(False)
	P = Process(target = start_loader, args = (IN,))
	P.start()
	app = App()
	P.join()
	app.mainloop()

