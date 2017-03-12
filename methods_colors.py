import numpy as np
from scipy.interpolate import interp1d

def givecolor(n, nmax):
	"""
	Given n, this method returns the interpolated red, green, and blue (RGB) values from 
	colorbrewer2's 'spectral' colorscheme corresponding to the fraction n / nmax of the 
	range from "red" end to the "blue" end of the scale.
	"""
	x = np.linspace(0, nmax, 11)
	yr = np.array([158, 213, 244, 253, 254, 255, 230, 171, 102, 50, 94])
	yg = np.array([1, 62, 109, 174, 224, 255, 245, 221, 194, 136, 79])
	yb = np.array([66, 79, 67, 97, 139, 191, 152, 164, 165, 189, 162])
	
	fr = interp1d(x, yr)
	fg = interp1d(x, yg)
	fb = interp1d(x, yb)
	
	return [int(fr(n)), int(fg(n)), int(fb(n))]
