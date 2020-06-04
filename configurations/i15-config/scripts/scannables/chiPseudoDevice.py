from gda.device.scannable import ScannableMotionBase
from time import sleep

import future.EulerianKconversion as H

# http://sector7.xor.aps.anl.gov/calculators/kappa.html

class ChiPseudoDevice(ScannableMotionBase):
    def __init__(self, name, theta, kappa, phi, thoffset=2.2, phioffset=2.2):
        self.setName(name)
        self.setInputNames(['chi'])
        self.setExtraNames(['phi','theta'])
        self.setLevel(5)
        self.theta=theta
        self.kappa=kappa
        self.phi=phi
        self.hconv=H.EulerianKconversion(theta, kappa, phi, thoffset, phioffset)
        self.verbose = False
        self.vphi, self.vkappa, self.vtheta = (
            phi.speed if phi.isConfigured() else 0, 
            kappa.speed if kappa.isConfigured() else 0, 
            theta.speed if theta.isConfigured() else 0
        )
        self.speedsAdjusted=False

    def asynchronousMoveTo(self,new_chi):
        Phi, _, Theta = self.hconv.KtoEulerian() 
        kphi, kappa, ktheta = self.hconv.EuleriantoK([Theta, new_chi, Phi]) # theta_now chi_now phi_now > kphi, kappa, ktheta
        
        if self.verbose:
            print "asynchronousMoveTo: kphi=%r, kappa=%r, ktheta=%r" % (kphi, kappa, ktheta)
        
        kphi_now, kappa_now, ktheta_now = self.phi(), self.kappa(), self.theta()
        if self.verbose:
            print "asynchronousMoveTo: kphi_now=%r, kappa_now=%r, ktheta_now=%r" % (kphi_now, kappa_now, ktheta_now)
        
        self.vphi, self.vkappa, self.vtheta = self.phi.speed, self.kappa.speed, self.theta.speed
        if self.verbose:
            print "asynchronousMoveTo: vphi=%r, vkappa=%r, vtheta=%r" % (self.vphi, self.vkappa, self.vtheta)
        
        tphi   =   abs(kphi_now-kphi)/self.vphi
        tkappa =  abs(kappa_now-kappa)/self.vkappa
        ttheta = abs(ktheta_now-ktheta)/self.vtheta
        
        t = (tphi, tkappa, ttheta)
        tmax = max(t)
        if self.verbose:
            print "asynchronousMoveTo: tphi=%r, tkappa=%r, ttheta=%r, tmax=%r" % (t+(tmax,))
        
        sphi   =   self.vphi if   tphi <= 0 else self.vphi/(tmax/tphi)
        skappa = self.vkappa if tkappa <= 0 else self.vkappa/(tmax/tkappa)
        stheta = self.vtheta if ttheta <= 0 else self.vtheta/(tmax/ttheta)
        if self.verbose:
            print "asynchronousMoveTo: sphi=%r, skappa=%r, stheta=%r" % (sphi, skappa, stheta)
        self.speedsAdjusted = True
        self.phi.speed, self.kappa.speed, self.theta.speed = sphi, skappa, stheta
        
        if self.verbose:
            print "asynchronousMoveTo: vphi=%r, vkappa=%r, vtheta=%r" % (self.phi.speed, self.kappa.speed, self.theta.speed)
        
        self.phi.asynchronousMoveTo(kphi)
        self.theta.asynchronousMoveTo(ktheta)
        self.kappa.asynchronousMoveTo(kappa)
        
        self.phi.waitWhileBusy()
        self.theta.waitWhileBusy()
        self.kappa.waitWhileBusy()
        
        self.phi.speed, self.kappa.speed, self.theta.speed = self.vphi, self.vkappa, self.vtheta
        self.speedsAdjusted=False
        if self.verbose:
            print "asynchronousMoveTo: vphi=%r, vkappa=%r, vtheta=%r" % (self.phi.speed, self.kappa.speed, self.theta.speed)
        
        #values=self.hconv.KtoEulerian() # Phi, Chi, Theta
        #listaval=[values[0],new_chi,values[2]]  # Phi,     Chi,    Theta
        #dempos=self.hconv.EuleriantoK(listaval) #theta_now chi_now phi_now
        ##print dempos
        ##pos dkphi dempos[0] dktheta dempos[2] dkappa dempos[1]
        #self.phi.asynchronousMoveTo(dempos[0])
        #self.theta.asynchronousMoveTo(dempos[2])
        #self.kappa.asynchronousMoveTo(dempos[1])
        return

    def atPointEnd(self):
        if self.speedsAdjusted:
            self.phi.speed, self.kappa.speed, self.theta.speed = self.vphi, self.vkappa, self.vtheta
            if self.verbose:
                print "atPointEnd: vphi=%r, vkappa=%r, vtheta=%r" % (self.phi.speed, self.kappa.speed, self.theta.speed)

    def stop(self):
        self.phi.stop()
        self.theta.stop()
        self.kappa.stop()
        if self.speedsAdjusted:
            self.phi.speed, self.kappa.speed, self.theta.speed = self.vphi, self.vkappa, self.vtheta
            print "Stop! vphi=%r, vkappa=%r, vtheta=%r" % (self.phi.speed, self.kappa.speed, self.theta.speed)

    def getPosition(self):
        Phi, Chi, Theta = self.hconv.KtoEulerian()
        return [Chi, Phi, Theta]
        #xx=self.hconv.KtoEulerian()
        #return [xx[1],xx[0],xx[2]]

    def isBusy(self):
        return self.phi.isBusy() or self.theta.isBusy() or self.kappa.isBusy()

    def __repr__(self):
        return "ChiPseudoDevice(name=%s, theta=%s, kappa=%s, phi=%s, thoffset=%r, phioffset=%r)" % (
            self.name, self.theta.name, self.kappa.name, self.phi.name, self.hconv.thoffset, self.hconv.phioffset)

#chi=ChiPseudoDevice('chi')
