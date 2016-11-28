# Scannables for moving sample perpendicular and parallel to the beam
#
# Based on i16's gda/config/scripts/Sample_perpMotion.py @717f87f
#
# On I15, this was tested using the following assumptions
# * At the `zero` position, where sx=sperp and sy=spara, phi-phi_offset is 0 (58-58) and mu-mu_offset is 0 (0-0)
# * The sample x and y stages are on the phi axis, so rotate with it.
# * sx is +ve to the right (not the usual left) when looking along the beam at the `zero` position. 
# * sy is the sample stage, +ve is along the beam towards (as usual) from the detector at the `zero` position.
# * mu is static and always returns 0
# * phi is horizontal at with Kappa at -134.74 and theta @-34.05
#
#sperp and spara using rotation matrix method
#15/10/2012 implemented horizontal scattering mode (mu different from zero)

#sperp=PerpendicularSampleMotion("sperp", sx, sy, mu, phi,
#    help="To move sample stage perpendicular to the beam.")

#spara=ParallelSampleMotion("spara", sx, sy, mu, phi,
#    help="To move sample stage parallel to the beam.")

#I15:
#dperp=PerpendicularSampleMotion("dperp", dx, dy, dmu, dkphi, True, 0, 58,
#    help="To move sample stage perpendicular to the beam.")

#dpara=ParallelSampleMotion("dpara", dx, dy, dmu, dkphi, True, 0, 58,
#    help="To move sample stage parallel to the beam.")

from gda.device.scannable import PseudoDevice
from math import pi, sin, cos

class PerpendicularSampleMotion(PseudoDevice):
    '''Device to move sample stage perpendicular to the beam when phi or mu are not zero'''
    def __init__(self, name, sx, sy, mu, phi, i15mode=False, mu_offset = 0, phi_offset = 0, help_text=None):
        self.setName(name)
        if help_text is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help_text
        self.setInputNames([name])
        self.setOutputFormat(['%4.4f'])
        self.Units=['mm']
        self.setLevel(5)
        self.sx = sx
        self.sy = sy
        self.mu = mu
        self.phi = phi
        self.i15mode = i15mode
        self.mu_offset = mu_offset
        self.phi_offset = phi_offset
        self.verbose=True
        self.no_move=False

    def xyFromPerpPara(self, sperp, spara):
        murad, phirad = self.getPositions()
        angle=phirad-murad
        if self.i15mode: # sx inverted compared to i16
#     dxI:    - DE  *COS(T)    - DA  *SIN(T)
            x=-sperp*cos(angle)-spara*sin(angle)
        else:
#     dx:     +DE  *COS(T)    + DA  *SIN(T)
            x=sperp*cos(angle)+spara*sin(angle)
        
        # - DE11*SIN(T11)  + DA11*COS(T11)
        y=-sperp*sin(angle)+spara*cos(angle)
        return x, y

    def asynchronousMoveToPerpendicular(self,value):
        murad, phirad = self.getPositions()
        
        if self.i15mode: # sx inverted compared to i16
            clock_x, clock_y = self.xyFromPerpPara(value, self.getPositionParallel())
        else:
            anticlock_x=self.sy()*sin(phirad-murad)+self.sx()*cos(phirad-murad)
            clock_x=anticlock_x*cos(phirad-murad)-value*sin(phirad-murad)
            clock_y=value*cos(phirad-murad)+anticlock_x*sin(phirad-murad)
        
        self.setPositions(value, clock_x, clock_y)

    def asynchronousMoveToParallel(self,value):
        murad, phirad = self.getPositions()
        
        if self.i15mode: # sx inverted compared to i16
            clock_x, clock_y = self.xyFromPerpPara(self.getPositionPerpendicular(), value)
        else:
            anticlock_y=self.sy()*cos(phirad-murad)-self.sx()*sin(phirad-murad)
            clock_x=value*cos(phirad-murad)-anticlock_y*sin(phirad-murad)
            clock_y=anticlock_y*cos(phirad-murad)+value*sin(phirad-murad)
        
        self.setPositions(value, clock_x, clock_y)

    def getPositionPerpendicular(self):
        murad, phirad = self.getPositions()
        angle=phirad-murad
        if self.i15mode: # sx inverted compared to i16
            #dperpI: -   DX  *COS(T)    -     DY  *SIN(T)
            return -self.sx()*cos(angle)-self.sy()*sin(angle)
        else:
            return self.sy()*cos(angle)-self.sx()*sin(angle)

    def getPositionParallel(self):
        murad, phirad = self.getPositions()
        angle=phirad-murad
        if self.i15mode: # sx inverted compared to i16
            #      -     DX  *SIN(T)    +     DY*  COS(T)
            return -self.sx()*sin(angle)+self.sy()*cos(angle)
        else:
            return self.sx()*cos(angle)+self.sy()*sin(angle)

    def isBusy(self):
        return self.sx.isBusy() or self.sy.isBusy()

    def setPositions(self, value, sx_pos, sy_pos):
        if self.verbose:
            print "%s: asynchronousMoveTo(%r) called" % (self.name, value)
        if self.verbose or self.no_move:
            print "%s: %s %s to %f & %s to %f" % (self.name, "Would move" if
                self.no_move else "Moving", self.sx.name, sx_pos, self.sy.name, sy_pos)
        if not self.no_move:
            self.sy.asynchronousMoveTo(sy_pos)
            self.sx.asynchronousMoveTo(sx_pos)

    def getPositions(self):
        return (self.mu()-self.mu_offset)*(pi/180), (self.phi()-self.phi_offset)*(pi/180)

    def asynchronousMoveTo(self,value):
        self.asynchronousMoveToPerpendicular(value)

    def getPosition(self):
        return self.getPositionPerpendicular()

class ParallelSampleMotion(PerpendicularSampleMotion):
    '''Device to move sample stage parallel to the beam when phi or mu are not zero'''
    def asynchronousMoveTo(self,value):
        self.asynchronousMoveToParallel(value)

    def getPosition(self):
        return self.getPositionParallel()
