# Scannables for moving sample perpendicular and parallel to the beam
#
# Based on i16's gda/config/scripts/Sample_perpMotion.py @717f87f
#
# On I15, calc_mode=None was tested using the following assumptions
# * At the `zero` position, where sx=sperp and sy=spara, phi-phi_offset is 0 (58-58) and mu-mu_offset is 0 (0-0)
# * The sample x and y stages are on the phi axis, so rotate with it.
# * sx is +ve to the right (not the usual left) when looking along the beam at the `zero` position. 
# * sy is the sample stage, +ve is along the beam towards (as usual) from the detector at the `zero` position.
# * mu is static and always returns 0
# * phi is horizontal at with Kappa at -134.74 and theta @-34.05
#
# In order to extend this class to remove the restrictions on kappa and theta (i.e. allow non flat phi) the
# option of calc_mode='jama' and 'scisoftpi' were added. They are intended to be equivalent to each other.
#
# On I15, calc_mode='jama'/'scisoftpi' were defined, but development was halted before they could be made to
# match up with calc_mode=None.
#
# With i15mode=False, calc_mode='jama'/'scisoftpi' will fail since appropriate transforms have not been defined.
#
#sperp and spara using rotation matrix method
#15/10/2012 implemented horizontal scattering mode (mu different from zero)

#sperp=PerpendicularSampleMotion("sperp", sx=sx, sy=sy, mu=mu, phi=phi,
#    help="To move sample stage perpendicular to the beam.")

#spara=ParallelSampleMotion("spara", sx=sx, sy=sy, mu=mu, phi=phi,
#    help="To move sample stage parallel to the beam.")

#I15:
#dperp=PerpendicularSampleMotion("dperp", sx=dx, sy=dy, mu=dmu, phi=dkphi, i15mode=True, mu_offset=0, phi_offset=58,
#    help_text="To move sample stage horizontal to the beam.")

#dpara=ParallelSampleMotion("dpara", sx=dx, sy=dy, mu=dmu, phi=dkphi, i15mode=True, mu_offset=0, phi_offset=58,
#    help_text="To move sample stage parallel to the beam.")

#dheight=HeightSampleMotion("dpara", sx=dx, sy=dy, sz=dz, mu=dmu, phi=dkphi, i15mode=True, mu_offset=0, phi_offset=58,
#    help_text="To move sample stage vertical to the beam.")

from gda.device.scannable import ScannableMotionBase
from Jama import Matrix as M
from scisoftpy import dot, pi, sin, cos
from scisoftpy.linalg import inv

import scisoftpy as dnp

class PerpendicularSampleMotion(ScannableMotionBase):
    '''Device to move sample stage perpendicular to the beam'''

    jamaMode='jama'
    scisoftpyMode='scisoftpy'

    def __init__(self, name, sx, sy, sz=None, mu=None, phi=None, kappa=None, theta=None, i15mode=False, mu_offset = 0, phi_offset = 0, calc_mode=None, help_text=None):
        self.setName(name)
        if help_text is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help_text
        self.setInputNames([name])
        self.setOutputFormat(['%4.4f'])
        self.Units=['mm']
        self.setLevel(5)
        self.sx = sx
        self.sy = sy
        self.sz = sz
        self.mu = mu
        self.phi = phi
        self.kappa = kappa
        self.theta = theta
        self.i15mode = i15mode
        self.mu_offset = mu_offset
        self.phi_offset = phi_offset
        self.verbose=True
        self.no_move=False

        self.setCalcMode(calc_mode)

    def setCalcMode(self, calc_mode=None):
        """ Note that when mode=None then this class will work as it did originally, where the Phi axis should be
            pointing straight up.
            
            When mode is jamaMode or scisoftpyMode, it will work according to the calculations in I15-207
            where the phi axis may be in any orientation. See http://jira.diamond.ac.uk/browse/I15-207
        """
        self.calc_mode=calc_mode

        if self.calc_mode==self.jamaMode :
            rx = lambda t : M([[1, 0, 0],
                               [0, cos(t), - sin(t)],
                               [0, sin(t), cos(t)]])
            ry = lambda t : M([[cos(t), 0, sin(t)],
                               [0, 1, 0],
                               [-sin(t), 0, cos(t)]])
            rz = lambda t : M([[cos(t), -sin(t), 0],
                               [sin(t), cos(t), 0],
                               [0, 0, 1]])
        if self.calc_mode==self.scisoftpyMode:
            rx = lambda t : dnp.array([[1, 0, 0],
                                       [0, cos(t), - sin(t)],
                                       [0, sin(t), cos(t)]])
            ry = lambda t : dnp.array([[cos(t), 0, sin(t)],
                                       [0, 1, 0],
                                       [-sin(t), 0, cos(t)]])
            rz = lambda t : dnp.array([[cos(t), -sin(t), 0],
                                       [sin(t), cos(t), 0],
                                       [0, 0, 1]])

        self.DEG2RAD = pi / 180

        Tmu    = lambda t : rx(t)
        Ttheta = lambda t : ry(t)

        if self.calc_mode == self.jamaMode:
            if self.i15mode:
                Tkappa = lambda t : rz(sin(0.7660443)).inverse().times(rx(t).inverse().times(rz(sin(0.7660443))))
                # Numpy:            rz(np.sin(0.7660443)).I * rx(t).I * rz(np.sin(0.7660443))
            else:
                raise NotImplementedError("Tkappa not defined for i15mode=%r use case with mode=%r!" % (self.i15mode, self.calc_mode))
        if self.calc_mode == self.scisoftpyMode:
            if self.i15mode:
                Tkappa = lambda t : dot(inv(rz(sin(0.7660443))) , dot(inv(rx(t)), rz(sin(0.7660443))))
                # Numpy:            rz(np.sin(0.7660443)).I * rx(t).I * rz(np.sin(0.7660443))
            else:
                raise NotImplementedError("Tkappa not defined for i15mode=%r use case with mode=%r!" % (self.i15mode, self.calc_mode))

        Tphi   = lambda t : ry(t)

        if self.calc_mode == self.jamaMode:
            if self.i15mode:
                S = M([[0, 1, 0],
                       [0, 0, -1],
                       [1, 0, 0]])
            else:
                raise NotImplementedError("S not defined for i15mode=%r use case with mode=%r!" % (self.i15mode, self.calc_mode))
        if self.calc_mode == self.scisoftpyMode:
            if self.i15mode:
                S = dnp.array([[0, 1, 0],
                               [0, 0, -1],
                               [1, 0, 0]])
            else:
                raise NotImplementedError("S not defined for i15mode=%r use case with mode=%r!" % (self.i15mode, self.calc_mode))

        # T = S.I * (Tmu(mu) * Ttheta(theta) * Tkappa(kappa) * Tphi(phi)).I
        if self.calc_mode == self.jamaMode:
            self.T = lambda mu_rad, theta_rad, kappa_rad, phi_rad : \
                S.inverse().times(
                    Tmu(mu_rad).times(Ttheta(theta_rad).times(Tkappa(kappa_rad).times(Tphi(phi_rad)))).inverse()
                )
        if self.calc_mode == self.scisoftpyMode:
            self.T = lambda mu_rad, theta_rad, kappa_rad, phi_rad : \
                dot(inv(S) , 
                    inv(dot(Ttheta(theta_rad) , dot(Tkappa(kappa_rad) , Tphi(phi_rad))))
                )

    def stageFromLab(self, dheight, dperp, dpara, mu_rad, theta_rad, kappa_rad, phi_rad):
        if self.calc_mode == self.jamaMode:
            stage = self.T(mu_rad, theta_rad, kappa_rad, phi_rad).times(M([[dheight], [dperp], [dpara]]))
            dx, dy, dz = stage.get(0,0), stage.get(1,0), stage.get(2,0)

        if self.calc_mode == self.scisoftpyMode:
            stage = dot(self.T(mu_rad, theta_rad, kappa_rad, phi_rad), dnp.array([[dheight], [dperp], [dpara]]))
            dx, dy, dz = stage.item(0,0), stage.item(1,0), stage.item(2,0)
        return dx, dy, dz
        # Numpy: (dx, dy, dz) = T * np.matrix([[x], [y], [z]])

    def labFromStage(self, dx, dy, dz, mu_rad, theta_rad, kappa_rad, phi_rad):
        if self.calc_mode == self.jamaMode:
            lab = self.T(mu_rad, theta_rad, kappa_rad, phi_rad).inverse().times(M([[dx], [dy], [dz]]))
            dheight, dperp, dpara = lab.get(0,0), lab.get(1,0), lab.get(2,0)

        if self.calc_mode == self.scisoftpyMode:
            lab = dot(inv(self.T(mu_rad, theta_rad, kappa_rad, phi_rad)), dnp.array([[dx], [dy], [dz]]))
            dheight, dperp, dpara = lab.item(0,0), lab.item(1,0), lab.item(2,0)

        return dheight, dperp, dpara
        # Numpy: (dheight, dperp, dpara) = (x, y, z) = T.I * np.matrix([[dx], [dy], [dz]])

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
        if self.calc_mode:
            dx, dy, dz = self.stageFromLab(dheight=self.getPositionHeight(), dperp=value, dpara=self.getPositionParallel())
            self.setPositions(value, dx, dy, dz)
            return

        murad, phirad = self.getPositions()
        
        if self.i15mode: # sx inverted compared to i16
            clock_x, clock_y = self.xyFromPerpPara(value, self.getPositionParallel())
        else:
            anticlock_x=self.sy()*sin(phirad-murad)+self.sx()*cos(phirad-murad)
            clock_x=anticlock_x*cos(phirad-murad)-value*sin(phirad-murad)
            clock_y=value*cos(phirad-murad)+anticlock_x*sin(phirad-murad)
        
        self.setPositions(value, clock_x, clock_y)

    def asynchronousMoveToParallel(self,value):
        if self.calc_mode:
            dx, dy, dz = self.stageFromLab(dheight=self.getPositionHeight(), dperp=self.getPositionPerpendicular(), dpara=value)
            self.setPositions(value, dx, dy, dz)
            return

        murad, phirad = self.getPositions()
        
        if self.i15mode: # sx inverted compared to i16
            clock_x, clock_y = self.xyFromPerpPara(self.getPositionPerpendicular(), value)
        else:
            anticlock_y=self.sy()*cos(phirad-murad)-self.sx()*sin(phirad-murad)
            clock_x=value*cos(phirad-murad)-anticlock_y*sin(phirad-murad)
            clock_y=anticlock_y*cos(phirad-murad)+value*sin(phirad-murad)
        
        self.setPositions(value, clock_x, clock_y)

    def asynchronousMoveToHeight(self,value):
        if self.calc_mode:
            dx, dy, dz = self.stageFromLab(dheight=value, dperp=self.getPositionPerpendicular(), dpara=self.getPositionParallel())
            self.setPositions(value, dx, dy, dz)
            return

        self.setPositions(value, self.sx(), self.sy(), value)

    def getPositionPerpendicular(self):
        if self.calc_mode:
            _, dperp, _ = self.labFromStage(self.sx(), self.sy(), self.sz())
            return dperp

        murad, phirad = self.getPositions()
        angle=phirad-murad
        if self.i15mode: # sx inverted compared to i16
            #dperpI: -   DX  *COS(T)    -     DY  *SIN(T)
            return -self.sx()*cos(angle)-self.sy()*sin(angle)
        else:
            return self.sy()*cos(angle)-self.sx()*sin(angle)

    def getPositionParallel(self):
        if self.calc_mode:
            _, _, dpara = self.labFromStage(self.sx(), self.sy(), self.sz())
            return dpara

        murad, phirad = self.getPositions()
        angle=phirad-murad
        if self.i15mode: # sx inverted compared to i16
            #      -     DX  *SIN(T)    +     DY*  COS(T)
            return -self.sx()*sin(angle)+self.sy()*cos(angle)
        else:
            return self.sx()*cos(angle)+self.sy()*sin(angle)

    def getPositionHeight(self):
        if self.calc_mode:
            dheight, _, _ = self.labFromStage(self.dx(), self.dy(), self.dz())
            return dheight

        return self.dz()

    def isBusy(self):
        return self.sx.isBusy() or self.sy.isBusy()

    def setPositions(self, value, sx_pos, sy_pos, sz_pos=None):
        if self.verbose:
            print "%s: asynchronousMoveTo(%r) called" % (self.name, value)
        if self.verbose or self.no_move:
            print "%s: %s %s to %f & %s to %f" % (self.name, "Would move" if
                self.no_move else "Moving", self.sx.name, sx_pos, self.sy.name, sy_pos)
            if self.sz and sz_pos <> None:
                print "%s: %s %s to %f" % (self.name, "Would also move" if
                    self.no_move else "Moving", self.sz.name, sz_pos)
        if not self.no_move:
            self.sy.asynchronousMoveTo(sy_pos)
            self.sx.asynchronousMoveTo(sx_pos)
            if self.sz and sz_pos <> None:
                self.sz.asynchronousMoveTo(sz_pos)

    def getPositions(self):
        return (self.mu()-self.mu_offset)*(pi/180), (self.phi()-self.phi_offset)*(pi/180)

    def asynchronousMoveTo(self,value):
        self.asynchronousMoveToPerpendicular(value)

    def getPosition(self):
        return self.getPositionPerpendicular()

class ParallelSampleMotion(PerpendicularSampleMotion):
    '''Device to move sample stage parallel to the beam'''
    def asynchronousMoveTo(self,value):
        self.asynchronousMoveToParallel(value)

    def getPosition(self):
        return self.getPositionParallel()

class HeightSampleMotion(PerpendicularSampleMotion):
    '''Device to move sample stage up and down relative to the beam'''
    def asynchronousMoveTo(self,value):
        self.asynchronousMoveToHeight(value)

    def getPosition(self):
        return self.getPositionHeight()
