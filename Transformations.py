#A library for transforming data
import numpy as np
import time
from scipy.signal import savgol_filter



def frunning(function):

	def wrapper(Data, *args, **kwargs):

		result = []

	        for i in xrange(len(Data)-1): result.append(function([Data[i],Data[i+1]], *args, **kwargs))

	        return result
	
	return wrapper

def reflexive(Data, *args):

	return Data

def smoothSavgol(Data, N = 11, order=2):

	y = savgol_filter(Data[0], N, order)
	for i in xrange(3):  #http://pubs.acs.org/doi/pdf/10.1021/ac50064a018
		
		y = savgol_filter(y, N, order)
	
	return np.array([y, Data[1]])

def smooth_(Data, N=10):

	##########################
	# Smooths Data By Boxcar #
	# Method.  Takes in A    #
	# 2-D array, and the     #
	# number of points to    #
	# smooth over            #
	##########################
	return np.array([np.convolve(Data[0], np.ones((N,))/N, mode = 'same'), Data[1]])

def normalize_int(Data, **kwargs):

	result = []
	for i in Data:
		result.append([i[0]/sum(i[0][np.logical_and(i[1]>4000.0, i[1]<9000.0)]), i[1]])
	return result

def normalize_wave(Data, wavelength = 6564.61):

	result = []
	for i in Data:
        	Diff = np.absolute(i[1] - wavelength)
       		separation = min(Diff)
		if separation > 1.0:
			return Data
        	scale = 1.0/(i[0][np.where(Diff == separation)[0][0]])
        	result.append([i[0]*scale,i[1]])
	return result


def FootPrint_(Data):

	if len(Data) != 2:

		raise Exception("Only Sets of Two Spectra Can Use this Function")

	else:

		Indecies = [[],[]]

		Indecies[0] = np.in1d(Data[0][1], Data[1][1], assume_unique = True)

		Indecies[1] = np.in1d(Data[1][1], Data[0][1], assume_unique = True)


		fData = [[Data[0][0][Indecies[0]], Data[0][1][Indecies[0]]],[Data[1][0][Indecies[1]],Data[1][1][Indecies[1]]]]
	
		return fData

@frunning
def subtract(Data):

	T0 = time.time()

	FP = FootPrint_(Data)

	result = np.array([np.subtract(FP[0][0], FP[1][0]), FP[0][1]])

	print "Subtraction Time: ", time.time() - T0

	return result

@frunning
def divide(Data):

	T0 = time.time()

	if len(Data) > 2:

		return runningTransform(Data, divide, N)

	FP = FootPrint_(Data)
	
	result = np.array([np.true_divide(FP[0][0], FP[1][0]), FP[0][1]], dtype = np.float64)

	index = np.where(np.abs(result[0]) > 99)

	result[0][index] = 0

	print "Division Time: ", time.time() - T0

	return result

def smooth(Data, method = smooth_, N = 0, **kwargs): #Vectorization of the smooth_ function.  Allows input of 3-D arrays
	T0 = time.time()

	if N == 0:

		return [i for i in Data]
	
	result = [method(i, **kwargs) for i in Data]
	
	print "Smoothing Time: ", time.time() - T0

	return result



def fsmooth(function, method = smooth_, **smoothargs):

	def wrapper(Data, **kwargs):

		fresults = function(Data, **kwargs)

		return [method(result, **smoothargs) for result in fresults]

	return wrapper

def normalize(f, method = normalize_int, **params):

	def wrap(Data, **kwargs):

		return f(method(Data, **params), **kwargs)

	return wrap

if __name__ == '__main__':


	x = np.arange(100)*1.0
	y = np.arange(100) * 2.0
	x1 = np.arange(103)*1.0
	y1 = np.arange(103)*2.0
	y2 = np.arange(105)*6.0
	x2 = np.arange(107)*1.0

	data = [[y,x],[y1**2, x1],[y2**3,x2]]

	transform = fsmooth(reflexive, method = smooth_, N = 10)
	transform = normalize(fsmooth(subtract, method = smooth_, N=10))

	a = transform(data)
	for i in a:
		print i


