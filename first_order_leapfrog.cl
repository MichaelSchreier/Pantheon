#if __OPENCL_VERSION__ <= CL_VERSION_1_1
	#ifdef cl_khr_fp64
		#pragma OPENCL EXTENSION cl_khr_fp64 : enable
	#elif defined(cl_amd_fp64)
		#pragma OPENCL EXTENSION cl_amd_fp64 : enable
	#endif
#endif


double norm( double4 r ) {
	return sqrt( r.x*r.x + r.y*r.y + r.z*r.z );
}

double4 Fg( double m1, double m2, double4 pos1, double4 pos2 ) {
	double4 dr;
	
	dr = pos2 - pos1;
	return dr * 6.674 * pow(10., -11) * m1 * m2 / pow(norm(dr), 3);
}

__kernel void kick(
	__global double * mass,
	__global double4 * npos,
	__global double4 * nvel,
	int length,
	float dt
) {
	int index = get_global_id(1);
	int i;
	
	/* calculate v_n+1 */
	if(index < length) {
		for(i=0; i<length; i++) {
				if(i!=index) {
					nvel[index] += Fg(1.0, mass[i], npos[index], npos[i]) * dt;
				}
		};
	}
}

__kernel void drift(
	__global double4 * npos,
	__global double4 * nvel,
	int length,
	float dt
) {
	/* npos and nvel are 2D arrays */
    
	int index = get_global_id(1);
	
	/* calculate x_n+1 */
	if(index < length) {
		npos[index] += nvel[index]*dt;
	}
}