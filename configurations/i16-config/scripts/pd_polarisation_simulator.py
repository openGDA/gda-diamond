"""
Polarisation Simulation scannable devices

Based on Steve's code:
/dls_sw/i16/scripts/Users/steve/pol_scannable_test_2.py

Instantiation:
moment = CrystalMagneticMoment('moment', hkl)
stokes_pars = StokesParameters('stokes_pars')
pa_jones = AnalyserJonesMatrix('jones_analyser', stokes, pa_crystal, stokes_pars)
charge_scattering = SampleCharge('charge_scattering', moment, stokes_pars, pa_jones)
magE1E1_scattering = SampleMagE1E1('magE1E1_scattering', moment, stokes_pars, pa_jones)
magSpin_scattering = SampleMagSpin('magSpin_scattering', moment, stokes_pars, pa_jones)

Usage:
  pos moment [0, 0, 3]  # moment of 3ub along c-axis
  mu, mv, mw, mx, my, mz = moment()  # returns moment in crystal and lab axes
  pos stokes_pars [1, 1, 0, 0]  # define incident beam Stokes parameters P0,P1,P2,P3
  j_00, j_01, j_10, j_11, Isim = pa_jones()  # uses current analyser position
  j_00, j_01, j_10, j_11, Itot, Iana = charge_scattering()
  j_00, j_01, j_10, j_11, Itot, Iana = magE1E1_scattering()
  j_00, j_01, j_10, j_11, Itot, Iana = magSpin_scattering()

Simulation:
  con gam 0 mu 0 psi 0
  pos moment [2, 0, 0]
  pos stokes_pars [1, 1, 0, 0]
  pos pol 90
  scan psic -180 180 10 hkl [0,0,6] magE1E1_scattering
  pos psic 0
  pos hkl [0,0,6]
  scan pol -180 180 10 magE1E1_scattering

By Dan Porter, BLI16
October 2023
"""

from gda.device.scannable import ScannableMotionBase
import scisoftpy as dnp


"----------------------------------------------------------------------------------------------------------------------"
"----------------------------------------------- General Functions ----------------------------------------------------"
"----------------------------------------------------------------------------------------------------------------------"


def trace2(array2):
    """trace of 2x2 array"""
    return (array2[0, 0] + array2[1, 1])


def dot(A, B):
    """dot product for complex arrays, dnp.dot method fails with complex arrays"""
    Ar, Aim, Br, Bim = dnp.real(A), dnp.imag(A), dnp.real(B), dnp.imag(B)
    return dnp.dot(Ar, Br) - dnp.dot(Aim, Bim) + 1.J * dnp.dot(Ar, Bim) + 1.J * dnp.dot(Aim, Br)


def spin_scattering_vector(q, q1, e, e1):
    """spin scattering vector"""
    e1xe = dnp.cross(e1, e)
    q1xe1 = dnp.cross(q1, e1)
    qxe = dnp.cross(q, e)
    return e1xe + q1xe1*dnp.dot(q1, e) - qxe*dnp.dot(q, e1) - dnp.cross(q1xe1, qxe)


def delta_gamma_rotation(delta, gamma):
    """Rotation matrix for detector arm"""
    dr = dnp.deg2rad(delta)
    gr = dnp.deg2rad(gamma)
    cd = dnp.cos(dr)
    sd = dnp.sin(dr)
    cg = dnp.cos(gr)
    sg = dnp.sin(gr)
    r = dnp.array([
        [cg, -sd*sg, sg*cd],
        [0., cd, sd],
        [-sg, -sd*cg, cd*cg]
    ])
    return r


def rotmatrix_diffractometer(phi, chi, eta, mu):
    """
    an intrinsic rotation using You et al. 4S+2D diffractometer
        mu right-handed rotation about x
        eta left-handed rotation about z'
        chi right-handed rotation about y''
        phi left-handed rotation about z'''
        Angles in degrees
      Z = MU.ETA.CHI.PHI
      V' = Z.V || rot_vec = np.dot(r, vec)
    :param phi: float left-handed rotation about z''' angle in degrees
    :param chi: float right-handed rotation about y'' angle in degrees
    :param eta: float left-handed rotation about z' angle in degrees
    :param mu: float right-handed rotation about x angle in degrees
    :return: [3*3] array
    """
    phi = dnp.deg2rad(phi)
    chi = dnp.deg2rad(chi)
    eta = dnp.deg2rad(eta)
    mu = dnp.deg2rad(mu)
    cp = dnp.cos(phi)
    sp = dnp.sin(phi)
    cc = dnp.cos(chi)
    sc = dnp.sin(chi)
    ce = dnp.cos(eta)
    se = dnp.sin(eta)
    cm = dnp.cos(mu)
    sm = dnp.sin(mu)
    r = dnp.array([
        [
            ce * cp * cc - se * sp,
            ce * sp * cc + se * cp,
            ce * sc
        ],
        [
            sm * cp * sc + cm * (-se * cp * cc - ce * sp),
            sm * sp * sc + cm * (ce * cp - se * sp * cc),
            -se * cm * sc - sm * cc
        ],
        [
            sm * (-se * cp * cc - ce * sp) - cm * cp * sc,
            sm * (ce * cp - se * sp * cc) - cm * sp * sc,
            cm * cc - se * sm * sc
        ]
    ])
    return r


def jones_analyser(stokes, tthp):
    """
    Returns the 2x2 Jones matrix for the polarisation analyser
    works only in vertical geometry
    """
    xi = dnp.deg2rad(stokes)
    tthp = dnp.deg2rad(tthp)
    return dnp.array([[dnp.cos(xi), -dnp.sin(xi)], [dnp.sin(xi)*dnp.cos(tthp), dnp.cos(tthp)*dnp.cos(xi)]])


"----------------------------------------------------------------------------------------------------------------------"
"----------------------------------------------- Magnetic Moment ------------------------------------------------------"
"----------------------------------------------------------------------------------------------------------------------"


class CrystalMagneticMoment(ScannableMotionBase):
    """
    Define magnetic moment in crystal axes
    Add moment in units of sample unit vectors (ua, vb, wc), returns moment in lab coordinates
    Uses either current or simulated positions from diffcalc hkl class
    When a hkl position is given, simulated angles using the current DiffCalc constraints
    will be used.

    Usage:
        moment = CrystalMagneticMoment('moment', hkl)
        pos moment [0, 0, 3]  # moment of 3ub along c-axis
        mu, mv, mw, mx, my, mz = moment()  # returns moment in crystal and lab axes
        sim moment [h, k, l]  # simulate moment coorinates at hkl position
        mx, my, mz = moment.get_moment_in_lab_basis(new_hkl, energy_kev)
        mh, mk, ml = moment.get_moment_in_wavevector_basis()
        m_pi, m_sig, m_q = moment.get_moment_in_scattering_basis(new_hkl, energy_kev)
        moment.add_scatteringplane_moment(m_pi, m_sigma, m_q) # define moment in scattering plane coordinates
        moment.add_wavevector_moment(mh, mk, ml) # define moment in hkl coordinates
        moment.add_lab_moment(mx, my, mz)  # define moment in lab coordinates


    ---Coordinate systems---
              (mu, mv, mw)   vector along crystal basis vectors (a,b,c)=inv(Bmatrix),
                             in units of Bohr magneton.
              (mh, mk, ml)   vector along reciprocal basis vectors (a*,b*,c*) = Bmatrix.T
                             in units of Bohr magneton.
        (m_pi, m_sig, m_q)   vector in scattering plane coordinates (See Busing, Hill et al.)
                             where m_q is along Q=ki-kf, m_pi is along ki_kf, m_sig is normal
                             to the scattering plane.
              (mx, my, mz)   vector in lab coordinates where z is along beam direction,
                             y is towards ceiling and x is horizontal (away from ring).
    """

    def __init__(self, name, diffcalc_hkl):
        self.setName(name)
        self.setInputNames(['mu', 'mv', 'mw'])
        self.setExtraNames(['mx', 'my', 'mz'])
        self.setOutputFormat(['%.4f','%.4f','%.4f', '%.4f','%.4f','%.4f'])
        self.setLevel(7)

        self.hkl_obj = diffcalc_hkl
        self.beam_direction = [0, 0, 1]
        self.beam_horizontal = [1, 0, 0]
        self.beam_vertical = [0, 1, 0]

        self.mu, self.mv, self.mw = 0, 0, 1

    " --- Scannable Functions ---"

    def getPosition(self):
        m_u, m_v, m_w = self.mu, self.mv, self.mw
        mx, my, mz = self.get_moment_in_lab_basis()
        return m_u, m_v, m_w, mx, my, mz

    def asynchronousMoveTo(self, new_moment):
        self.add_sample_moment(*new_moment)

    def isBusy(self):
        return 0

    def simulateMoveTo(self, new_hkl, energy_kev=None):
        """simulate motion at a paritcular hkl position, works with sim moment [h,k,l]"""
        m_pi, m_sig, m_q = self.get_moment_in_scattering_basis(new_hkl, energy_kev)
        mx, my, mz = self.get_moment_in_lab_basis(new_hkl, energy_kev)
        mh, mk, ml = self.get_moment_in_wavevector_basis()
        euler = self.get_euler(new_hkl, energy_kev)
        if energy_kev is None:
            energy_kev = self.hkl_obj._diffcalc.settings.hardware.get_energy()
        print('Reflection (hkl) = (%.3g,%.3g,%.3g) at E=%.4g keV' % (new_hkl[0], new_hkl[1], new_hkl[2], energy_kev))
        print('Euler: phi: %.2f, chi: %.2f, eta: %.2f, mu: %.2f, delta: %.2f, gam: %.2f' % euler)
        print("    Moment in sample basis: (mu,mv,mw)=(%.3f,%.3f,%.3f)" % (self.mu, self.mv, self.mw))
        print("       Moment in hkl basis: (mh,mk,ml)=(%.3f,%.3f,%.3f)" % (mh, mk, ml))
        print("Moment in scattering plane: (u1,u2,u3)=(%.3f,%.3f,%.3f)" % (m_pi, m_sig, m_q))
        print("       Moment in lab space: (mx,my,mz)=(%.3f,%.3f,%.3f)" % (mx, my, mz))
        return self.mu, self.mv, self.mw, mx, my, mz

    " --- calculation functions --- "

    def get_euler(self, new_hkl=None, energy_kev=None):
        """Return current diffractometer positions - phi, chi, eta, mu, delta, gamma"""
        if new_hkl is None:
            my_euler = self.hkl_obj.diffhw()
        else:
            _h, _k, _l = new_hkl
            my_euler, params = self.hkl_obj._diffcalc.hkl_to_angles(_h, _k, _l, energy_kev)
        return my_euler

    def get_sample_r_matrix(self, new_hkl=None, energy_kev=None):
        """Return diffractometer rotation matrix for current or simulated hkl position"""
        myphi, mychi, myeta, mymu, mydelta, mygamma = self.get_euler(new_hkl, energy_kev)
        return rotmatrix_diffractometer(myphi, mychi, myeta, mymu)

    def get_detector_r_matrix(self, new_hkl=None, energy_kev=None):
        """Returns rotation matrix for the detector"""
        myphi, mychi, myeta, mymu, mydelta, mygamma = self.get_euler(new_hkl, energy_kev)
        return delta_gamma_rotation(mydelta, mygamma)

    def get_delta_gamma_radians(self, new_hkl=None, energy_kev=None):
        """Returns delta and gamma in radians"""
        myphi, mychi, myeta, mymu, mydelta, mygamma = self.get_euler(new_hkl, energy_kev)
        return dnp.deg2rad(mydelta), dnp.deg2rad(mygamma)

    def scattered_vector(self, new_hkl=None, energy_kev=None):
        """Returns the scattered beam vector, kf"""
        r = self.get_detector_r_matrix(new_hkl, energy_kev)
        return dnp.dot(r, self.beam_direction)

    def get_UB(self):
        """Return current diffcalc UB matrix"""
        return dnp.array(self.hkl_obj._diffcalc._ub.ubcalc.UB.tolist())

    def get_lab_matrix(self):
        """Returns transformation matrix between diffractometer reference frame and I16 lab frame"""
        return dnp.array([self.beam_direction, self.beam_horizontal, self.beam_vertical])

    def get_scattering_plane_basis(self, new_hkl=None, energy_kev=None):
        """Return basis vectors U1, U2, U3"""
        ki = self.beam_direction
        kf = self.scattered_vector(new_hkl=None, energy_kev=None)

        U3 = (ki - kf) / dnp.linalg.norm(ki - kf)  # z-z1 = ki - kf = -q
        U1 = (kf + kf) / dnp.linalg.norm(ki + kf)  # vector parallel to the scattering plane, perp. to U3
        U2 = dnp.cross(U3, U1)
        return U1, U2, U3

    " --- moment coordinate conversions ---"

    def get_moment_in_lab_basis(self, new_hkl=None, energy_kev=None):
        """Returns moment vector in coordinate system of i16 lab, in Bohr Magnetons"""
        ub_matrix = self.get_UB()
        r_matrix = self.get_sample_r_matrix(new_hkl, energy_kev)
        lab_matrix = self.get_lab_matrix()
        ub_rl_matrix = dnp.dot(lab_matrix, dnp.dot(r_matrix, ub_matrix))

        moment = [self.mu, self.mv, self.mw]
        momentmag = dnp.linalg.norm(moment)
        momentxyz = dnp.dot(moment, dnp.linalg.inv(ub_rl_matrix))
        momentxyz = momentmag * momentxyz / dnp.linalg.norm(momentxyz)
        momentxyz[dnp.isnan(moment)] = 0.
        return momentxyz

    def get_moment_in_scattering_basis(self, new_hkl=None, energy_kev=None):
        """Return moment vector in coordinate system of the scattering plane (Z||Q) [unitless]"""
        u1u2u3 = self.get_scattering_plane_basis(new_hkl, energy_kev)
        mxmymz = self.get_moment_in_lab_basis(new_hkl, energy_kev)
        scat_mom = dnp.dot(mxmymz, dnp.linalg.inv(u1u2u3))
        return scat_mom / dnp.linalg.norm(scat_mom)

    def get_moment_in_wavevector_basis(self, mxmymz=None):
        """Return moment vector in coordinate system of the reciprocal lattice, in Bohr Magnetons"""
        if mxmymz is None:
            mxmymz = self.get_moment_in_lab_basis()
        moment_mag = dnp.linalg.norm(mxmymz)
        ub_matrix = self.get_UB()
        r_matrix = self.get_sample_r_matrix()
        lab_matrix = self.get_lab_matrix()
        ub_rl_matrix = dnp.dot(lab_matrix, dnp.dot(r_matrix, ub_matrix))
        mhmkml = dnp.dot(ub_rl_matrix, mxmymz)
        return moment_mag * mhmkml / dnp.linalg.norm(mhmkml)

    def get_moment_in_crystal_basis(self, mxmymz):
        """Return moment vector in coordinate system of the crystal, in Bohr Magnetons"""
        moment_mag = dnp.linalg.norm(mxmymz)
        ub_matrix = self.get_UB()
        r_matrix = self.get_sample_r_matrix()
        lab_matrix = self.get_lab_matrix()
        ub_rl_matrix = dnp.dot(lab_matrix, dnp.dot(r_matrix, ub_matrix))
        mumvmw = dnp.dot(mxmymz, ub_rl_matrix)
        return moment_mag * mumvmw / dnp.linalg.norm(mumvmw)

    def get_magnitude(self):
        """Returns the magnitude of the magnetic moment, in Bohr Magnetons"""
        return dnp.linalg.norm([self.mu, self.mv, self.mw])

    def add_sample_moment(self, mu, mv, mw):
        """
        Define the magnetic moment in crystal coordinates a,b,c = inv(B)
        """
        self.mu, self.mv, self.mw = mu, mv, mw

    def add_lab_moment(self, mx, my, mz):
        """
        Define the magnetic moment in lab coordinates X,Y,Z, where Z is along the beam, X is horizontal (away from ring)
        """
        self.mu, self.mv, self.mw = self.get_moment_in_crystal_basis([mx,my,mz])

    def add_scatteringplane_moment(self, m_pi, m_sigma, m_q):
        """
        Define the magnetic moment in scattering plane coordinates U1,U2,U3, where U3=ki-kf, U1=ki+kf, U2=U3xU1
        """
        U1, U2, U3 = self.get_scattering_plane_basis()
        mxmymz = m_pi * U1 + m_sigma * U2 + m_q * U3  # moment in lab coordinates
        self.mu, self.mv, self.mw = self.get_moment_in_crystal_basis(mxmymz)

    def add_wavevector_moment(self, mh, mk, ml):
        """
        Define the magnetic moment in hkl coordinates
        """
        # convert to lab coordinates
        moment_mag = dnp.linalg.norm([mh, mk, ml])
        ub_matrix = self.get_UB()
        r_matrix = self.get_sample_r_matrix()
        lab_matrix = self.get_lab_matrix()
        ub_rl_matrix = dnp.dot(lab_matrix, dnp.dot(r_matrix, ub_matrix))
        mxmymz = dnp.dot(ub_rl_matrix, [mh, mk, ml])
        return moment_mag * mxmymz / dnp.linalg.norm(mxmymz)

    " --- matrices --- "

    def linear_polarisations(self, new_hkl=None, energy_kev=None):
        """Returns matrix of linear polarisations [[sigma-sigma, pi-sigma], [sigma-pi, pi-pi]]"""
        r = self.get_detector_r_matrix(new_hkl, energy_kev)
        ki = self.beam_direction
        kf = dnp.dot(r, ki)
        sigma = self.beam_horizontal
        sigma_ = dnp.dot(r, sigma)
        pi = self.beam_vertical
        pi_ = dnp.dot(r, pi)

        pol = dnp.array([
            [
                spin_scattering_vector(ki, kf, sigma, sigma_),
                spin_scattering_vector(ki, kf, pi, sigma_)
            ],
            [
                spin_scattering_vector(ki, kf, sigma, pi_),
                spin_scattering_vector(ki, kf, pi, pi_)
            ]
        ])
        return pol

    def jones_magE1E1(self, new_hkl=None, energy_kev=None):
        """Returns Jones 2x2 polarisation matrix for resonant magnetic E1E1 scattering"""
        dr, gr = self.get_delta_gamma_radians(new_hkl, energy_kev)
        mx, my, mz = self.get_moment_in_lab_basis(new_hkl, energy_kev)
        j = dnp.array([
            [
                -my * dnp.sin(gr),
                 mx * dnp.sin(gr) + mz * dnp.cos(gr)
            ],
            [
                -my * dnp.sin(dr) * dnp.cos(gr) - mz * dnp.cos(dr),
                 mx * dnp.sin(dr) * dnp.cos(gr) - mz * dnp.sin(dr)*dnp.sin(gr)
            ]
        ])
        return j

    def jones_magSpin(self, new_hkl=None, energy_kev=None):
        """Returns Jones 2x2 polarisation matrix for non-resonant magnetic scattering"""
        moment = self.get_moment_in_lab_basis(new_hkl, energy_kev)
        pol = self.linear_polarisations(new_hkl, energy_kev)

        j = dnp.array([
            [dnp.dot(moment, pol[0, 0]), dnp.dot(moment, pol[0, 1])],
            [dnp.dot(moment, pol[1, 0]), dnp.dot(moment, pol[1, 1])]
        ])
        return j


class ScatteringMagneticMoment(CrystalMagneticMoment):
    """
    Define magnetic moment in crystal axes
    Add moment in units of sample unit vectors (ua, vb, wc), returns moment in lab coordinates
    Uses either current or simulated positions from diffcalc hkl class
    When a hkl position is given, simulated angles using the current DiffCalc constraints
    will be used.

    Usage:
        moment = ScatteringMagneticMoment('moment', hkl)
        pos moment [0, 0, 3]  # moment of 3ub along c-axis
        mu, mv, mw, mx, my, mz = moment()  # returns moment in crystal and lab axes
        sim moment [h, k, l]  # simulate moment coorinates at hkl position
        mx, my, mz = moment.get_moment_in_lab_basis(new_hkl, energy_kev)
        m_pi, m_sig, m_q = moment.get_moment_in_scattering_basis(new_hkl, energy_kev)
        moment.add_wavevector_moment(m_pi, m_sigma, m_q)


    ---Coordinate systems---
    Crystal system
              (mu, mv, mw)   vector along crystal basis vectors (a,b,c)=inv(Bmatrix),
                             in units of Bohr magneton.
        (m_pi, m_sig, m_q)   vector in scattering plane coordinates (See Busing, Hill et al.)
                             where m_q is along Q=ki-kf, m_pi is along ki_kf, m_sig is normal
                             to the scattering plane.
              (mx, my, mz)   vector in lab coordinates where z is along beam direction,
                             y is towards ceiling and x is horizontal (away from ring).
    """

    def __init__(self, name, diffcalc_hkl):
        self.setName(name)
        self.setInputNames(['m_u1', 'm_u2', 'm_u3'])
        self.setExtraNames(['mx', 'my', 'mz'])
        self.setOutputFormat(['%.4f','%.4f','%.4f', '%.4f','%.4f','%.4f'])
        self.setLevel(7)

        self.hkl_obj = diffcalc_hkl
        self.beam_direction = [0, 0, 1]
        self.beam_horizontal = [1, 0, 0]
        self.beam_vertical = [0, 1, 0]

        self.m_u1, self.m_u2, self.m_u3 = 0, 0, 1

    def getPosition(self):
        m_u1, m_u2, m_u3 = self.m_u1, self.m_u2, self.m_u3
        mx, my, mz = self.get_moment_in_lab_basis()
        return m_u, m_v, m_w, mx, my, mz

    def asynchronousMoveTo(self, new_moment):
        self.add_wavevector_moment(*new_moment)

    def isBusy(self):
        return 0

    def simulateMoveTo(self, new_hkl, energy_kev=None):
        """simulate motion at a paritcular hkl position, works with sim moment [h,k,l]"""
        mx, my, mz = self.get_moment_in_lab_basis(new_hkl, energy_kev)
        mu, mv, mw = self.get_moment_in_crystal_basis([mx, my, mz])
        euler = self.get_euler(new_hkl, energy_kev)
        if energy_kev is None:
            energy_kev = self.hkl_obj._diffcalc.settings.hardware.get_energy()
        print('Reflection (hkl) = (%.3g,%.3g,%.3g) at E=%.4g keV' % (new_hkl[0], new_hkl[1], new_hkl[2], energy_kev))
        print('Euler: phi: %.2f, chi: %.2f, eta: %.2f, mu: %.2f, delta: %.2f, gam: %.2f' % euler)
        print("Moment in scattering plane: (u1,u2,u3)=(%.3f,%.3f,%.3f)" % (self.m_u1, self.m_u2, self.m_u3))
        print("Moment in sample basis: (mu,mv,mw)=(%.3f,%.3f,%.3f)" % (self.mu, self.mv, self.mw))
        print("Moment in lab space: (mx,my,mz)=(%.3f,%.3f,%.3f)" % (mx, my, mz))
        return self.m_u1, self.m_u2, self.m_u3, mx, my, mz

    def get_moment_in_lab_basis(self, new_hkl=None, energy_kev=None):
        """Returns moment vector in coordinate system of i16 lab, in Bohr Magnetons"""
        U1, U2, U3 = self.get_scattering_plane_basis(new_hkl, energy_kev)
        return self.m_u1 * U1 + self.m_u2 * U2 + self.m_u3 * U3

    def get_moment_in_scattering_basis(self, new_hkl=None, energy_kev=None):
        """Return moment vector in coordinate system of the scattering plane (Z||Q) [unitless]"""
        u1u2u3 = self.get_scattering_plane_basis(new_hkl, energy_kev)
        mxmymz = self.get_moment_in_lab_basis(new_hkl, energy_kev)
        scat_mom = dnp.dot(mxmymz, dnp.linalg.inv(u1u2u3))
        return scat_mom / dnp.linalg.norm(scat_mom)

    def get_magnitude(self):
        """Returns the magnitude of the magnetic moment, in Bohr Magnetons"""
        return dnp.linalg.norm([self.m_u1, self.m_u2, self.m_u3])

    def add_sample_moment(self, mu, mv, mw):
        """
        Add sample moment in coordinates a,b,c = inv(B)
        """
        ub_matrix = self.get_UB()
        r_matrix = self.get_sample_r_matrix()
        lab_matrix = self.get_lab_matrix()
        ub_rl_matrix = dnp.dot(lab_matrix, dnp.dot(r_matrix, ub_matrix))

        moment = [mu, mv, mw]
        momentmag = dnp.linalg.norm(moment)
        mxmymz = dnp.dot(moment, dnp.linalg.inv(ub_rl_matrix))

        u1u2u3 = self.get_scattering_plane_basis()
        scat_mom = dnp.dot(mxmymz, dnp.linalg.inv(u1u2u3))
        scat_mom = momentmag * scat_mom / dnp.linalg.norm(scat_mom)
        self.m_u1, self.m_u2, self.m_u3 = scat_mom

    def add_wavevector_moment(self, m_pi, m_sigma, m_q):
        """
        Return the magnetic moment in the reference frame of the scattering plane (z || q=ki-kf, y perp. beam)
        :returns (x,y,z) direction of magnetic moment in scattering plane basis
        """
        self.m_u1, self.m_u2, self.m_u3 = m_pi, m_sigma, m_q

    def linear_polarisations(self, new_hkl=None, energy_kev=None):
        """Returns matrix of linear polarisations [[sigma-sigma, pi-sigma], [sigma-pi, pi-pi]]"""
        r = self.get_detector_r_matrix(new_hkl, energy_kev)
        ki = self.beam_direction
        kf = dnp.dot(r, ki)
        sigma = self.beam_horizontal
        sigma_ = dnp.dot(r, sigma)
        pi = self.beam_vertical
        pi_ = dnp.dot(r, pi)

        pol = dnp.array([
            [
                spin_scattering_vector(ki, kf, sigma, sigma_),
                spin_scattering_vector(ki, kf, pi, sigma_)
            ],
            [
                spin_scattering_vector(ki, kf, sigma, pi_),
                spin_scattering_vector(ki, kf, pi, pi_)
            ]
        ])
        return pol

    def jones_magE1E1(self, new_hkl=None, energy_kev=None):
        """Returns Jones 2x2 polarisation matrix for resonant magnetic E1E1 scattering"""
        dr, gr = self.get_delta_gamma_radians(new_hkl, energy_kev)
        mx, my, mz = self.get_moment_in_lab_basis(new_hkl, energy_kev)
        j = dnp.array([
            [
                -my * dnp.sin(gr),
                 mx * dnp.sin(gr) + mz * dnp.cos(gr)
            ],
            [
                -my * dnp.sin(dr) * dnp.cos(gr) - mz * dnp.cos(dr),
                 mx * dnp.sin(dr) * dnp.cos(gr) - mz * dnp.sin(dr)*dnp.sin(gr)
            ]
        ])
        return j

    def jones_magSpin(self, new_hkl=None, energy_kev=None):
        """Returns Jones 2x2 polarisation matrix for non-resonant magnetic scattering"""
        moment = self.get_moment_in_lab_basis(new_hkl, energy_kev)
        pol = self.linear_polarisations(new_hkl, energy_kev)

        j = dnp.array([
            [dnp.dot(moment, pol[0, 0]), dnp.dot(moment, pol[0, 1])],
            [dnp.dot(moment, pol[1, 0]), dnp.dot(moment, pol[1, 1])]
        ])
        return j


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


"----------------------------------------------------------------------------------------------------------------------"
"------------------------------------------ Jones Matrix - Analyser ---------------------------------------------------"
"----------------------------------------------------------------------------------------------------------------------"


class AnalyserJonesMatrix(ScannableMotionBase):
    """
    Jones Matrix for Analyser crystal

    Usage:
      pa_jones = AnalyserJonesMatrix('jones_analyser', stokes, pa_crystal, stokes_pars)
      J00, J01, J10, J11, Isim = pa_jones()
      J = pa_jones.get_jones(stokes_angle, energy_kev=None)
      Isim = pa_jones.get_analyser_intensity(stokes_angle, energy_kev=None)

    Simulation:
      scan pol -180 180 10 pa_jones
    """

    def __init__(self, name, pd_stokes_motor, pd_analyser_crystal, pd_stokes_params):
        self.setName(name)
        self.setInputNames([])
        self.setExtraNames(['J00', 'J01', 'J10', 'J11', 'Isim'])
        self.setOutputFormat(['%.4f','%.4f','%.4f','%.4f', '%.4f'])
        self.setLevel(3)

        self.pd_stokes_motor = pd_stokes_motor
        self._pa_crystal = pd_analyser_crystal
        self.pd_stokes_params = pd_stokes_params

    def get_jones(self, stokes_angle=None, energy_kev=None):
        """Return Jones 2x2 polarisation matrix as array"""
        if stokes_angle is None:
            stokes_angle = self.pd_stokes_motor()
        return self._pa_crystal.calcJones(stokes_angle, energy_kev)

    def get_analyser_intensity(self, stokes_angle=None, energy_kev=None):
        """Simulate analyser intensity"""
        mu = self.pd_stokes_params.polarisation_density_matrix()
        jones = self.get_jones(stokes_angle, energy_kev)  # Jones matrix of sample
        intensity = trace2(dnp.dot( jones, dnp.dot(mu, dnp.conjugate(jones).T)))
        return float(dnp.real(intensity))

    def isBusy(self):
        return 0

    def getPosition(self):
        j = self.get_jones()
        intensity = self.get_analyser_intensity()
        return j[0, 0], j[0, 1], j[1, 0], j[1, 1], intensity

    def simulateMoveTo(self, stokes_angle=None, energy_kev=None):
        j = self.get_jones(stokes_angle, enegy_kev)
        intensity = self.get_analyser_intensity(stokes_angle, enegy_kev)
        return j[0, 0], j[0, 1], j[1, 0], j[1, 1], intensity


"----------------------------------------------------------------------------------------------------------------------"
"------------------------------------------- Jones Matrix - Sample ----------------------------------------------------"
"----------------------------------------------------------------------------------------------------------------------"


class SampleCharge(ScannableMotionBase):
    """
    Jones Matrix for Sample charge scattering
    Returns 2x2 polarisation Jones matrix and simulted intensity before and after analyser

    Usage:
      charge_scattering = SampleCharge('charge_scattering', sample_moment, stokes_pars, pa_jones)
      J00, J01, J10, J11, Itot, Iana = charge_scattering()
      J = charge_scattering.get_jones(hkl, energy_kev=None)
      Itot = charge_scattering.get_total_intensity(hkl, enegy_kev=None)
      Iana = charge_scattering.get_analysed_intensity(hkl, enegy_kev=None)

    Simulation:
      con gam 0 mu o psi 0
      pos moment [2, 0, 0]
      pos stokes_pars [1, 0, 0]
      pos pol 90
      scan psic -180 180 10 hkl [0,0,6] charge_scattering
      pos psic 0
      pos hkl [0,0,6]
      scan pol -180 180 10 charge_scattering
    """

    def __init__(self, name, pd_moment, pd_stokes_params, pd_analyser_jones):
        self.setName(name)
        self.setInputNames([])
        self.setExtraNames(['J00', 'J01', 'J10', 'J11', 'Isim', 'Ipol'])
        self.setOutputFormat(['%.4f','%.4f','%.4f','%.4f', '%.4f', '%.4f'])
        self.setLevel(3)

        self.pd_moment = pd_moment  # contains delta, gamma
        self.pd_stokes_params = pd_stokes_params
        self.pd_analyser_jones = pd_analyser_jones

    def get_jones(self, new_hkl=None, energy_kev=None):
        """Return Jones 2x2 polarisation matrix as array"""
        dr, gr = self.pd_moment.get_delta_gamma_radians(new_hkl, energy_kev)
        return dnp.array([[dnp.cos(gr), 0], [-dnp.sin(dr)*dnp.sin(gr), dnp.cos(dr)]])

    def get_total_intensity(self, new_hkl=None, energy_kev=None):
        """Simulate total (without analyser) intensity from sample in charge scattering condition"""
        mu = self.pd_stokes_params.polarisation_density_matrix()
        jones = self.get_jones(new_hkl, energy_kev)  # Jones matrix of sample
        intensity = trace2(dnp.dot( jones, dnp.dot(mu, dnp.conjugate(jones).T)))
        return float(dnp.real(intensity))

    def get_analysed_intensity(self, new_hkl=None, energy_kev=None):
        """Simulate intensity after analyser in charge scattering condition"""
        mu = self.pd_stokes_params.polarisation_density_matrix()
        jones_analyser = self.pd_analyser_jones.get_jones()  # Jones matrix of analyser
        jones = self.get_jones(new_hkl, energy_kev)  # Jones matrix of sample
        intensity = trace2(
            dnp.dot(jones_analyser,
                   dnp.dot(jones, dnp.dot(mu,
                                        dnp.dot(dnp.conjugate(jones).T, dnp.conjugate(jones_analyser).T))
                         )
                  )
        )
        return float(dnp.real(intensity))

    def isBusy(self):
        return 0

    def getPosition(self):
        j = self.get_jones()
        itot = self.get_total_intensity()
        iana = self.get_analysed_intensity()
        return j[0, 0], j[0, 1], j[1, 0], j[1, 1], itot, iana

    def simulateMoveTo(self, new_hkl, energy_kev=None):
        j = self.get_jones(new_hkl, energy_kev)
        itot = self.get_total_intensity(new_hkl, energy_kev)
        iana = self.get_analysed_intensity(new_hkl, energy_kev)
        return j[0, 0], j[0, 1], j[1, 0], j[1, 1], itot, iana


class SampleMagE1E1(SampleCharge):
    """
    Jones Matrix for Sample magnetic E1E1 resonant scattering
    Returns 2x2 polarisation Jones matrix and simulted intensity before and after analyser

    Usage:
      magE1E1_scattering = SampleCharge('magE1E1_scattering', sample_moment, stokes_pars, pa_jones)
      J00, J01, J10, J11, Itot, Iana = magE1E1_scattering()
      J = magE1E1_scattering.get_jones(hkl, energy_kev=None)
      Itot = magE1E1_scattering.get_total_intensity(hkl, enegy_kev=None)
      Iana = magE1E1_scattering.get_analysed_intensity(hkl, enegy_kev=None)

    Simulation:
      con gam 0 mu o psi 0
      pos moment [2, 0, 0]
      pos stokes_pars [1, 0, 0]
      pos pol 90
      scan psic -180 180 10 hkl [0,0,6] magE1E1_scattering
      pos psic 0
      pos hkl [0,0,6]
      scan pol -180 180 10 magE1E1_scattering
    """

    def get_jones(self, new_hkl=None, energy_kev=None):
        """Return Jones 2x2 polarisation matrix for magnetic E1E1 resonant scattering, as array"""
        return self.pd_moment.jones_magE1E1(new_hkl, energy_kev)


class SampleMagSpin(SampleCharge):
    """
    Jones Matrix for Sample magnetic non-resonant scattering
    Returns 2x2 polarisation Jones matrix and simulted intensity before and after analyser

    Usage:
      magSpin_scattering = SampleCharge('magSpin_scattering', sample_moment, stokes_pars, pa_jones)
      J00, J01, J10, J11, Itot, Iana = magSpin_scattering()
      J = magSpin_scattering.get_jones(hkl, energy_kev=None)
      Itot = magSpin_scattering.get_total_intensity(hkl, enegy_kev=None)
      Iana = magSpin_scattering.get_analysed_intensity(hkl, enegy_kev=None)

    Simulation:
      con gam 0 mu o psi 0
      pos moment [2, 0, 0]
      pos stokes_pars [1, 0, 0]
      pos pol 90
      scan psic -180 180 10 hkl [0,0,6] magSpin_scattering
      pos psic 0
      pos hkl [0,0,6]
      scan pol -180 180 10 magSpin_scattering
    """

    def get_jones(self, new_hkl=None, energy_kev=None):
        """Return Jones 2x2 polarisation matrix for magnetic non-resonant scattering, as array"""
        return self.pd_moment.jones_magSpin(new_hkl, energy_kev)



"""
if '__main__' in __name__:
    sample_moment = MagneticMoment('sample_moment', delta, gam, None)
    stokes_pars = StokesParameters('stokes_pars')
    pa_jones = AnalyserJonesMatrix('jones_analyser', stokes, pa_crystal, stokes_pars)
    charge_scattering = SampleCharge('charge_scattering', sample_moment, stokes_pars, pa_jones)
    magE1E1_scattering = SampleMagE1E1('magE1E1_scattering', sample_moment, stokes_pars, pa_jones)
    magSpin_scattering = SampleMagSpin('magSpin_scattering', sample_moment, stokes_pars, pa_jones)
"""