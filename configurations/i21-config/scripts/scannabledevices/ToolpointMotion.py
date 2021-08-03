from math import sin, cos

from gda.device.scannable.scannablegroup import ScannableGroup, ScannableMotionWithScannableFieldsBase
from gdaserver import  x, y,z, chi, phi  # @UnresolvedImport
from diffcalc.util import TORAD  # @UnresolvedImport
from gda.observable import IObserver

# Manipulator position where all rotation axes
# intersect in a single point in the middle of the beam
#AXES_ZERO = (6.1, -0.3878, -0.111)
#AXES_ZERO = (6.12, -0.2189, 0.9214)
AXES_ZERO = (6.12, -0.3141, 0.9214)


class ToolpointMotion(ScannableMotionWithScannableFieldsBase, IObserver):
    '''Define virtual manipulator translations as of the sample stage is mounted on top of diffractometer circles chi and phi'''

    def __init__(self, name, sax, say, saz, chi_rot, phi_rot, zero_pos):
        self.x0, self.y0, self.z0 = zero_pos
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
        # make tool point tracks real axes changes in hardware
        self.xyz_group.addIObserver(self)

    def checkPositionValid(self, pos):
        if len(pos) != 5: raise ValueError('Toolpoint device expects five inputs')
        nu, nv, nw, ps_chi, ps_phi = pos
        
        str_chi = chi.checkPositionValid(ps_chi)
        if str_chi:
            return str_chi
        str_phi = phi.checkPositionValid(ps_phi)
        if str_phi:
            return str_phi

        chi_pos = ps_chi * TORAD
        phi_pos = ps_phi * TORAD
        sx = self.x0 + nu*cos(chi_pos) + nv*sin(chi_pos)*sin(phi_pos) + nw*cos(phi_pos)*sin(chi_pos)
        sy = self.y0 + nv*cos(phi_pos) - nw*sin(phi_pos)
        sz = self.z0 - nu*sin(chi_pos) + nv*cos(chi_pos)*sin(phi_pos) + nw*cos(chi_pos)*cos(phi_pos)

        str_x = x.checkPositionValid(sx)
        if str_x:
            return str_x
        str_y = y.checkPositionValid(sy)
        if str_y:
            return str_y
        str_z = z.checkPositionValid(sz)
        if str_z:
            return str_z
        return None

    def rawAsynchronousMoveTo(self, pos):
        if len(pos) != 5: raise ValueError('Toolpoint device expects five inputs')
        nu, nv, nw, ps_chi, ps_phi = pos
        chi_pos = ps_chi * TORAD
        phi_pos = ps_phi * TORAD
        
        sx = self.x0 + nu*cos(chi_pos) + nv*sin(chi_pos)*sin(phi_pos) + nw*cos(phi_pos)*sin(chi_pos)
        sy = self.y0 + nv*cos(phi_pos) - nw*sin(phi_pos)
        sz = self.z0 - nu*sin(chi_pos) + nv*cos(chi_pos)*sin(phi_pos) + nw*cos(chi_pos)*cos(phi_pos)
        
        self.xyz_group.asynchronousMoveTo([sx, sy, sz, ps_chi, ps_phi])
        
    def update(self, theobserved, changecode):  # @UnusedVariable
        if theobserved == self.xyz_group:
            # send tool point values to observer, not the change code which default to scannable group status.
            self.notifyIObservers(self, self.rawGetPosition())

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
    
    def stop(self):
        self.xyz_group.stop()

    def getFieldPosition(self, i):
        return self.getPosition()[i]

    def isBusy(self):
        return self.xyz_group.isBusy()

    def waitWhileBusy(self):
        return self.xyz_group.waitWhileBusy()


tp = ToolpointMotion('tp', x, y, z, chi, phi, AXES_ZERO)

u, v, w, ps_chi, ps_phi = tp.u, tp.v, tp.w, tp.ps_chi, tp.ps_phi

u.setLowerGdaLimits([x.getLowerInnerLimit() - AXES_ZERO[0],])
u.setUpperGdaLimits([x.getUpperInnerLimit() - AXES_ZERO[0],])
v.setLowerGdaLimits([y.getLowerInnerLimit() - AXES_ZERO[1],])
v.setUpperGdaLimits([y.getUpperInnerLimit() - AXES_ZERO[1],])
w.setLowerGdaLimits([z.getLowerInnerLimit() - AXES_ZERO[2],])
w.setUpperGdaLimits([z.getUpperInnerLimit() - AXES_ZERO[2],])
ps_chi.setLowerGdaLimits([chi.getLowerInnerLimit(),])
ps_chi.setUpperGdaLimits([chi.getUpperInnerLimit(),])
ps_phi.setLowerGdaLimits([phi.getLowerInnerLimit(),])
ps_phi.setUpperGdaLimits([phi.getUpperInnerLimit(),])

u.limitsComponent.setInternalLower([x.getLowerInnerLimit() - AXES_ZERO[0],])
u.limitsComponent.setInternalUpper([x.getUpperInnerLimit() - AXES_ZERO[0],])
v.limitsComponent.setInternalLower([y.getLowerInnerLimit() - AXES_ZERO[1],])
v.limitsComponent.setInternalUpper([y.getUpperInnerLimit() - AXES_ZERO[1],])
w.limitsComponent.setInternalLower([z.getLowerInnerLimit() - AXES_ZERO[2],])
w.limitsComponent.setInternalUpper([z.getUpperInnerLimit() - AXES_ZERO[2],])
ps_chi.limitsComponent.setInternalLower([chi.getLowerInnerLimit(),])
ps_chi.limitsComponent.setInternalUpper([chi.getUpperInnerLimit(),])
ps_phi.limitsComponent.setInternalLower([phi.getLowerInnerLimit(),])
ps_phi.limitsComponent.setInternalUpper([phi.getUpperInnerLimit(),])

# a scannable group that sends its members' positions to the observer, not the change code from its observable
class ScannableGroupWithUpdateMethodOverride(ScannableGroup):
    def update(self, theobserved, changecode):  # @UnusedVariable
        if theobserved == tp.xyz_group:
            self.notifyIObservers(self, self.getPosition())
            
uvw = ScannableGroupWithUpdateMethodOverride('uvw', (u, v, w))
# make uvw group watching real hardware axes changes
tp.xyz_group.addIObserver(uvw)

