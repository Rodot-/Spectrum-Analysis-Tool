import numpy as np
from DataManager import getMatchesArray, groupData
import Config
from astropy.io import fits
import time
import sys, os
from multiprocessing import Process, Pipe, Queue, Array
import copy
import cPickle
fits.HDUList.__exit__ = fits.HDUList.close

#TODO: Most methods haven't been checked for bugs.  

#Global Variables:

class FileExporter(object):

	"""This class is used to export one of the data files 
	into to the desired format for future use.  Currently only
	two file formats are supported. (See formats) """

	formats = [
	'fits',
	'csv'
	]

	def __init__(self, data, **kwargs):

		default_format = 'csv'
		default_name = 'ExportedMatches'
		default_group = None
		default_tag = None

		self.data = data
		self.defaults = dict(format = default_format, name = default_name, tag = default_tag, group = default_group) 
		self.params = self.defaults.copy()
		self.params.update(kwargs)

	def save(self):

		print 'Saving...'

		if self.params['format'] == 'csv':

			self.export_csv(True)

		elif self.params['format'] == 'fits':

			self.export_fits()
		print 'Saved', self.params['name']


	def assert_params(self, revert_to_default = False):
		"""Make Sure that the params are valid
		if not, will revert to default values or 
		raise an exception depending on the arguments"""

		invalid = dict()
		
		#First, make sure the file format is valid
		invalid['format'] = self.params['format'] not in FileExporter.formats		
		#Check to See if we are overwriting
		#invalid['name'] = os.path.isfile(self.params['name'])

		#Check to make sure we are using a valid group or tag
		invalid['tag'] = self.params['tag'] not in self.data.tagList and self.params['tag'] is not None
		invalid['group'] = self.params['group'] not in self.data.groupList and self.params['group'] is not None
 		#Get The list of invalid keys
		invalid_keys = filter(invalid.get, invalid)

		if invalid_keys:	

			if revert_to_default:	
				for key in invalid_keys: 
					self.params[key] = self.defaults[key]
			else:
				raise Exception(",".join(invalid_keys))

	def prepare_data(self):

		self.assert_params(False)		
		headers = ['MJD', 'PLATEID', 'FIBERID', 'RA', 'DEC', 'REDSHIFT']
		formats = ['u2','u2','u2','f4','f4','f4']		
		IDS = []
		if self.params['group'] is not None:
			IDS.append(self.params['group'])	

		if self.params['tag'] is not None:
			IDS.extend([j() for j in self.data[self.params['tag']].getMembers()])	
		elif self.params['tag'] is self.params['group']:
			IDS = self.data.groupList.keys()

		spectra = (j for i in IDS for j in self.data[i].getMembers())

		return formats, headers, spectra		

	def export_csv(self, header = True):

		formats, headers, spectra = self.prepare_data()
		
		head = '#'+','.join(headers)+'\n' if header else ''

		with open(self.params['name'],'wb') as f:
			f.write(head)
			f.write('\n'.join([','.join(map(str,[spec[head] for head in headers])) for spec in spectra]))

	def export_fits(self):

		formats, headers, spectra = self.prepare_data()	
		columns = []
		M,P,F,RA,DEC,Z = zip(*[[spec[head] for head in headers] for spec in spectra])
		data = dict(zip(headers,(M,P,F,RA,DEC,Z)))
		for head, form in zip(headers, formats):
			form = form.replace('u2','J').replace('f4','E')	
			columns.append(fits.Column(name = head, format = form, array = np.asarray(data[head])))
		tbhdu = fits.BinTableHDU.from_columns(columns)  
		tbhdu.writeto(self.params['name'], clobber = True)


class Label(object):


	def __init__(self, ID):

		self.ID = ID
		self.members = []

	def size(self):

		return len(self.members)

	def __len__(self):

		return len(self.members)

	def getMembers(self):

		return (i for i in self.members)

	def addMember(self, obj):

		self.members.append(obj)

	def removeMember(self, obj):

		self.members.remove(obj)

	def __getitem__(self, index):

		return list(self.members)[index]

	def reduced(self):

		self.members = list(set(self.members))

class Group(Label):

	def __init__(self, GroupID):

		Label.__init__(self, GroupID)
		self.Data = dict(zip(['RA','DEC','REDSHIFT','GroupID'],[None, None, 0, self.ID]))
		self.tags = Label(GroupID)

	def __call__(self):

		return self.ID

	def __getitem__(self, index):

		return self.Data[index]

	def addTag(self, tag):

		self.tags.addMember(tag)

	def removeTag(self, tag):

		self.tags.removeMember(tag)

	def getTags(self):

		return self.tags.getMembers()

	def sortedReturn(self):

		result = []
		for i in self.getMembers():
			for j in result:
				if i.Data['MJD'] < j.Data['MJD']:
					result.insert(result.index(j),i)
					break
			else:
				result.append(i)
		for i in result: yield i

	def bestData(self):

		for i in self.getMembers():

			if self.Data['RA'] == None:
	
				self.Data['RA'] = i['RA']

			if self.Data['DEC'] == None:

				self.Data['DEC'] = i['DEC']
	
			if i['REDSHIFT'] <= 0:

				continue
	
			else:

				self.Data['REDSHIFT'] = i['REDSHIFT']

	def __repr__(self):

		return " ".join(["Group Object <"]+[str(i) for i in self.Data.values()]+["> with Size", str(self.size())])

class Tag(Label):

	def __init__(self, name, ID):

		Label.__init__(self, ID)
		self.name = name

	def __call__(self):
		
		return self.name

	def __repr__(self):

		return " ".join(("Tag Object <",str(self.name),str(self.ID),"> with Size", str(self.size())))


class Spectrum(object):

	def __init__(self, Data):

		self.Data = Data
		self.Flux = []
		self.Lambda = []
		self.Lines = []

	def __getitem__(self, index):

		return self.Data[index]

	def __call__(self):

		return self.Data

	def getSpectrum(self):

		self.loadSpectrum()

		return [self.Flux, self.Lambda]

	def ploadSpectrum(self): #Background Spectrum Loading
	
		if self.Flux != [] or self.Lambda != []: return	
		#p = Process(target = self.loadSpectrum, args = (QUEUE,))
		#p.start()
		#self.Flux, self.Lambda = QUEUE.get()
		#p.join()
		parent, child = Pipe()
		p = Process(target = self.loadSpectrum, args = (child,))
		p.daemon = True
		p.start()
		self.Flux, self.Lambda = parent.recv()
		p.join()

	def loadSpectrum(self, pipe = None):

		if self.Flux == [] or self.Lambda == []:
			with fits.open("/".join((Config.PATH,str(self['FILENAME'])))) as Data:
				self.Flux = Data[1].data['flux']
				self.Lambda = np.power(10,Data[1].data['loglam'])
				self.Lines = Data[3].data
			sys.stderr.write("Loaded A Spectrum of"+str(self))
		if pipe:
			pipe.send([self.Flux, self.Lambda])
			pipe.close()
			#pipe.put([self.Flux, self.Lambda])

	def __repr__(self):

		return " ".join(("Spectrum Object <",str(self['MJD']),str(self['PLATEID']),str(self['FIBERID']),">"))

class Data(object):

	def __init__(self):

		#State Variables

		self.tagState = [("None",'u')]

		#self.MIN_GROUP_SIZE = MIN_GROUP_SIZE

		T0 = time.clock()
		print "Setting Up"
	
		matches = getMatchesArray()
		groups = matches['GroupID']
		tags = matches['TAGS']
		#Make a list of all the possible unique tags
		tagSet = list(set([i for t in tags if t!= "None" for i in t.split()]))
		#Make a list of of all possible unique Groups
		groupSet = list(set(groups))
		#use sets to initialize dictionaries, prevents lookups
		self.groupList = dict(zip(groupSet, (Group(ID) for ID in groupSet)))
		self.tagList = dict(zip(tagSet, (Tag(t,0) for t in tagSet))) 

		#Setting Up groups and Tags
		for spectrum, ID, Tags in zip(matches, groups, tags): #Go through loaded Objects
			#if not ID % 127: #Loading Info
			#	print "                        \r",
			#	print "Loading Object", ID,
			currentGroup = self.groupList[ID]
			currentGroup.addMember(Spectrum(spectrum))
			if Tags != "None": #Adding Tags
				for tag in Tags.split():
					newTag = self.tagList[tag]
					newTag.addMember(self.groupList[ID])
					currentGroup.addTag(newTag)
		self.currentData = np.array(self.groupList.keys())
		print "\rMatching Time:", time.clock() - T0

		#Removing Duplicate Entries
		for i in self.groupList.values(): 
			i.tags.reduced()
			i.bestData()
		for i in self.tagList.values():
			i.reduced()

		#Sort the Data by Redshift
		self.sort()
		#Full data used for referencing everything contained in the Object.  Slightly more specific to user contraints
		self.FullData = np.array([i for i in self.currentData if self.groupList[i].size() >= Config.MIN_GROUP_SIZE])
		self.DataPosition = 0
		self.update()

	def update(self): #Update the data after change to Tagstate

		if self.size() != 0:

			temp = self.currentData[self.DataPosition]

		else:

			temp = 0

		self.currentData = np.array([])

		if ("None",'u') in self.tagState:

			self.currentData = self.FullData

		else:

			for i,k in self.tagState:

				if k == 'u':

					self.currentData = np.union1d(self.currentData,np.array([j() for j in self.tagList[i].getMembers() if j.size() >= Config.MIN_GROUP_SIZE ]))
				elif k == 'i':

					self.currentData = np.intersect1d(self.currentData,np.array([j() for j in self.tagList[i].getMembers() if j.size() >= Config.MIN_GROUP_SIZE ]))

			self.sort()

		if temp in self.currentData:

			self.DataPosition = np.where(self.currentData == temp)[0][0]
		
		elif self.DataPosition >= self.currentData.size:

			self.DataPosition = 0

		try:

			if len(self.currentData) == 0: raise IndexError(self.tagState)
		except IndexError as e:
			print "currentData is empty"
			print "Available Tags Are:"
			for i in self.tagList.values(): print "     ",i.name, "with size", len(i)
			#sys.exit(" ".join(("IndexError:","Tag State", str(self.tagState), "is invalid for MIN_GROUP_SIZE", str(self.MIN_GROUP_SIZE))))
			sys.stderr.write(" ".join(("IndexError:","Tag State", str(self.tagState), "is invalid for MIN_GROUP_SIZE", str(Config.MIN_GROUP_SIZE))))
			self.removeTagState(self.tagState[-1])
			self.update()
	

	def size(self):

		return len(self.currentData)

	def sort(self, field = 'REDSHIFT'):	

		T0 = time.clock()

		index = iter(np.argsort([self.groupList[i].Data[field] for i in self.currentData]))

		self.currentData = np.array([self.currentData[i] for i in index])

		print "Sorting Time: ", time.clock() - T0

	def __getitem__(self, index):

		if type(index) is list or type(index) is np.ndarray:

			result = copy.deepcopy(self)
			result.currentData = result.currentData[np.array(index)]		
			return result

		elif index in self.tagList:

			return self.tagList[index]

		elif index in self.groupList:
	
			return self.groupList[index]

		elif index in self().Data:

			return np.array([group[index] for group in self])
		else:
			print "Error: No Such index:",index

	def __iter__(self):

		return (self.groupList[i] for i in self.currentData)

	def __call__(self):

		return self.groupList[self.currentData[self.DataPosition]]

	def next(self):

		if self.currentData.size - self.DataPosition - 1: self.DataPosition += 1	
		else: self.DataPosition = 0

	def prev(self):

		if self.DataPosition: self.DataPosition -= 1
		else: self.DataPosition = self.currentData.size - 1

	def addTag(self, name): #Helper function for creating new Tags

		newTag = Tag(name, len(self.tagList))
		self.tagList.setdefault(name, newTag)
		return newTag

	def appendTag(self, name): #Appends a Tag to a Group

		if name not in self.tagList.keys(): newTag = self.addTag(name)
                else: newTag = self.tagList[name]
                newTag.addMember(self())
		self().addTag(newTag)

	def removeTag(self, name): #Removes a Tag from a group

		if name in self.getCurrentTagNames():
			while self() in self.tagList[name].getMembers():
				self.tagList[name].removeMember(self())
			self().removeTag(self.tagList[name])
	
	def getCurrentTags(self):

		return set(self().getTags())

	def getCurrentTagNames(self):

		return set([i.name for i in self.getCurrentTags()])

	def getTagState(self):

		return self.tagState

	def setTagState(self, *args):	

		self.tagState = list(args)
		
	def appendTagState(self, *args):

		if ("None",'u') in self.tagState: self.tagState.remove(("None",'u'))

		for i in args:

			self.tagState.append(i)

	def removeTagState(self, *args):

		self.tagState = list(set(self.tagState) - set(args))

		if len(self.tagState) == 0: self.appendTagState(("None",'u'))

	def search(self, subset = None, **params): #Search function.  Params are RA, DEC, MJD, PLATEID, FIBERID, REDSHIFT, GroupID.  Params may be tuples for multiple value searching.  Returns a list of indecies 
		T0 = time.clock() 	
	
		if subset is None:

			subset = self.FullData

		old_set = subset

		groupProps = ['RA','DEC','GroupID','REDSHIFT'] #List of group Properties
		specProps = ['FILENAME','MJD','PLATEID','FIBERID']

		group = dict([item for item in params.items() if item[0] in groupProps])
		
		spec = dict([item for item in params.items() if item[0] in specProps])

		subset = self.searchGroup(subset, **group)

		subset = self.searchSpectrum(subset, **spec)

		print "Search Single Time: ", time.clock() - T0

		if subset is old_set:

			return np.array([])

		return np.array(list(set(subset)))	
		
	def searchSpectrum(self, subset, **params):

		if not params:

			return subset

		result = []

		for item in params.items():

			for group in subset:

				for spectrum in self.groupList[group].getMembers():

					if spectrum[item[0]] == item[1]:

						result.append(group)

			subset = np.array(result)
			result = []

		return subset

	def searchGroup(self, subset, **params):

		if not params:

			return subset

		result = []
		error = 0

		for item in params.items():

			for group in subset:

				if type(item[1]) is tuple:

					error = item[1][1]
					obj = item[1][0]

				else:

					error = 0
					obj = item[1]

				if abs(self.groupList[group].Data[item[0]] - obj) <= error:

					result.append(group)

			subset = np.array(result)
			result = []

		return subset

if __name__ == '__main__':

	EX = FileExporter(Data(), format = 'fits', name = 'Group2', group = 2)
	EX.save()
	exit()

	data = Data()
	data.sort('RA')
	data.currentData = data.search(RA = (193.93, 8), DEC = (50.017,8), MJD = 52736, REDSHIFT = (0,3))
	#data.update()

	print "------------------------------------"
	for dat in data:
		print dat['GroupID'], dat['RA'], dat['DEC'], dat['REDSHIFT']
		for spec in dat.getMembers():
			print "|--",spec['MJD'], spec['PLATEID'], spec['FIBERID']
		print "------------------------------------"




#T0 = time.clock()
#a = Data()
#print "Setup Time: ", time.clock() - T0
