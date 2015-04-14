import numpy as np

TAGS = dict(np.loadtxt('resource/tags.conf', delimiter = ' ', dtype = [('keys','<S8'),('values','<f4')]))

def RedShiftSlines(z): #Returns Spectral lines with redshift corrections
	
	return (np.array(TAGS.values()) * (1 + z)).astype(int)


