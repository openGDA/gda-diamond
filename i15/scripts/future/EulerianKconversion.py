## @file EulerianKconversion.py  contains a module that
#  calculates the angles used in the transformation
#  between the Eulerian and the K geometry.
#  Usually is not accessed directly but through EulerianKconversionModes
#  @author Alessandro Bombardi
#  @version 1.0 (alpha release)
#  Please report bugs to Alessandro.Bombardi@diamond.ac.uk
#  Diamond Light Source Ltd.

from math import pi, tan, cos, sin, atan, asin

# Global Variables of the module; Please do not change
class EulerianKconversion:

    def __init__(self, dkth, dkap, dkphi, thoffset=2.2, phioffset=2.2):
        self.Kalpha=50.*pi/180.0 # Value to have chi=90 
        self.K=dkap
        self.Kth=dkth
        self.Kphi=dkphi
        self.thoffset=thoffset
        self.phioffset=phioffset

    ## Public function returns a list in the form
    #  [[kth kap kphi],[kth kap kphi],[kth kap kphi],[kth kap kphi]]
    #  of the four possible solution for the Eulerian - K conversion.
    def EuleriantoK(self,x=None):
        """@sig public double[[],[],[],[]] EuleriantoK([theta_now chi_now phi_now])"""
        if x==None:
            xxx=self.KtoEulerian()
            theta_now=xxx[0]
            chi_now=xxx[1]
            phi_now=xxx[2]
        else:
            theta_now=x[0]
            chi_now=x[1]
            phi_now=x[2]

        if abs(chi_now) <= self.Kalpha*180./pi*2:
            delta1=-asin(tan(pi/180.*chi_now/2.)/tan(self.Kalpha))
            K1=-asin(cos(delta1)*sin(pi/180*chi_now)/sin(self.Kalpha))*180/pi
            if abs(chi_now) > 65.595503 and chi_now > 0.:
                K1=self.setRange(180-K1)
            elif abs(chi_now) > 65.595503 and chi_now < 0.:
                K1=self.setRange(-180-K1)
            theta_K1=self.setRange(theta_now-delta1*180/pi,-90.,270.)
            phi_K1=self.setRange(phi_now-delta1*180/pi,-90.,270.)
            theta_K2=self.setRange(theta_now-(pi-delta1)*180/pi,-90.,270.)
            phi_K2=self.setRange(phi_now-(pi-delta1)*180/pi,-90.,270.)
            K2=self.setRange(K1)
        elif abs(chi_now) > self.Kalpha*180./pi*2:
            K1='NA'
            K2='NA'
            phi_K1='NA'
            phi_K2='NA'
            theta_K1='NA'
            theta_K2='NA'
        return [phi_K1+self.phioffset,K1,theta_K1-90-self.thoffset]

    def KtoEulerian(self):
        """@sig public double[] EuleriantoK(double [],integer)"""
        y=1
        if y==1:
            gamma = -atan(cos(self.Kalpha)*tan(self.K()/2.*pi/180.))*180./pi
            Chi   = -2*asin(sin(self.K()*pi/180/2)*sin(self.Kalpha))*180./pi
            Theta =  self.Kth()-gamma+90
            Phi   =  self.Kphi()-gamma
        Theta=self.setRange(Theta,-90.,270.)
        Chi=self.setRange(Chi)
        Phi=self.setRange(Phi,-90.,270.)
        return [Phi,Chi,Theta]

    def setRange(self,x,m=-180.,M=180.):
        if x  <  m:
            x=x+360.
        elif x > M:
            x=x-360.
        return x

    def __repr__(self):
        return '<EulerianKconversion error>'
