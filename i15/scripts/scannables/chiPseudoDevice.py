from gda.device.scannable import PseudoDevice

import future.EulerianKconversion as H

class ChiPseudoDevice(PseudoDevice):
    def __init__(self, name, theta, kappa, phi, thoffset=2.2, phioffset=2.2):
        self.setName(name)
        self.setInputNames(['chi'])
        self.setExtraNames(['phi','eta'])
        self.setLevel(5)
        self.theta=theta
        self.kappa=kappa
        self.phi=phi
        self.hconv=H.EulerianKconversion(theta, kappa, phi, thoffset, phioffset)

    def asynchronousMoveTo(self,new_position):
        values=self.hconv.KtoEulerian()
        listaval=[values[0],new_position,values[2]]
        dempos=self.hconv.EuleriantoK(listaval)
        #print dempos
        #pos dkphi dempos[0] dktheta dempos[2] dkappa dempos[1]
        self.phi.asynchronousMoveTo(dempos[0])
        self.theta.asynchronousMoveTo(dempos[2])
        self.kappa.asynchronousMoveTo(dempos[1])

    def getPosition(self):
        xx=self.hconv.KtoEulerian()
        return [xx[1],xx[0],xx[2]]

    def isBusy(self):
        return self.phi.isBusy() or self.theta.isBusy() or self.kappa.isBusy()

#chi=ChiPseudoDevice('chi')
