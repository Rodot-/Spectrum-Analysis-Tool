import numpy as np
from DataManager import getMatchesArray, groupData
from Config import PATH, MIN_GROUP_SIZE
from astropy.io import fits
import time
import sys

#TODO: Most methods haven't been checked for bugs.  

#Global Variables:


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

	def __getitem__(self, index):

		return self.Data[index]

	def __call__(self):

		return self.Data

	def getSpectrum(self):

		self.loadSpectrum()

		return [self.Flux, self.Lambda]

	def loadSpectrum(self):

		if len(self.Flux) == 0 or len(self.Lambda) == 0:
			Data = fits.open("/".join((PATH,str(self['FILENAME']))))
			self.Flux = Data[1].data['flux']
			self.Lambda = np.power(10,Data[1].data['loglam'])
			Data.close()

	def __repr__(self):

		return " ".join(("Spectrum Object <",str(self['MJD']),str(self['PLATEID']),str(self['FIBERID']),">"))

class Data(object):

	def __init__(self):

		#State Variables

		self.tagState = [("None",'u')]

		self.MIN_GROUP_SIZE = MIN_GROUP_SIZE

		T0 = time.clock()
		print "Setting Up"
		self.groupList = dict() #dict of groups
		self.tagList = dict() #dict of tags
		TAGNAMES = self.tagList.viewkeys()
		#Setting Up groups and Tags
		for spectrum in getMatchesArray(): #Go through loaded Objects
			ID = spectrum['GroupID']
			if not ID % 128: #Loading Info
				print "                        \r",
				print "Loading Object", ID,
			currentGroup = self.groupList.setdefault(ID, Group(ID))
			currentGroup.addMember(Spectrum(spectrum))
			for tag in spectrum['TAGS'].split(): #Adding Tags
				if tag != "None":
					newTag = self.tagList.setdefault(tag, Tag(tag, 0))
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
		self.FullData = np.array([i for i in self.currentData if self.groupList[i].size() >= self.MIN_GROUP_SIZE])
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

	def __iter__(self):

		return (self[i] for i in self.currentData)

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
