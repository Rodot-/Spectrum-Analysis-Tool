
options = dict()
with open('resource/SAT.conf', 'rb') as Config:

	for line in Config:
		items = line.split()
		if len(items) == 3:
			options.setdefault(items[0], items[2])


PATH = options['PATH']
MIN_GROUP_SIZE = int(options['MIN_GROUP_SIZE'])
