#A library for transforming data
import numpy as np
import time
from scipy.signal import savgol_filter

def smoothSavgol(Data, window_length = 11, order=2):

	y = savgol_filter(Data[0], window_length, order)
	for i in xrange(3):  #http://pubs.acs.org/doi/pdf/10.1021/ac50064a018
		
		y = savgol_filter(y, window_length, order)
	
	return np.array([y, Data[1]])

def smooth_(Data, N):

	##########################
	# Smooths Data By Boxcar #
	# Method.  Takes in A    #
	# 2-D array, and the     #
	# number of points to    #
	# smooth over            #
	##########################
	return np.array([np.convolve(Data[0], np.ones((N,))/N, mode = 'same'), Data[1]])

def FootPrint_(Data):

	if len(Data) != 2:

		raise Exception("Only Sets of Two Spectra Can Use this Function")

	else:

		Indecies = [[],[]]

		Indecies[0] = np.in1d(Data[0][1], Data[1][1], assume_unique = True)

		Indecies[1] = np.in1d(Data[1][1], Data[0][1], assume_unique = True)


		fData = [[Data[0][0][Indecies[0]], Data[0][1][Indecies[0]]],[Data[1][0][Indecies[1]],Data[1][1][Indecies[1]]]]
	
		return fData

def runningTransform(Data, Transform, N = 10):

	result = []

	for i in xrange(len(Data)-1): result.append(Transform([Data[i],Data[i+1]], N)[0])

	return result

def subtract(Data, N = 10):

	T0 = time.time()

	if len(Data) > 2:

		return runningTransform(Data, subtract, N)

	FP = FootPrint_(Data)

	result = [np.array([np.subtract(FP[0][0], FP[1][0]), FP[0][1]])]

	result = smooth(result, N)
	
	print "Subtraction Time: ", time.time() - T0

	return result

def divide(Data, N = 10):

	T0 = time.time()

	if len(Data) > 2:

		return runningTransform(Data, divide, N)

	FP = FootPrint_(Data)
	
	result = np.array([np.true_divide(FP[0][0], FP[1][0]), FP[0][1]], dtype = np.float64)

	index = np.where(np.abs(result[0]) > 99)

	result[0][index] = 0

	result = smooth([result], N)

	print "Division Time: ", time.time() - T0

	return result

def smooth(Data, N = 10): #Vectorization of the smooth_ function.  Allows input of 3-D arrays
	T0 = time.time()

	if N == 0:

		return [i for i in Data]
	
	result = [smooth_(i, N) for i in Data]
	
	print "Smoothing Time: ", time.time() - T0

	return result

def normalize(Data, wavelength):

	result = []
	for i in Data:
        	Diff = np.absolute(i[1] - wavelength)
       		separation = min(Diff)
        	scale = 1.0/(i[0][np.where(Diff == separation)[0][0]])
        	result.append([i[0]*scale,i[1]])
	return result

'''
x = np.arange(100)*1.0
y = np.arange(100) * 2.0
x1 = np.arange(103)*1.0
y1 = np.arange(103)*2.0

data = [[x,y],[x1, y1**2]]

print subtract_(data)

'''
