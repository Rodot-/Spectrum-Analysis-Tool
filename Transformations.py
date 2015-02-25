#A library for transforming data
import numpy as np
import time

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

def subtract(Data, N = 10):

	T0 = time.time()

	FP = FootPrint_(Data)

	result = [np.array([np.subtract(FP[0][0], FP[1][0]), FP[0][1]])]

	result = smooth(result, N)
	
	print "Subtraction Time: ", time.time() - T0

	return result

def divide(Data, N = 10):

	T0 = time.time()

	FP = FootPrint_(Data)
	
	result = np.array([np.true_divide(FP[0][0], FP[1][0]), FP[0][1]], dtype = np.float64)

	index = np.where(np.abs(result[0]) > 99)

	result[0][index] = 0

	result = smooth([result], N)

	print "Division Time: ", time.time() - T0

	return result

def smooth(Data, N = 10): #Vectorization of the smooth_ function.  Allows input of 3-D arrays
	T0 = time.time()
	
	result = [smooth_(i, N) for i in Data]
	
	print "Smoothing Time: ", time.time() - T0

	return result

'''
x = np.arange(100)*1.0
y = np.arange(100) * 2.0
x1 = np.arange(103)*1.0
y1 = np.arange(103)*2.0

data = [[x,y],[x1, y1**2]]

print subtract_(data)

'''
