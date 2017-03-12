import numpy as np


def getAncestor(obj, objectlist):
    """
    returns a list with all ancestors of the astronomical object obj
    """
    primarylist = []
    if obj.getPrimaryName() != "no primary":
        for i in objectlist:
            if i.getName() == obj.getPrimaryName() and i.getName() not in primarylist:
                primarylist.append(i)
                if i.getPrimaryName() != "no primary":
                    primarylist.append(getAncestor(i, objectlist)[0])
          
    return(primarylist)
        
    
def getAstrObjPos(obj, objectlist):
    """
    returns x, y and z coordinate of an astronomical object
    corrected for the positions of its primaries
    """
    primarylist = getAncestor(obj, objectlist)
    x = obj.getX()
    y = obj.getY()
    z = obj.getZ()
    
    for i in primarylist:
        x += i.getX()
        y += i.getY()
        z += i.getZ()
        
    return [x, y, z]
 
 
def getAstrObjVel(obj, objectlist):
    """
    returns x, y and z coordinate of an astronomical object
    corrected for the positions of its primaries
    """
    vx = obj.getVx()
    vy = obj.getVy()
    vz = obj.getVz()
    
    primarylist = getAncestor(obj, objectlist)
    for i in primarylist:
        vx += i.getVx()
        vy += i.getVy()
        vz += i.getVz()
        
    return [vx, vy, vz]
    
    
def arbitraryRotate(coords, axis, angle):
	ax = axis / np.linalg.norm(axis)
	rmat = np.array([
		[ax[0]**2*(1-cos(angle)) + cos(angle), ax[0]*ax[1]*(1-cos(angle)) - ax[2]*sin(angle), ax[0]*ax[2]*(1-cos(angle)) + ax[1]*sin(angle)],
		[ax[1]*ax[0]*(1-cos(angle)) + ax[2]*sin(angle), ax[1]**2*(1-cos(angle)) + cos(angle), ax[1]*ax[2]*(1-cos(angle)) - ax[0]*sin(angle)],
		[ax[2]*ax[0]*(1-cos(angle)) - ax[1]*sin(angle), ax[2]*ax[1]*(1-cos(angle)) + ax[0]*sin(angle), ax[2]**2*(1-cos(angle)) + cos(angle)]], dtype=np.float64)
	
	return(np.dot(rmat, coords))
