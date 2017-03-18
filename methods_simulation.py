import methods_ODESolve as ode
import methods_AstronomicalObject as ao
import numpy as np
import pyopencl as cl
from pyopencl import array
import os

import time

os.environ['PYOPENCL_COMPILER_OUTPUT'] = '1'

def threadedSimulation(
	time_delta, 
	time_steps, 
	objects, 
	queue_data, 
	queue_comm, 
	skip_n, 
	openCL = False,
	method = "first order leapfrog"
):
	"""
	Transforms the input to numpy types if the simulation is run on the CPU or to OpenCL 
	types if OpenCL is being used.
	Then coditionally sets up an OpenCL environment and finally runs the siumlation.
	"""
	#transformation-----------------------------------------------------
	name = [""] * len(objects)
	mass = np.zeros(len(objects), dtype=np.float64)
	position_out = np.zeros((int(time_steps)//int(skip_n)+1, len(objects), 3), dtype=np.float64)
	
	if openCL == False:
		pos = np.zeros((len(objects), 3), dtype=np.float64)
		vel = np.zeros((len(objects), 3), dtype=np.float64)
	
		for elem in range(len(objects)):
			name[elem] = objects[elem].getName()
			mass[elem] = objects[elem].getMass()
			pos[elem] = np.array([ao.getAstrObjPos(objects[elem], objects)], dtype=np.float64)
			vel[elem] = np.array([ao.getAstrObjVel(objects[elem], objects)], dtype=np.float64)
			
		position_out[0] = np.array(pos, dtype=np.float64)
	
	else:
		pos = np.zeros((1, len(objects)), cl.array.vec.double4)
		vel = np.zeros((1, len(objects)), cl.array.vec.double4)
		force = np.zeros((1, len(objects)), cl.array.vec.double4)
		
		for elem in range(len(objects)):
			name[elem] = objects[elem].getName()
			mass[elem] = objects[elem].getMass()
			pos[0, elem] = tuple(ao.getAstrObjPos(objects[elem], objects))+ (0,)
			vel[0, elem] = tuple(ao.getAstrObjVel(objects[elem], objects))+ (0,)
			
		position_out[0] = np.array([list(pos[0][i])[0:3] for i in range(len(pos[0]))], dtype=np.float64)
	   
	#OpenCL initialization----------------------------------------------
	if openCL == True:
		platform = cl.get_platforms()[0]
		device = platform.get_devices()[0]
		context = cl.Context([device])
		clqueue = cl.CommandQueue(context)
		
		if method == "first order leapfrog":
			kernel = open("first_order_leapfrog.cl", 'r').read()
			program = cl.Program(context, kernel).build()
			program.kick.set_scalar_arg_dtypes([None, None, None, np.int32, np.float32])
			program.drift.set_scalar_arg_dtypes([None, None, np.int32, np.float32])
		elif method == "PEFRL":
			kernel = open("PEFRL.cl", 'r').read()
			program = cl.Program(context, kernel).build()
			program.PEFRL_1.set_scalar_arg_dtypes([None, None, np.int32, np.float32])
			program.PEFRL_2.set_scalar_arg_dtypes([None, None, None, np.int32, np.float32])
			program.PEFRL_3.set_scalar_arg_dtypes([None, None, np.int32, np.float32])
			program.PEFRL_4.set_scalar_arg_dtypes([None, None, None, np.int32, np.float32])
			program.PEFRL_5.set_scalar_arg_dtypes([None, None, np.int32, np.float32])
			
		mem_flags = cl.mem_flags
			
		buffer_position = cl.Buffer(context, mem_flags.READ_WRITE | mem_flags.COPY_HOST_PTR, hostbuf=pos)
		buffer_velocity = cl.Buffer(context, mem_flags.READ_WRITE | mem_flags.COPY_HOST_PTR, hostbuf=vel)
		buffer_mass = cl.Buffer(context, mem_flags.READ_ONLY | mem_flags.COPY_HOST_PTR, hostbuf=mass)

	#simulation----------------------------------------------------	
	if openCL == False:
		if method == "first order leapfrog":
			vel = ode.leapfrog_first_order_kick(pos, vel, mass, time_delta/2)#initial phase shift
		j = 1;
		for i in range(time_steps):
			if i % 10 == 0:
				if not queue_comm.empty():
					tmp = queue_comm.get()
					if tmp == "stop":
						break
					else:
						queue_comm.put(tmp)
			
			if method == "first order leapfrog":
				pos = ode.leapfrog_first_order_drift(pos, vel, time_delta)
				vel = ode.leapfrog_first_order_kick(pos, vel, mass, time_delta)
			elif method == "PEFRL":
				pos, vel = ode.PEFRL(pos, vel, mass, time_delta)
				
			#there should be a closed form covering both cases...
			if skip_n == 1:
				position_out[i+1] = np.array(pos, dtype=np.float64)
			elif (i+1) % skip_n == 0: 
				position_out[j] = np.array(pos, dtype=np.float64)
				j += 1
			if queue_comm.empty():
				queue_comm.put(i/time_steps*100)
	else:
		dim = np.int32(len(objects))
		time_delta_CL = np.float32(time_delta)
		
		#send kernels to GPU--------------------------------------------------------------
		if method == "first order leapfrog":
			kernel_kick_built = program.kick
			kernel_kick_built.set_args(
				buffer_mass, 
				buffer_position, 
				buffer_velocity,  
				dim, 
				np.float32(time_delta/2)
			)
			#inital phase offset
			cl.enqueue_nd_range_kernel(clqueue, kernel_kick_built, vel.shape, None)
			
			kernel_drift_built = program.drift
			kernel_drift_built.set_args(
				buffer_position,
				buffer_velocity,
				dim,
				time_delta_CL
			)
			
			kernel_kick_built.set_args(
				buffer_mass, 
				buffer_position, 
				buffer_velocity, 
				dim, 
				time_delta_CL
			)
		elif method == "PEFRL":
			kernel_PEFRL1_built = program.PEFRL_1
			kernel_PEFRL1_built.set_args(
				buffer_position,
				buffer_velocity,
				dim,
				time_delta_CL
			)
			
			kernel_PEFRL2_built = program.PEFRL_2
			kernel_PEFRL2_built.set_args(
				buffer_mass,
				buffer_position,
				buffer_velocity,
				dim,
				time_delta_CL
			)
			
			kernel_PEFRL3_built = program.PEFRL_3
			kernel_PEFRL3_built.set_args(
				buffer_position,
				buffer_velocity,
				dim,
				time_delta_CL
			)
			
			kernel_PEFRL4_built = program.PEFRL_4
			kernel_PEFRL4_built.set_args(
				buffer_mass,
				buffer_position,
				buffer_velocity,
				dim,
				time_delta_CL
			)
			
			kernel_PEFRL5_built = program.PEFRL_5
			kernel_PEFRL5_built.set_args(
				buffer_position,
				buffer_velocity,
				dim,
				time_delta_CL
			)
		
		#actual simulation loop-----------------------------------------------------------
		j = 1;
		for i in range(time_steps):
			if i % 10 == 0:
				if not queue_comm.empty():
					tmp = queue_comm.get()
					if tmp == "stop":
						break
					else:
						queue_comm.put(tmp)
			
			if method == "first order leapfrog":
				cl.enqueue_nd_range_kernel(clqueue, kernel_drift_built, vel.shape, None)
				cl.enqueue_nd_range_kernel(clqueue, kernel_kick_built, vel.shape, None)
			elif method == "PEFRL":
				cl.enqueue_nd_range_kernel(clqueue, kernel_PEFRL1_built, pos.shape, None)
				cl.enqueue_nd_range_kernel(clqueue, kernel_PEFRL2_built, vel.shape, None)
				cl.enqueue_nd_range_kernel(clqueue, kernel_PEFRL3_built, pos.shape, None)
				cl.enqueue_nd_range_kernel(clqueue, kernel_PEFRL4_built, vel.shape, None)
				cl.enqueue_nd_range_kernel(clqueue, kernel_PEFRL5_built, pos.shape, None)
				cl.enqueue_nd_range_kernel(clqueue, kernel_PEFRL4_built, vel.shape, None)
				cl.enqueue_nd_range_kernel(clqueue, kernel_PEFRL3_built, pos.shape, None)
				cl.enqueue_nd_range_kernel(clqueue, kernel_PEFRL2_built, vel.shape, None)
				cl.enqueue_nd_range_kernel(clqueue, kernel_PEFRL1_built, pos.shape, None)

			#prevents the queue from growing in some implementations of OpenCL
			if i % 100 == 0:
				clqueue.finish()
			
			if skip_n == 1:
				cl.enqueue_copy(clqueue, pos, buffer_position)
				position_out[i+1] = np.array([list(pos[0][k])[0:3] for k in range(len(pos[0]))], dtype=np.float64)
			elif (i+1) % skip_n == 0: 
				cl.enqueue_copy(clqueue, pos, buffer_position)
				position_out[j] = np.array([list(pos[0][k])[0:3] for k in range(len(pos[0]))], dtype=np.float64)
				j += 1
			if queue_comm.empty():
				queue_comm.put(i/time_steps*100)
	
	queue_data.put([name, [time_delta, skip_n], position_out])