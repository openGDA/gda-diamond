from math import sin, cos

from gda.device.scannable.scannablegroup import ScannableGroup, ScannableMotionWithScannableFieldsBase
from gdaserver import  x, y,z, chi, phi
from diffcalc.util import TORAD 

# Manipulator position where all rotation axes
# intersect in a single point in the middle of the beam
AXES_ZERO = (6.1, -0.3878, -0.111)


class ToolpointMotion(ScannableMotionWithScannableFieldsBase):
    '''Define virtual manipulator translations as of the sample stage is mounted on top of diffractometer circles chi and phi'''

    def __init__(self, name, sax, say, saz, chi_rot, phi_rot, zero_pos):
        self.x0, self.y0, self.z0 = zero_pos
        #self.xyz_group = ScannableGroup('xyz_stage', (sax, say, saz, chi_rot, phi_rot))
        self.xyz_group = ScannableGroup()
        self.xyz_group.addGroupMember(sax)
        self.xyz_group.addGroupMember(say)
        self.xyz_group.addGroupMember(saz)
        self.xyz_group.addGroupMember(chi_rot)
        self.xyz_group.addGroupMember(phi_rot)
        self.xyz_group.setName('xyz_stage')
        self.xyz_group.configure()
        self.setName(name)
        self.setInputNames(['u', 'v', 'w', 'ps_chi', 'ps_phi'])
        self.setOutputFormat(['%7.5f'] * 5)

        self.completeInstantiation()
        self.setAutoCompletePartialMoveToTargets(True)

    def rawAsynchronousMoveTo(self, pos):
        if len(pos) != 5: raise ValueError('Toolpoint device expects five inputs')
        nu, nv, nw, ps_chi, ps_phi = pos
        chi_pos = ps_chi * TORAD
        phi_pos = ps_phi * TORAD
        
        sx = self.x0 + nu*cos(chi_pos) + nv*sin(chi_pos)*sin(phi_pos) + nw*cos(phi_pos)*sin(chi_pos)
        sy = self.y0 + nv*cos(phi_pos) - nw*sin(phi_pos)
        sz = self.z0 - nu*sin(chi_pos) + nv*cos(chi_pos)*sin(phi_pos) + nw*cos(chi_pos)*cos(phi_pos)
        
        self.xyz_group.asynchronousMoveTo([sx, sy, sz, ps_chi, ps_phi])

    def rawGetPosition(self):
        tx, ty, tz, ps_chi, ps_phi  = [float(t) for t in self.xyz_group.getPosition()]
        chi_pos = ps_chi * TORAD
        phi_pos = ps_phi * TORAD
        dx = tx - self.x0
        dy = ty - self.y0
        dz = tz - self.z0
        nu = dx*cos(chi_pos) - dz*sin(chi_pos)
        nv = dx*sin(chi_pos)*sin(phi_pos) + dy*cos(phi_pos) + dz*cos(chi_pos)*sin(phi_pos)
        nw = dx*cos(phi_pos)*sin(chi_pos) - dy*sin(phi_pos) + dz*cos(chi_pos)*cos(phi_pos)
        return nu, nv, nw, ps_chi, ps_phi

    def getFieldPosition(self, i):
        return self.getPosition()[i]

    def isBusy(self):
        return self.xyz_group.isBusy()

    def waitWhileBusy(self):
        return self.xyz_group.waitWhileBusy()


tp = ToolpointMotion('tp', x, y, z, chi, phi, AXES_ZERO)

u, v, w, ps_chi, ps_phi = tp.u, tp.v, tp.w, tp.ps_chi, tp.ps_phi

