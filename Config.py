"""
Program Configuration Manager. 
Get's configuration options 
from resource/SAT.conf.  
Configuration saving also available.
"""
def save(fileName): 
	"""
	Saves the config file to fileName
	"""
	with open(fileName,'wb') as config:
		config.write("\n".join((" = ".join(option) for option in options.items())))


class bcolors:
	"""
	Text colors in unix.  
	Used for displaying warning messages etc.
	"""

	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

#Loading the config file.  Always called when referenced
options = dict()
with open('resource/SAT.conf', 'rb') as Config:

	for line in Config:
		if line[0] != '#' and line.strip() != '':
			items = line.split('=',1)
			if len(items) == 2:
				options[items[0].strip()] = items[1].strip()
			else:
				print bcolors.WARNING, "Bad Configuration Parameter:", items, bcolors.ENDC




if __name__ == '__main__':

	for i in options.items():
		print i[0], i[1]
	save('resource/SAT_test.conf')

if __name__ == 'Config':

	PATH = options['PATH']
	MIN_GROUP_SIZE = int(options['MIN_GROUP_SIZE'])
	INFO_FIELDS = options['INFO_FIELDS'].split(',')
	FILES_AHEAD = int(options['FILES_AHEAD'])


