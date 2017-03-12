class AstronomicalObject():

    def __init__(self, name="", mass=0, primaryname=None, x=0, y=0, z=0, vx=0, vy=0, vz=0):
        super(AstronomicalObject, self).__init__()
        self.initParameters(name, mass, primaryname, x, y, z, vx, vy, vz)
        
    def initParameters(self, name, mass, primaryname, x, y, z, vx, vy, vz):
        self._name = name
        self._mass = mass
        self._primaryname = primaryname
        
        self._x = x
        self._y = y
        self._z = z
        
        self._vx = vx
        self._vy = vy
        self._vz = vz
      
      
    def getName(self):
        return self._name
        
    def getMass(self):
        return self._mass
        
    def getPrimaryName(self):
        return self._primaryname
        
    def getX(self):
        return self._x
        
    def getY(self):
        return self._y
        
    def getZ(self):
        return self._z
        
    def getVx(self):
        return self._vx
        
    def getVy(self):
        return self._vy
        
    def getVz(self):
        return self._vz
        
        
    def setName(self, name):
        self._name = name
        
    def setMass(self, mass):
        self._mass = mass
        
    def setPrimaryName(self, primaryname):
        self._primaryname = primaryname
        
    def setX(self, x):
        self._x = x
        
    def setY(self, y):
        self._y = y
        
    def setZ(self, z):
        self._z = z
        
    def setVx(self, vx):
        self._vx = vx
        
    def setVy(self, vy):
        self._vy = vy
        
    def setVz(self, vz):
        self._vz = vz
