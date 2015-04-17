#This code contains a class that is meant to mimic the ftplib.FTP class, but for URLs 

import urllib
import re

class URL:

	def __init__(self, address): #initialize with an address

		self.address = address
		self.parse_re = re.compile('href="([^"]*)".*(..-...-.... ..:..).*?(\d+[^\s<]*|-)') #Parses HTML for directories and files by searching for a Name, size, and time


	def cwd(self, path): #Change Directory

		if path.rfind('.') != -1 and path != '..':

			raise IOError("Not a Directory")

		elif self.address.rfind('.') < len(self.address) - 7 and path != '..':
		
			if not self.address.endswith('/'):

				self.address += '/'


			self.address += path

		elif self.address.rfind('/') > self.address.rfind('spectro') + 7:

			self.address = self.address[0:self.address.rfind('/')]
			self.address = self.address[0:self.address.rfind('/')]

		else:
		
			raise IOError("Not a Directory")

		html = urllib.urlopen(self.address)

	def dir(self): #print directory contents

		try:
			html = urllib.urlopen(self.address).read()
		except IOError, e:
			print 'error fetching %s: %s' % (self.address, e)
			return
		if not self.address.endswith('/'):
			self.address += '/'
		files = self.parse_re.findall(html)
		dirs = []
		print self.address + ' :'
		print '%4d file' % len(files) + 's' * (len(files) != 1)
		for name, date, size in files:
			if size.strip() == '-':
				size = 'dir'
			if name.endswith('/'):
				dirs += [name]
			print '%5s  %s  %s' % (size, date, name)

	def nlst(self):	#List directory contents as an array
	
		nlst = []

                try:
                        html = urllib.urlopen(self.address).read()
                except IOError, e:
                        print 'error fetching %s: %s' % (self.address, e)
                        return
                if not self.address.endswith('/'):
                        self.address += '/'
                files = self.parse_re.findall(html)
                dirs = []
                for name, date, size in files:
                        nlst.append(str(name))

		return nlst	

