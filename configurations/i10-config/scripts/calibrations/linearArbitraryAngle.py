'''
class that provides control of Linear Arbitrary Angle in 'la' polarisation mode.

It implements linear interpolation from angle requested to jawphase motor position as Poly([-120./7.5, 1./7.5], power0first=True).
The angle is delivered by moving jawphase motor

There is no stop() method implemented as there is reverse interpolation from jawphase to angle is not supported.

the code logic is extracted from EnergyScannableLinearArbitrary class in OLD system

Created on Apr 20, 2021

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from calibrations.energy_polarisation_class import X_RAY_POLARISATIONS
from Diamond.Poly import Poly
from calibrations.xraysource import X_RAY_SOURCE_MODES

class LinearArbitraryAngle(ScannableMotionBase):
    
    def __init__(self, name, idu_jawphase, idd_jawphase, smode, pol, jawphase_from_angle=Poly([-120./7.5, 1./7.5], power0first=True), angle_threshold_deg = 30.0):
        self.setName(name)
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(["%f"])
        
        self.idu_jawphase = idu_jawphase
        self.idd_jawphase = idd_jawphase
        self.smode = smode
        self.pol = pol
        self.jawphase_from_angle = jawphase_from_angle
        self.angle_threshold_deg = angle_threshold_deg
        
        #cached data
        self.jawphase = None
        self.angle_deg = 0.0

    # def __str__(self):
    #     output_format=", ".join([ a + "=" + b for (a,b) in zip(
    #           self.getInputNames() + self.getExtraNames(), self.getOutputFormat())])
    #     return output_format % self.getPosition()

    # def __repr__(self):
    #     output_format = "LinearArbitraryAngle(%r, %r, %r, %r, %r, %r)"
    #     return output_format % (self.getName(), self.idu_jawphase.name, self.idd_jawphase.name, self.smode.name, self.pol.name, "jawphase_from_angle=Poly([-120./7.5, 1./7.5], power0first=True), angle_threshold_deg = 30.0)")

    def isBusy(self):
        return self.jawphase.isBusy()
    
    def asynchronousMoveTo(self, angle_deg):
        self.angle_deg = float(angle_deg)
        mode = self.smode.getPosition()
        if mode == X_RAY_SOURCE_MODES[0] :
            self.jawphase = self.idd_jawphase
        elif mode == X_RAY_SOURCE_MODES[1]:
            self.jawphase = self.idu_jawphase
        else:
            message="Source mode '%s' is not supported." % (mode)
            raise RuntimeError(message)
           
        pol=self.pol.getPosition()
        if  pol != X_RAY_POLARISATIONS[4]:
            message="Angle control is not available in polarisation '%s' in source mode '%s'" % (pol, mode)
            raise RuntimeError(message)
        
        alpha_real = self.angle_deg if self.angle_deg > self.angle_threshold_deg else self.angle_deg + 180.
        jawphase = self.jawphase_from_angle(alpha_real)
        if jawphase < -12 or jawphase > 12:
            raise RuntimeError("jawphase position for angle %f is outside permitted range [-12,12]")
        self.jawphase.asynchronousMoveTo(jawphase)

    def getPosition(self):
        pol=self.pol.getPosition()
        if pol in X_RAY_POLARISATIONS[:2] or pol == X_RAY_POLARISATIONS[6]:
            self.setOutputFormat(["%s"])
            return "undefined"
        else:
            self.setOutputFormat(["%f"])
            if pol == X_RAY_POLARISATIONS[2] or pol == X_RAY_POLARISATIONS[5]:
                return 0
            if pol == X_RAY_POLARISATIONS[3] :
                return 90
            if pol == X_RAY_POLARISATIONS[4] :
                return self.angle_deg
            self.setOutputFormat(["%s"])
            return "undefined"
    
    