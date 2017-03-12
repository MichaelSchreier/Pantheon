#if __OPENCL_VERSION__ <= CL_VERSION_1_1
	#ifdef cl_khr_fp64
		#pragma OPENCL EXTENSION cl_khr_fp64 : enable
	#elif defined(cl_amd_fp64)
		#pragma OPENCL EXTENSION cl_amd_fp64 : enable
	#endif
#endif

__constant double xi = 0.1786178958448091;
__constant double lambda = -0.2123418310626054;
__constant double chi = -0.06626458266981849;

double norm( double4 r ) {
	return sqrt( r.x*r.x + r.y*r.y + r.z*r.z );
}

double4 Fg( double m1, double m2, double4 pos1, double4 pos2 ) {
	double4 dr;
	
	dr = pos2 - pos1;
	return dr * 6.673 * pow(10., -11) * m1 * m2 / pow(norm(dr), 3);
}

__kernel void PEFRL_1(
	__global double4 * npos,
	__global double4 * nvel,
	int length,
	float dt
) {
	int index = get_global_id(1);
	
	if(index < length) {
		npos[index] += xi * nvel[index] * dt;
	}
}

__kernel void PEFRL_2(
	__global double * mass,
	__global double4 * npos,
	__global double4 * nvel,
	int length,
	float dt
) {
	int index = get_global_id(1);
	int i;
	
	if(index < length) {
		for(i=0; i<length; i++) {
			if(i != index) {
				nvel[index] += (1.0 - 2.0 * lambda) * Fg(1.0, mass[i], npos[index], npos[i]) * dt / 2.0;
			}
		}
	}
}

__kernel void PEFRL_3(
	__global double4 * npos,
	__global double4 * nvel,
	int length,
	float dt
) {
	int index = get_global_id(1);
	
	if(index < length) {
		npos[index] += chi * nvel[index] * dt;
	}
}

__kernel void PEFRL_4(
	__global double * mass,
	__global double4 * npos,
	__global double4 * nvel,
	int length,
	float dt
) {
	int index = get_global_id(1);
	int i;
	
	if(index < length) {
		for(i=0; i<length; i++) {
			if(i != index) {
				nvel[index] += lambda * Fg(1.0, mass[i], npos[index], npos[i]) * dt;
			}
		}
	}
}

__kernel void PEFRL_5(
	__global double4 * npos,
	__global double4 * nvel,
	int length,
	float dt
) {
	int index = get_global_id(1);
	
	if(index < length) {
		npos[index] += (1.0 - 2.0 *(chi + xi)) * nvel[index] * dt;
	}
}