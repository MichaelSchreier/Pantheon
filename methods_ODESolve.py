import array
import math
import numpy as np

def fGrav(pos1, pos2, mass1, mass2):
	return 6.674 * pow(10, -11) * mass1 * mass2 * (pos2 - pos1) / pow(np.linalg.norm(pos2-pos1), 3)


#first order leapfrog --------------------------------------------------
def leapfrog_first_order_kick(pos, vel, mass, dt):
	for i in range(len(pos)):
		for j in range(len(pos)):
			if i != j:
				vel[i] += fGrav(pos[i], pos[j], 1, mass[j]) * dt
	return vel


def leapfrog_first_order_drift(pos, vel, dt):
	for i in range(len(pos)):
		pos[i] += vel[i] * dt
	return pos


#Position Extended Forest-Ruth Like (PEFRL) method----------------------
def PEFRL(pos, vel, mass, dt):
	"""
	I.M. Omelyan, I.M. Mryglod and R. Folk, Computer Physics Communications 146, 188 (2002)
	
	Optimized Forest-Ruth- and Suzuki-like algorithms for integration of motion in 
	many-body systems, Omelyan et al., arXiv 0110585, https://arxiv.org/abs/cond-mat/0110585
	"""
	XI = 0.1786178958448091
	LAMBDA = -0.2123418310626054
	CHI = -0.06626458266981849
	
	
	#1------------------------------
	for i in range(len(pos)):
		pos[i] += XI * vel[i] * dt
	
	#2------------------------------
	for i in range(len(pos)):
		for j in range(len(pos)):
			if i != j:
				vel[i] += (1 - 2 * LAMBDA) * fGrav(pos[i], pos[j], 1, mass[j]) * dt / 2
			
	#3------------------------------
	for i in range(len(pos)):
		pos[i] += CHI * dt * vel[i]
		
	#4------------------------------
	for i in range(len(pos)):
		for j in range(len(pos)):
			if i != j:
				vel[i] += LAMBDA * dt * fGrav(pos[i], pos[j], 1, mass[j])
			
	#5------------------------------
	for i in range(len(pos)):
		pos[i] += (1 - 2 * (CHI + XI)) * dt * vel[i]
	
	#6(=4)---------------------------
	for i in range(len(pos)):
		for j in range(len(pos)):
			if i != j:
				vel[i] += LAMBDA * dt * fGrav(pos[i], pos[j], 1, mass[j])
			
	#7(=3)---------------------------
	for i in range(len(pos)):
		pos[i] += CHI * dt * vel[i]
		
	#8(=2)---------------------------
	for i in range(len(pos)):
		for j in range(len(pos)):
			if i != j:
				vel[i] += (1 - 2 * LAMBDA) * fGrav(pos[i], pos[j], 1, mass[j]) * dt / 2
			
	#9(=1)---------------------------
	for i in range(len(pos)):
		pos[i] += XI * vel[i] * dt
		
	return (pos, vel)