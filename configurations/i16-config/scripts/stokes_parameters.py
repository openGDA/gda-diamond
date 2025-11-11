
from gda.device.scannable import ScannableMotionBase
import scisoftpy as dnp

"----------------------------------------------------------------------------------------------------------------------"
"----------------------------------------------- Stokes Parameters ----------------------------------------------------"
"----------------------------------------------------------------------------------------------------------------------"


class StokesParameters(ScannableMotionBase):
    """
    Define Stokes Parameters of incident beam

    The Stokes parameters are four components labelled I,Q,U,V or p0, p1, p2, p3

    I (S_0) is the beam intensity (often normalized to 1).
    Q (S_1) is linearly polarized along the x axis (Q > 0) or y axis (Q < 0).
    U (S_2) is linearly polarized along the x==y axis (U > 0) or the -x==y axis (U < 0).
    V (S_3) is circularly polarized. V > 0 when the electric field vector rotates clockwise
               at the sample with respect to time when observed from the source;
               V < 0 indicates the opposite rotation.

    Usage:
        stokes_pars = StokesParameters('stokes_pars')
        pos stokes_pars [1, 1, 0, 0]  # linear horizontal
        pos stokes_pars [1, -1, 0, 0]  # linear vertical
        pos stokes_pars [1, 0, 1, 0]  # Linearly polarized (+45Deg)
        pos stokes_pars [1, 0, -1, 0]  # Linearly polarized (-45Deg)
        pos stokes_pars [1, 0, 0, 1]  # circular right
        pos stokes_pars [1, 0, 0, -1]  # circular left
    """

    def __init__(self, name):
        self.setName(name)
        self.setInputNames(["stokes_parameters"])  # 22/11/2024 by DP I16-839
        self.setExtraNames([])
        self.setOutputFormat(['%.4f'])
        self.setLevel(3)
        self.p0 = 1.
        self.p1 = 1.
        self.p2 = 0.
        self.p3 = 0

    def getPosition(self):
        return [[self.p0, self.p1, self.p2, self.p3]]

    def isBusy(self):
        return 0

    def asynchronousMoveTo(self, stokes_parameters):
        self.p0, self.p1, self.p2, self.p3 = stokes_parameters

    def setStokes(self, phi=0, chi=0):
        """
        set Stokes parameters from phi=pol rotation, chi=pol chirality
        phi  chi  p1 p2 p3
        0    0    1  0  0  linear horizontal
        45   0    0  1  0  linear 45 deg
        90   0    -1 0  0  linear vertical
        0   45    0  0  1  circular right
        0   135   0  0 -1  circular left
        """
        phi = dnp.deg2rad(phi)
        chi = dnp.deg2rad(chi)
        self.p1 = dnp.cos(2 * phi) * dnp.cos(2 * chi)
        self.p2 = dnp.sin(2 * phi) * dnp.cos(2 * chi)
        self.p3 = dnp.sin(2 * chi)

    def polarisation_density_matrix(self):
        """Polarisation Density Matrix using Stokes parameters"""
        p1, p2, p3 = self.p1, self.p2, self.p3
        return dnp.array([[p1/2. + 1/2., p2/2. - 1J*p3/2.], [p2/2. + 1J*p3/2., 1/2. - p1/2.]])

stokes_pars = StokesParameters("stokes_pars")
