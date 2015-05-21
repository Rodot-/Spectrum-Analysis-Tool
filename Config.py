
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
		if line[0] != '#' and line.strip() != '':
			items = line.split('=',1)
			if len(items) == 2:
				options[items[0].strip()] = items[1].strip()
			else:
				print bcolors.WARNING, "Bad Configuration Parameter:", items, bcolors.ENDC



PATH = options['PATH']
MIN_GROUP_SIZE = int(options['MIN_GROUP_SIZE'])
INFO_FIELDS = options['INFO_FIELDS'].split(',')
FILES_AHEAD = int(options['FILES_AHEAD'])

if __name__ == '__main__':

	for i in options.items():
		print i[0], i[1]

