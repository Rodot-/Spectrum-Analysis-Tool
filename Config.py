
class bcolors:

	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

options = dict()
with open('resource/SAT.conf', 'rb') as Config:

	for line in Config:
		if line[0] == '#': continue
		items = line.split()
		if len(items) == 3:
			options.setdefault(items[0], items[2])


PATH = options['PATH']
MIN_GROUP_SIZE = int(options['MIN_GROUP_SIZE'])
INFO_FIELDS = options['INFO_FIELDS'].split(',')
