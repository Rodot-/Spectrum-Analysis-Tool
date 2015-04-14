import numpy as np

#conf = np.loadtxt('resource/SAT.conf', dtype = {"names":('PATH'), "formats":("<S256")})

PATH = open('resource/SAT.conf', 'rb').read()

PATH = PATH.split()[2]

#PATH = conf['PATH'][0]
