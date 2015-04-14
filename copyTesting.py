import numpy as np
from DataManager import getMatchesArray
from Config import PATH
from astropy.io import fits
import time
import sys

#TODO: Most methods haven't been checked for bugs.  

#Global Variables:

#PATH = "downloads/SDSS"
#PATH = '/media/rodot/257ed97b-65be-4cbe-85ff-39d657a241c1/home/rodot/SpectraFiles'


class List(object):

	def __init__(self, head=None):

		self._head = head
		self._end = self._head
		self._size = 0

	def pop(self, obj):

		if self._head == None: return

		elif obj == self._head.data():

			self._head = self._head.link()
			self._size -= 1

		elif obj == self._end.data():

			self.pop_back()

		else:

			ptr = self._head
			while ptr.link().data() != obj and ptr.link() != self._end:
				ptr = ptr.link()
				print ptr.link()

			if ptr.link() == self._end:
				print "No Objects Found"
				return

			ptr.setlink(ptr.link().link())	

			self._size -= 1


	def pop_back(self):

		if self._head == None: return

		elif self._head.link() == None:

			self._head = None
			self._end = self._head

		else:
			
			ptr = self._head
			while ptr.link() != self._end:
				ptr = ptr.link()
			self._end = ptr
			self._end.setlink(None)

		self._size -= 1

	def push_back(self, obj):

		if self._head == None:
	
			self._head = Node(obj)
			self._end = self._head

		else:

			ptr = self._end
			self._end = Node(obj)
			ptr.setlink(self._end)

		self._size += 1

	def insert(self, obj, pos):

		if pos >= self._size:

			print "Index Out of Range"
			return None

		elif pos == 0:

			ptr = self._head
			self._head = Node(obj)
			self._head.setlink(ptr)
			self._size += 1

		elif pos == self._size - 1:

			self.push_back(obj)

		else:

			ptr = self._head

			for i in xrange(self._size-1):

				ptr = ptr.link()

			objptr = Node(obj)
			objptr.setlink(ptr.link())
			ptr.setlink(objptr)
		
			self._size += 1				
		
	def __getitem__(self, index):

		ptr = self._head

		for i in xrange(index): ptr = ptr.link()

		return ptr.data()

	def __call__(self):

		if self._head == None:return

		ptr = self._head

		for i in xrange(self.size()):

			yield ptr.data()
			ptr = ptr.link()	

	def size(self):

		return self._size

	def sort(self):

		print "Sorting Not Currently Supported"

class Node(object):

	def __init__(self, data):

		self._data = data
		self._link = None

	def setlink(self, node):

		self._link = node

	def setdata(self, data):

		self._data = data

	def link(self):

		return self._link

	def data(self):

		return self._data

class Label(object):


	def __init__(self, ID):

		self.ID = ID
		self.members = List()

	def size(self):

		return self.members.size()

	def __len__(self):

		return self.size()

	def getMembers(self):

		return self.members()

	def addMember(self, obj):

		self.members.push_back(obj)

	def removeMember(self, obj):

		self.members.pop(obj)

	def __getitem__(self, index):

		return self.members[index]

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

		if tag not in self.getTags(): self.tags.addMember(tag)

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

	def __getitem__(self, index):

		return self.Data[index]

	def __call__(self):

		return self.Data

	def getSpectrum(self):

		f = len(self.Flux)
		l = len(self.Lambda)

		if f != l or f == 0 or l == 0:

			Data = fits.open("/".join((PATH, str(self['FILENAME']))))
			self.Flux = Data[1].data['flux']
			self.Lambda = 10**Data[1].data['loglam']
			Data.close()

		return [self.Flux, self.Lambda]

	def __repr__(self):

		return " ".join(("Spectrum Object <",str(self['MJD']),str(self['PLATEID']),str(self['FIBERID']),">"))

class Data(object):

	def __init__(self):

		print "Mapping To Spectrum"
		spectra = map(Spectrum, getMatchesArray())
		print "Done Mapping To Spectrum"
	
		self.groupList = dict(zip([i for i in xrange(spectra[-1].Data['GroupID']+1)],[Group(i) for i in xrange(spectra[-1].Data['GroupID']+1)]))

		self.tagList = dict(zip(['None'],[Tag("None", 0)]))

		self.currentData = np.array(self.groupList.keys())

		self.tagState = [("None",'u')]

		self.DataPosition = 0

		self.MIN_GROUP_SIZE = 2

		TAGNAMES = self.tagList.viewkeys()

		for i in xrange(len(spectra)):

			ID = spectra[i].Data['GroupID']
			Tags = set(spectra[i].Data['TAGS'].split())
			self.groupList[ID].addMember(spectra[i])

			for j in Tags:

				#if j not in TAGNAMES:

				#	newTag = Tag(j, len(self.tagList))
				#	self.tagList.setdefault(j,newTag)
	
				newTag = self.tagList.setdefault(j, Tag(j, len(self.tagList)))

				#else:

				#	newTag = self.tagList[j]

				self.groupList[ID].addTag(newTag)
				if j!= "None":
					if self.groupList[ID] not in newTag.getMembers():
						newTag.addMember(self.groupList[ID])
				#else:
					#newTag.addMember(self.groupList[ID])#TODO:BROKEN
		print "Getting Best Data For Each Group"
		for i in xrange(len(self.groupList)): self.groupList[i].bestData()
		self.sort()
		self.FullData = np.array([i for i in self.currentData if self.groupList[i].size() >= self.MIN_GROUP_SIZE])
		self.update()
		self.DataPosition = 0

	def update(self): #Update the data after change to Tagstate

		print self.tagState

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

					self.currentData = np.union1d(self.currentData,np.array([j() for j in self.tagList[i].getMembers() if j.size() >= self.MIN_GROUP_SIZE ]))
				elif k == 'i':

					self.currentData = np.intersect1d(self.currentData,np.array([j() for j in self.tagList[i].getMembers() if j.size() >= self.MIN_GROUP_SIZE ]))

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
			sys.exit(" ".join(("IndexError:","Tag State", str(self.tagState), "is invalid for MIN_GROUP_SIZE", str(self.MIN_GROUP_SIZE))))

	def size(self):

		return len(self.currentData)

	def sort(self):	

		T0 = time.clock()

		index = iter(np.argsort([self.groupList[i].Data['REDSHIFT'] for i in self.currentData]))

		self.currentData = np.array([self.currentData[i] for i in index])

		print "Sorting Time: ", time.clock() - T0

	def __getitem__(self, index):

		if type(index) is str or index in self.tagList.keys():

			return self.tagList[index]

		elif type(index) is int:
	
			return self.groupList[index]

		else: return self.groupList[index]


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

#T0 = time.clock()
#a = Data()
#print "Setup Time: ", time.clock() - T0
