import numpy as np

CIV = 1545.86
LyA = 1215.24
NV = 1239.42
MgII = 2800.32
Ha = 6564.61
Hb = 4863.68
OII = 3728.30
OIII = 4960.295

CHARS = {'alpha':"".join((chr(206),chr(177))), 'empty':chr(0),'beta':"".join((chr(206),chr(178)))}

Slines = np.array((CIV, LyA, NV, MgII, Ha, Hb, OII, OIII), dtype = {'names':['CIV:',"".join(('Ly-',CHARS['alpha'],':')),'NV:','MgII:',"".join(('H',CHARS['alpha'],':')),"".join(('H',CHARS['beta'],':')),'OII:','OIII:'], 'formats':['<f8' for i in xrange(8)]})

Slines_Values = np.array([Slines[i] for i in Slines.dtype.names])


def RedShiftSlines(z): #Returns Spectral lines with redshift corrections
	
	return (Slines_Values * (1 + z)).astype(int)


