"""
New polarisation analyser scannable device

The new device is split into three scannables:
    pa_crystal -> contains analyser crystal and reflection, set name/index, get index, name, dspace, ref_multiplier
    pa_detector -> contains analyser detector choice, set name/index, get index, name, offset_pd, offset_pd, use_mtthp
    pa -> contains offsets, pa_crystal and pa_detector

Instantiation:
    pa_crystal = AnalyserCrystal('pa_crystal', offset_crystal_id, offset_crystal_ref, ANALYSER_DATABASE)
    pa_detector = AnalyserDetector('pa_detector', offset_detector_id, DETECTOR_DATABASE)
    pa_jones = AnalyserJonesMatrix('pa_jones', stokes, pa_crystal)
    pa = PolarisationAnalyser(name, stokes_motor, th_motor, tth_motor, zp_motor, dettrans_motor, mtthp_motor,
        pa_crystal, pa_detector,
        scattering_direction, thp_offset_0, thp_offset_90, tthp_offset_0, tthp_offset_90,
        dettrans_offset_0, dettrans_offset_90, mtthp_offset_0, mtthp_offset_90)

Usage:
    pos pa_crystal 'PG001'  # sets the analyser crystal to graphite
    pos pa_crystal 2  # sets the analyser crystal to Cu111
    pos pa_crystal ['PG001', 6]  # sets analyser crystal to Graphite (006)
    pa_crystal()  # returns id, 'name', ref_order, ref_d-space
    pa_crystal.showCrystals()  # displays available analysers at this energy
    pa_crystal.showAllCrystals()  # displays full list of crystals
    pa_crystal.calcBragg() # returns Bragg angle for current energy
    pa_crystal.calcJones(stokes_angle) # returns Jones polarisation matrix for current energy and rotation

    pos pa_detector 0  # detector set for APD
    pos pa_detector 'merlin'  # detector set for Merlin
    pa_detector()  # returns: id, 'name'
    pa_detector.showDetectors()   # shows list of available detectors




Old scannable device "pol":
/dls_sw/i16/software/gda/config/scripts/pd_polarizationAnalyser_new_alpha.py

By Dan Porter, BLI16
October 2023
"""

from gda.device.scannable import ScannableBase
from mathd import pi, asin, cosd, sind
from scisoftpy import asarray
import beamline_info as BLi


"----------------------------------------------------------------------------------------------------------------------"
"------------------------------------------------- GENERAL FUNCTIONS --------------------------------------------------"
"----------------------------------------------------------------------------------------------------------------------"


def bragg_angle(wl, dspace):
    """Calculate Bragg angle in degrees"""
    if wl / (2 * dspace) > 1:
        return 180.
    return (180 / pi) * asin(wl / (2 * dspace))


def jones_analyser(xi, two_theta):
    """
    Returns the 2x2 Jones matrix for the polarisation analyser
    """
    return asarray([[cosd(xi), -sind(xi)], [sind(xi)*cosd(two_theta), cosd(two_theta)*cosd(xi)]])


"----------------------------------------------------------------------------------------------------------------------"
"---------------------------------------------------- SCANNABLES ------------------------------------------------------"
"----------------------------------------------------------------------------------------------------------------------"


class AnalyserCrystal(ScannableBase):
    """
    Device to set and get polarisation analyser crystal
    Usage:
        pa_crystal = AnalyserCrystal('pa_crystal', offset_crystal_id, offset_crystal_ref, database)
        pos pa_crystal 'PG001'  # sets the analyser crystal to graphite
        pos pa_crystal 2  # sets the analyser crystal to Cu111
        pos pa_crystal ['PG001', 6]  # sets analyser crystal to Graphite (006)
        pa_crystal()  # returns id, 'name', ref_order, ref_d-space
        pa_crystal.showCrystals()  # displays available analysers at this energy
        pa_crystal.showAllCrystals()  # displays full list of crystals
        pa_crystal.calcBragg() # returns Bragg angle for current energy
        pa_crystal.calcJones(stokes_angle) # returns Jones polarisation matrix for current energy and rotation

    database is a list of lists specifiying the available analyser crystals, with entries:
    database = [
                ('name', reflection_d-spacing, reflection_multiplier),
                ('PG001', 6.711, 2),
                ...
               ]
    """

    def __init__(self, name, pd_pa_crystal_index, pd_pa_crystal_ref, analyser_database):
        self.setName(name)
        self.setInputNames(['analyser_id', 'analyser_order'])
        self.setExtraNames(['analyser_name', 'analyser_dspace'])
        self.setOutputFormat(["%.0f", "%.0f", "%s", "%.5f"])
        self.setLevel(5)

        # Offset Scannables to make persistent
        self._pd_index = pd_pa_crystal_index
        self._pd_ref_order = pd_pa_crystal_ref

        # Analyser database
        self._names = [db[0] for db in analyser_database]
        self._dspaces = [db[1] for db in analyser_database]
        self._multipliers = [db[2] for db in analyser_database]

        # Values
        self.crystal_index = 0
        self.crystal_name = ''
        self.order = 1
        self.dspace = 1.0
        self.setAnalyserIndex(self._pd_index(), self._pd_ref_order())

    "---- ScannableMotionBase ----"

    def getPosition(self):
        return [self.crystal_index, self.order, self.crystal_name, self.dspace]

    def isBusy(self):
        return 0

    def asynchronousMoveTo(self, index_name_order):
        """
        2 options:
          MoveTo([4, 2]) - int number, index of crystal, then reflection multiple
          MoveTo(['PG001', 2]) - str, name of crystal, then reflection multiple
        """
        order = int(index_name_order[1])
        name_index = index_name_order[0]

        # str or int
        try:
            self.setAnalyserIndex(int(name_index), order)
        except ValueError:
            self.setAnalyserName(name_index, order)

    "---- Crystal Database ----"

    def getAnalyser(self, name=None, index=0):
        """Returns idx, name, dspace, order if name in dictionary, else return graphite"""
        if name is None:
            idx = int(index)
        elif name in self._names:
            idx = self._names.index(name)
        else:
            # search for name, for example get_analyser('ni') = 'Ni001'
            name = name.lower()
            idx = 0  # return PG001 by default
            for n, analyser_name in enumerate(self._names):
                if name in analyser_name.lower():
                    idx = n
                    break
        return idx, self._names[idx], self._dspaces[idx], self._multipliers[idx]

    def addAnalyser(self, name, dspace, multiplier=1):
        """Add new analyser (not persitent)"""
        name = str(name)
        dspace = float(dspace)
        multiplier = int(multiplier)
        self._names.append(name)
        self._dspaces.append(dspace)
        self._multipliers.append(multiplier)

    def showAllCrystals(self):
        """Displays full analyser crystal database"""
        print("ID Name       d-space multiplier")
        for n in range(len(self._names)):
            print("%2d %10s %7.4f %d" % (n, self._names[n], self._dspaces[n], self._multipliers[n]))

    def showCrystals(self, tthval=90., lowlimit=80, highlimit=100, energy_kev=None, wl=None):
        """
        Displays crystals suitable at this beamline energy

          showCrystals(tthval=90., lowlimit=80, highlimit=100, energy_kev=None)
            Without argument returns the list of crystals and reflections closest to
            90 deg. 2theta angles (>80 and <100 deg) at the current beamline energy

        :param tthval: float, Bragg angle (two-theta) required of analyser
        :param lowlimit: float, minimum Bragg angle reflections to show
        :param highlimit: float, maximum Bragg angle reflections to show
        :param energy_kev: incident beam energy in keV (None for current BL energy)
        :param wl: wavelength in A (None for current BL wavelength)
        :return: None
        """

        if energy_kev is not None:
            wl = 12.39841938 / energy_kev
        if wl is None:
            wl = BLi.getWavelength()
        energy_kev = 12.39841938 / wl

        max_index = 5
        ref_list = []
        for n in range(len(self._names)):
            if self._multipliers[n] == -1:  # odd refs
                ref_order_list = [(ref*2) - 1 for ref in range(1, max_index)]
            else:
                ref_order_list = [ref*self._multipliers[n] for ref in range(1, max_index)]
            for ref_order in ref_order_list:
                dspace = float(self._dspaces[n]) / ref_order
                if wl / (2 * dspace) > 1:
                    continue
                tthbragg = 2 * (180 / pi) * asin(wl / (2 * dspace))
                if lowlimit < tthbragg < highlimit:
                    ref_list += [{
                        'index': n,
                        'name': self._names[n],
                        'order': ref_order,
                        'dspace': dspace,
                        'tth': tthbragg
                    }]
        # sort by proximity to tthval
        ref_list.sort(key=lambda x: abs(x['tth']-tthval))

        # Print list
        print('Suitable analysers at E=%.5g keV' % energy_kev)
        print('%10s %5s %6s %8s' % ('Crystal', 'order', 'dspace', 'two-theta'))
        print('\n'.join(['%10s %5.0f %6.3f %8.4f' % (r['name'], r['order'], r['dspace'], r['tth']) for r in ref_list]))

    "---- Set Crystal ----"

    def _setAnalyser(self, index, name, order, dspace):
        """
        Set analyser crystal, order and d-spacing"
        :param index: int, index of crystal in ANALYSER_NAMES
        :param name: str, name of crystal in ANALYSER_NAMES
        :param order: int, order of reflection
        :param dspace: float, reflection d-spacing in Angstroms of 1st order reflection
        :return: None
        """
        self.crystal_index = index
        self.crystal_name = name
        if order is not None:
            self.order = order
            self._pd_ref_order(order)
        self.dspace = float(dspace) / self.order
        self._pd_index(index)

    def setAnalyserIndex(self, index, order=None):
        """Set analyser using index"""
        idx, name, dspace, orders = self.getAnalyser(index=int(index))
        self._setAnalyser(idx, name, order, dspace)

    def setAnalyserName(self, name, order=None):
        """Set analyser using index"""
        idx, name, dspace, orders = self.getAnalyser(name=str(name))
        self._setAnalyser(idx, name, order, dspace)

    "---- Calculated parameters ----"

    def calcBragg(self, energy_kev=None):
        """Return the Bragg angle, in degrees"""
        mywl = BLi.getWavelength()
        if energy_kev is not None:
            mywl = 12.39841938 / energy_kev
        return bragg_angle(mywl, self.dspace)

    def calcJones(self, stokes, energy_kev=None):
        """Return the Jones matrix"""
        bragg = self.calcBragg(energy_kev)
        return jones_analyser(stokes, 2 * bragg)


class AnalyserDetector(ScannableBase):
    """
    Device to set and get polarisation analyser detector
    Usage:
        pa_det = AnalyserDetector('pa_det', offset_detector_id, database)
        pos pa_det 0  # detector set for APD
        pos pa_det 'merlin'  # detector set for Merlin
        pa_det()  # returns: id, 'name'
        pa_det.showDetectors()   # shows list of available detectors

    database is a list of lists specifiying the available analyser detectors, with entries:
    database = [
                ('name', tthp_offset_pd, dettrans_offset_pd, use_mtthp),
                ('APD', APD_tthp_offset, APD_dettrans_offset, 0),
                ('merlin', merlin_mtthp_offset, None, 1),
                ...
               ]
    """

    def __init__(self, name, pd_pa_detector_index, detector_database):
        self.setName(name)
        self.setInputNames(['pa_detector_id'])
        self.setExtraNames(['pa_detector_name'])
        self.setOutputFormat(["%.0f", "%s"])
        self.setLevel(5)

        # Detector database
        self._names = [db[0] for db in detector_database]
        self._tthp_pd = [db[1] for db in detector_database]
        self._dettrans_pd = [db[2] for db in detector_database]
        self._use_mtthp = [db[3] for db in detector_database]
        self._pd_index = pd_pa_detector_index

        self.detector_index = 0
        self.detector_name = ''
        self.pd_tthp_offset = None
        self.pd_dettrans_offset = None
        self.use_mtthp = False
        self.setDetectorIndex(self._pd_index())

    "---- ScannableMotionBase ----"

    def getPosition(self):
        return [self.detector_index, self.detector_name]

    def isBusy(self):
        return 0

    def asynchronousMoveTo(self, index_name):
        """
        3 options:
          MoveTo(4) - int number, index of detector
          MoveTo('PG001') - str, name of detector
        """
        if index_name is None:
            return
        # str or int
        try:
            self.setDetectorIndex(int(index_name))
        except ValueError:
            self.setDetectorName(index_name)

    "---- Detector Database ----"

    def getDetector(self, name=None, index=0):
        """Returns idx, name, tthp, dettrans, use_mtthp if name in dictionary, else return APD"""
        if name is None:
            idx = int(index)
        elif name in self._names:
            idx = self._names.index(name)
        else:
            # allow, for example get_analyser('QuadMerlin') = 'Merlin'
            name = name.lower()
            idx = 0  # return APD by default
            for n, detector_name in enumerate(self._names):
                if detector_name.lower() in name:  # allow 'QuadMerlin' and 'Cam1'
                    idx = n
                    break
        return idx, self._names[idx], self._tthp_pd[idx], self._dettrans_pd[idx], self._use_mtthp[idx]

    def addDetector(self, name, tthp_offset_device, dettrans_offset_device, use_mtthp=0):
        """Add detector to database (not persistent)"""
        self._names.append(name)
        self._tthp_pd.appen(tthp_offset_device)
        self._dettrans_pd.append(dettrans_offset_device)
        self._use_mtthp.append(use_mtthp)

    def showDetectors(self):
        """Displays full analyser detector database"""
        print("ID Name")
        for n in range(len(self._names)):
            print("%2d %10s" % (n, self._names[n]))

    "---- set Detector ----"

    def setDetectorIndex(self, index):
        """Set detector using index"""
        # if None, will use the current index
        idx, name, tthp, dettrans, use_mtthp = self.getDetector(index=index)
        self._pd_index(idx)
        self.detector_index = idx
        self.detector_name = name
        self.pd_tthp_offset = tthp
        self.pd_dettrans_offset = dettrans
        self.use_mtthp = True if use_mtthp else False

    def setDetectorName(self, name):
        """Set detector using name"""
        # if None, will use the current index
        idx, name, tthp, dettrans, use_mtthp = self.getDetector(name)
        self._pd_index(idx)
        self.detector_index = idx
        self.detector_name = name
        self.pd_tthp_offset = tthp
        self.pd_dettrans_offset = dettrans
        self.use_mtthp = True if use_mtthp else False


class AnalyserJonesMatrix(ScannableBase):
    """
    Jones Matrix for Analyser crystal
    """

    def __init__(self, name, pd_stokes_motor, pa_crystal):
        self.setName(name)
        # self.setInputNames([])
        # self.setExtraNames(['pa_jones_matrix'])
        self.setOutputFormat(["%5.5g"])
        self.setLevel(5)

        self.pd_stokes_motor = pd_stokes_motor
        self._pa_crystal = pa_crystal

    def getPosition(self):
        return [self._pa_crystal.calcJones(self.pd_stokes_motor()).tolist()]

    def isBusy(self):
        return 0


"----------------------------------------------------------------------------------------------------------------------"
"--------------------------------------------- PolarisationAnalyser ---------------------------------------------------"
"----------------------------------------------------------------------------------------------------------------------"


class PolarisationAnalyser(ScannableBase):
    """
    New Polarisation Analyser scannable device
    Contains offsets for thp, tthp, dettrans, mtthp at different Stokes values to
    account for variations in alignment.
    This device contains a larger set of crystals, multiple detectors and more accurate offsets.

    Usage:
        pol = AnalyserDetector('pol', ...)
        pos pol 0  # moves stokes to 0, thp, detector to calibrated positions
        pol.showCrystals()  # show crystals suitable for this energy
        pol.showCrystals(energy_kev=6) # Show crystals available at given energy
        pol.setCrystal('PG001', 6)  # set crystal and reflection (Graphite 006)
        pol.setDetector('merlin')  # set detector. Options: APD, Merlin, Diode
        pol.move_mtthp(False)  # Fix the mtthp motor in position, in case of collision with limits
        pol.calcPos(stokes, [energy])  # show calculated motor positions
        pol.calibrate() # sets offsets at Stokes 0, 90
        pol.showOffsets() # show current offsets
        pol.reset_offsets() # set offsets to 0
        pol.getBraggAngle() # returns the Bragg angle of the reflection at the current energy (no offsets)
        pol.getJonesMatrix() # returns 2x2 Jones polarisation matrix using current positions
        pol.moveOut() # moves thp to 0, zp out of beam
        pol.moveIn() # returns motors to positions before pol.moveOut()
        pol.zpIn() # returnz zp only to "in" position
        pol.direct_beam('diode')  # moves thp to 0, zp out, tthp,dettrans to direct beam position
        # Offsets
        pol.scattering_direction(-1)  # thp scattering +1 up, -1 down
        pol.thp_offset_0(0)  # sigma thp offset
        pol.thp_offset_90(0)  # pi thp offset
        pol.tthp_offset_0(0)  # sigma tthp offset
        pol.tthp_offset_90(0)  # pi tthp offset
        pol.dettrans_offset_0(0)  # sigma dettrans offset
        pol.dettrans_offset_90(0)  # pi dettrans offset
        pol.mtthp_offset_0(0)  # sigma mtthp offset (merlin only)
        pol.mtthp_offset_90(0)  # pi mtthp offset (merlin only)
    
    Calibration:
    Motor offsets are determined by maximising the reflected intensity at Stokes angles 0 and 90
    Example:
        pol.setCrystal('PG001', 6)
        pol.setDetector('Merlin')
        pol.reset_offsets()
        pol.calcPos(0)
        pos pol 0
        scancn thp 0.05 31 merlin 1
        go peak
        pol.calibrate()
        pos pol 90
        scancn thp 0.05 31 merlin 1
        go peak
        pol.calibrate()
        scan pol -180 180 5 merlin 1
    """

    def __init__(self, name, stokes_motor, th_motor, tth_motor, zp_motor, dettrans_motor, mtthp_motor,
                 pa_crystal, pa_detector,
                 scattering_direction, thp_offset_0, thp_offset_90,
                 tthp_offset_0, tthp_offset_90,
                 dettrans_offset_0, dettrans_offset_90,
                 mtthp_offset_0, mtthp_offset_90):
        self.setName(name)
        self.setInputNames(['stokes'])
        self.setExtraNames(['thp', 'tthp', 'dettrans', 'mtthp'])
        self.setOutputFormat(["%4.4f", "%4.4f", "%4.4f", "%4.4f", "%4.4f"])

        self.stokes = stokes_motor
        self.thp = th_motor
        self.tthp = tth_motor
        self.zp = zp_motor
        self.dettrans = dettrans_motor
        self.mtthp = mtthp_motor

        # Detector
        self.detector = pa_detector  # contains detector offsets

        # Analyser crystal
        self.crystal = pa_crystal  # contains reflection d-spacing

        # Offsets
        self.scattering_direction = scattering_direction  # offset1, thp scattering direction
        self.thp_offset_0 = thp_offset_0  # offset2, thp_0
        self.thp_offset_90 = thp_offset_90  # offset3, thp_90
        self.tthp_offset_0 = tthp_offset_0  # offset4, tthp_0
        self.tthp_offset_90 = tthp_offset_90  # offset 8, tthp_90
        self.dettrans_offset_0 = dettrans_offset_0  # offset9, dettrans_0
        self.dettrans_offset_90 = dettrans_offset_90  # offset10, dettrans_90
        self.mtthp_offset_0 = mtthp_offset_0  # new
        self.mtthp_offset_90 = mtthp_offset_90  # new
        # self.zp_offset_0 = zp_offset_0  # new
        # self.zp_offset_90 = zp_offset_90  # new

        # fixed position for mtthp
        self.fixed_mtthp = False

        # Save positions when taking analyser out
        self._saved_position = None
        self.savePos()

        # functions
        self.showCrystals = self.crystal.showCrystals
        self.showAllCrystals = self.crystal.showAllCrystals
        self.showDetectors = self.detector.showDetectors
        self.addCrystal = self.crystal.addAnalyser

    "------- Database Functions -------"

    def setDetector(self, detector_name):
        """
        Sets the detector to use, specifying the motor to use and
        Available detectors are: apd, vortex, cam and merlin
         e.g.   pol.setDetector('Vortex')
        """
        self.detector(detector_name)

    def getDetector(self):
        """
        returns the detector name
        """
        return self.detector.detector_name

    def setCrystal(self, crystal_name=None, reflection_order=None):
        """
        Sets the crystal and the order of the reflection.
        e.g.   pol.setCrystal('PG001',6)
        :param crystal_name: str, Crystal name, see pol.showCrystals()
        :param reflection_order: int, multiplier for reflection index (001)*6 = (006)
        :return: None
        """
        self.crystal([crystal_name, reflection_order])

    def getCrystal(self):
        """
        Gets the crystal, reflection order and d-spacing
        :return: name, order, d-space
        """
        return self.crystal.crystal_name, self.crystal.order, self.crystal.dspace

    "------- General Functions -------"

    def checkerrors(self):
        if self.scattering_direction() == 1 or self.scattering_direction() == -1:
            return False
        else:
            raise Exception("please set the pol.scattering_direction device to either 1 (upward scattering) or -1 (downward scattering)")

    def move_mtthp(self, allow_move=None):
        """Set movement of mtthp motor, True/False"""
        if allow_move is None:
            return not self.fixed_mtthp
        self.fixed_mtthp = not allow_move
        will_move = '' if allow_move else ' not'
        print('mtthp will%s move' % will_move)

    def getBraggAngle(self, energy_kev=None):
        """Return the analyser Bragg angle, in degrees"""
        return self.crystal.calcBragg(energy_kev)

    def getJonesMatrix(self):
        """Return 2x2 Jones matrix for analyser"""
        return self.crystal.calcJones(self.stokes_motor())

    "------- Motor Offsets -------"

    def _sim_offset(self, stokes_angle, offset_0, offset_90, phase=45):
        """Calcualate the offset"""
        # return (offset_0 - offset_90) * cosd(stokes_angle) + offset_90  # old method
        amp = (offset_0 - offset_90) / (sind(0-phase) - sind(90-phase))  # amplitude of offset (not necessarily at 0 or 90)
        bkg = offset_0 - amp * sind(-phase)
        return amp * sind(stokes_angle - phase) + bkg  # new version

    def _sim_thp(self, stokes_angle, bragg_angle):
        """Calculate thp offset"""
        th = self.scattering_direction() * bragg_angle
        offset = self._sim_offset(stokes_angle, self.thp_offset_0(), self.thp_offset_90(), phase=45)
        return th + offset

    def _sim_tthp(self, stokes_angle, bragg_angle):
        """Calculate tthp offset"""
        tth = 2 * self.scattering_direction() * bragg_angle
        det_offset = self.detector.pd_tthp_offset()
        offset = self._sim_offset(stokes_angle, self.tthp_offset_0(), self.tthp_offset_90(), phase=90)
        return tth + det_offset + offset

    def _sim_dettrans(self, stokes_angle):
        """Calculate dettrans offset"""
        offset = self._sim_offset(stokes_angle, self.dettrans_offset_0(), self.dettrans_offset_90(), phase=90)
        det_offset = self.detector.pd_dettrans_offset()
        return det_offset + offset

    def _sim_mtthp(self, stokes_angle, bragg_angle):
        """Calculate mtthp offset"""
        tth = 2 * self.scattering_direction() * bragg_angle
        det_offset = self.detector.pd_tthp_offset()
        offset = self._sim_offset(stokes_angle, self.mtthp_offset_0(), self.mtthp_offset_90(), phase=90)
        return tth + det_offset + offset

    def _sim_zp(self, stokes_angle):
        """Calculate dettrans offset"""
        offset = self._sim_offset(stokes_angle, self.zp_offset_0(), self.zp_offset_90(), phase=90)
        return self._saved_position['zp'] + offset

    def _get_thp_offset(self, bragg_angle):
        """Get current thp offset"""
        th = self.scattering_direction() * bragg_angle
        thp = self.thp()
        return thp - th

    def _get_mtthp_offset(self, bragg_angle):
        """Calculate tthp offset"""
        tth = 2 * self.scattering_direction() * bragg_angle
        det_offset = self.detector.pd_tthp_offset()
        return self.mtthp() - tth - det_offset

    def _get_tthp_offset(self, bragg_angle):
        """Calculate tthp offset"""
        tth = 2 * self.scattering_direction() * bragg_angle
        det_offset = self.detector.pd_tthp_offset()
        return self.tthp() - tth - det_offset

    def _get_dettrans_offset(self):
        """Calculate dettrans offset"""
        det_offset = self.detector.pd_dettrans_offset()
        return self.dettrans() - det_offset

    def _get_zp_offset(self):
        """Calcualte the zp offset"""
        current_zp = self._saved_position['zp']
        return self.zp() - current_zp

    "------- Simulate Functions -------"

    def sim(self, stokes_angle=None, energy_kev=None):
        """
        Calculate the PA angles at a given Stokes angle and energy
        Calculates Bragg angle for analyser crystal and applies correction based on Stokes angle
        :param stokes_angle: Stokes analyser rotation angle, None to use current value
        :param energy_kev: beamline energy in keV, None to use the current value
        :return: thp, tthp, dettrans, mtthp
        """
        self.checkerrors()
        if stokes_angle is None:
            stokes_angle = self.stokes()
        bragg_angle = self.getBraggAngle(energy_kev)

        new_thp = self._sim_thp(stokes_angle, bragg_angle)
        new_tthp = None if self.detector.use_mtthp else self._sim_tthp(stokes_angle, bragg_angle)
        new_dettrans = None if self.detector.use_mtthp else self._sim_dettrans(stokes_angle)
        if self.fixed_mtthp:
            new_mtthp = self.mtthp() if self.detector.use_mtthp else None
        else:
            new_mtthp = self._sim_mtthp(stokes_angle, bragg_angle) if self.detector.use_mtthp else None
        return new_thp, new_tthp, new_dettrans, new_mtthp

    def calcPos(self, stokes_angle=None, energy_kev=None):
        """Takes one real argument, calculates for the given stokes value the polarization analyser thp and tthp """
        new_thp, new_tthp, new_dettrans, new_mtthp = self.sim(stokes_angle, energy_kev)

        if stokes_angle is None:
            stokes_angle = self.stokes()
        if energy_kev is None:
            energy_kev = 12.39841938 / BLi.getWavelength()

        print('Polarisation Analyser %s, %s, %s' % (self.detector.detector_name, self.crystal.crystal_name, self.crystal.order))
        print('%.5g keV, Stokes angle = %.5g Deg' % (energy_kev, stokes_angle))
        if self.detector.use_mtthp:
            print('thp=%.3f, mtthp=%.3f' % (new_thp, new_mtthp))
        else:
            print('thp=%.3f, tthp=%.3f, dettrans=%.3f' % (new_thp, new_tthp, new_dettrans))

    "------- Movement Functions -------"

    def savePos(self):
        """Saves current positions"""
        self._saved_position = {
            'zp': self.zp(),
            'thp': self.thp(),
            'tthp': self.tthp(),
            'dettrans': self.dettrans(),
            'mtthp': self.mtthp()
        }

    def getPosition(self):
        """Returns thp tthp and stokes without offsets"""
        self.checkerrors()
        out = [
            self.stokes(),
            self.thp(),
            self.tthp(),
            self.dettrans(),
            self.mtthp(),
        ]
        return out

    def movethp(self, stokes_angle=None, energy_kev=None):
        """Move thp only, using correction for Stokes angle"""
        new_thp, new_tthp, new_dettrans, new_mtthp = self.sim(stokes_angle, energy_kev)
        self.thp.asynchronousMoveTo(new_thp)
        self.savePos()

    def moveall(self, stokes_angle=None, energy_kev=None):
        """Move stokes, thp, tthp, dettrans, mtthp, using correction for Stokes angle"""
        new_thp, new_tthp, new_dettrans, new_mtthp = self.sim(stokes_angle, energy_kev)
        if stokes_angle is not None:
            self.stokes.asynchronousMoveTo(stokes_angle)
        self.thp.asynchronousMoveTo(new_thp)
        if new_tthp is not None:
            self.tthp.asynchronousMoveTo(new_tthp)
        if new_dettrans is not None:
            self.dettrans.asynchronousMoveTo(new_dettrans)
        if new_mtthp is not None:
            self.mtthp.asynchronousMoveTo(new_mtthp)
        self.savePos()

    def asynchronousMoveTo(self, stokes_angle):
        """Takes one real argument (the Stokes value), moves the polarization analyser thp tthp and stokes """
        self.moveall(stokes_angle)

    def isBusy(self):
        """ Returns Busy if either stokes or thp or tthp are busy"""
        self.checkerrors()
        if self.stokes.isBusy() == 1 or self.thp.isBusy() == 1 or self.tthp.isBusy() == 1 or self.mtthp.isBusy() == 1:
            return 1
        else:
            return 0

    def moveOut(self):
        """
        Removes analyser crystal
        Set thp to 0
        Set mtthp to -45
        Inc zp -10
        Restore position with
        pol.moveIn()
        """
        # self.savePos()
        print('Moving thp->0, mtthp->-45, zp-10. Return position with pol.moveIn()')
        self.thp.asynchronousMoveTo(0)
        self.mtthp.asynchronousMoveTo(-45)
        self.zp.asynchronousMoveTo(self._saved_position['zp'] - 10)

    def direct_beam(self, detector='diode'):
        """Removes analyser crystal, moves zp, thp, mtthp and detector into beam"""
        self.moveOut()
        ii, name, tthp_offset, dettrans_offset, use_mtthp = self.detector.getDetector(detector)
        if not use_mtthp:
            print('Putting %s into beam' % name)
            self.tthp.asynchronousMoveTo(tthp_offset())
            self.dettrans.asynchronousMoveTo(dettrans_offset())
        else:
            print("Merlin will not be put into beam, use merlinin()")
        while self.isBusy():
            continue

    def moveIn(self):
        """Returns analyser to previous position"""
        if self._saved_position:
            print('Returning to saved positions')
            self.thp.asynchronousMoveTo(self._saved_position['thp'])
            self.mtthp.asynchronousMoveTo(self._saved_position['mtthp'])
            self.tthp.asynchronousMoveTo(self._saved_position['tthp'])
            self.dettrans.asynchronousMoveTo(self._saved_position['dettrans'])
            self.zp.asynchronousMoveTo(self._saved_position['zp'])
            while self.isBusy():
                continue
        else:
            print('No previous position saved')

    def zpIn(self):
        """Return analyser crystal to previous height"""
        if self._saved_position:
            print('Returning zp to saved position')
            self.zp(self._saved_position['zp'])
        else:
            print('No previous position saved')

    "------- Calibration -------"

    def calibrate(self):
        """ Calibrate the PA at stokes=0 and 90 degrees
        use: when stokes = 0 and the reflection on the analiser centered call pol.calibrate()
        use: when stokes = 90 and the reflection on the analiser centered call pol.calibrate()
        The set-up of the analyser is complete.
        """
        self.checkerrors()
        bragg = self.getBraggAngle()
        stokes_angle = self.stokes()
        thp_offset = self._get_thp_offset(bragg)
        wl = BLi.getWavelength()
        self.savePos()

        print('\nPA Calibration at Stokes=%.2f Deg, E=%.3f keV' % (stokes_angle, 12.39841938 / wl))
        print('Bragg angle %.2f Deg, two-theta: %.2f Deg' % (bragg, 2 * bragg))
        print('thp offset at this position: %.3f' % thp_offset)
        if abs(stokes_angle) < 0.5:
            # Stokes 0
            self.thp_offset_0(thp_offset)
            if self.detector.use_mtthp:
                self.mtthp_offset_0(self._get_mtthp_offset(bragg))
                print('New mtthp offset0: %s' % self.mtthp_offset_0())
            else:
                self.tthp_offset_0(self._get_tthp_offset(bragg))
                self.dettrans_offset_0(self._get_dettrans_offset())
                print('New tthp offset0: %s' % self.tthp_offset_0())
                print('New dettrans offset0: %s' % self.dettrans_offset_0())
        elif abs(stokes_angle - 90) < 0.5:
            # Stokes 90
            self.thp_offset_90(thp_offset)
            if self.detector.use_mtthp:
                self.mtthp_offset_90(self._get_mtthp_offset(bragg))
                print('New mtthp offset90: %s' % self.mtthp_offset_90())
            else:
                self.tthp_offset_90(self._get_tthp_offset(bragg))
                self.dettrans_offset_90(self._get_dettrans_offset())
                print('New tthp offset90: %s' % self.tthp_offset_90())
                print('New dettrans offset90: %s' % self.dettrans_offset_90())
        else:
            raise Exception('Stokes must be 0 or 90 for calibration.')
        """
        elif abs(stokes_angle) <= 45 or abs(stokes_angle) > 135:
            # calculate offset_0
            self.thp_offset_0(self._calc_offset_0(stokes_angle, thp_offset, self.thp_offset_90()))
            print('New thp offset0: %s' % self.thp_offset_0())
            if self.detector.use_mtthp:
                mtthp_offset = self._get_mtthp_offset(bragg)
                print('mtthp offset at this position: %.2f' % mtthp_offset)
                self.mtthp_offset_0(self._calc_offset_0(stokes_angle, mtthp_offset, self.mtthp_offset_90()))
                print('New mtthp offset0: %s' % self.mtthp_offset_0())
            else:
                tthp_offset = self._get_tthp_offset(bragg)
                dettrans_offset = self._get_dettrans_offset()
                print('tthp offset at this position: %.2f' % tthp_offset)
                print('dettrans offset at this position: %.2f' % dettrans_offset)
                self.tthp_offset_0(self._calc_offset_0(stokes_angle, tthp_offset, self.tthp_offset_90()))
                self.dettrans_offset_0(self._calc_offset_0(stokes_angle, dettrans_offset, self.dettrans_offset_90()))
                print('New tthp offset0: %s' % self.tthp_offset_0())
                print('New dettrans offset0: %s' % self.dettrans_offset_0())
        else:
            # calculate offset 90
            self.thp_offset_90(self._calc_offset_90(stokes_angle, thp_offset, self.thp_offset_0()))
            print('New thp offset90: %s' % self.thp_offset_90())
            if self.detector.use_mtthp:
                mtthp_offset = self._get_mtthp_offset(bragg)
                self.mtthp_offset_90(self._calc_offset_90(stokes_angle, mtthp_offset, self.mtthp_offset_0()))
                print('New mtthp offset90: %s' % self.mtthp_offset_90())
            else:
                tthp_offset = self._get_tthp_offset(bragg)
                dettrans_offset = self._get_dettrans_offset()
                self.tthp_offset_90(self._calc_offset_90(stokes_angle, tthp_offset, self.tthp_offset_0()))
                self.dettrans_offset_90(self._calc_offset_90(stokes_angle, dettrans_offset, self.dettrans_offset_0()))
                print('New tthp offset90: %s' % self.tthp_offset_90())
                print('New dettrans offset90: %s' % self.dettrans_offset_90())
        """

    def showOffsets(self):
        """Prints the offsets for the pa device"""
        print('Scattering direction: ', self.scattering_direction)
        print('thp offset at 0: ', self.thp_offset_0)
        print('thp offset at 90: ', self.thp_offset_90)
        print('tthp offset at 0: ', self.tthp_offset_0)
        print('tthp offset at 90: ', self.tthp_offset_90)
        print('dettrans offset at 0: ', self.dettrans_offset_0)
        print('dettrans offset at 90: ', self.dettrans_offset_90)
        print('mtthp offset at 0: ', self.mtthp_offset_0)
        print('mtthp offset at 90: ', self.mtthp_offset_90)

    def reset_offsets(self, answer=None):
        """ Resets all the offsets except the crystal """
        if answer is None:
            print("Warning you are changing the offset position from:")
            print(self.scattering_direction, 'to', -1)
            print(self.thp_offset_0, 'to', 0)
            print(self.thp_offset_90, 'to', 0)
            print(self.tthp_offset_0, 'to', 0)
            print(self.tthp_offset_90, 'to', 0)
            print(self.dettrans_offset_0, 'to', 0)
            print(self.dettrans_offset_90, 'to', 0)
            print(self.mtthp_offset_0, 'to', 0)
            print(self.mtthp_offset_90, 'to', 0)
            print("The crystal and the reflection will be not changed")
            print("The scattering will be downward if stokes is 0")
            answer = input('Do you want to continue? (True/False)')
        if answer:
            self.scattering_direction(-1)
            self.thp_offset_0(0)
            self.thp_offset_90(0)
            self.tthp_offset_0(0)
            self.tthp_offset_90(0)
            self.mtthp_offset_0(0)
            self.mtthp_offset_90(0)
            self.dettrans_offset_0(0)
            self.dettrans_offset_90(0)
            print('Offsets reset')
        else:
            print("Change Aborted")


import pd_offset
APD_tthp_offset=pd_offset.Offset('APD_tthp_offset')
APD_dettrans_offset=pd_offset.Offset('APD_dettrans_offset')
diode_tthp_offset=pd_offset.Offset('diode_tthp_offset')
diode_dettrans_offset=pd_offset.Offset('diode_dettrans_offset')
cam1_tthp_offset=pd_offset.Offset('cam1_tthp_offset')
cam1_dettrans_offset=pd_offset.Offset('cam1_dettrans_offset')
merlin_mtthp_offset=pd_offset.Offset('merlin_mtthp_offset')


# Analyser dictionary (replaced with lists to keep order)
# ('name', reflection d-spacing, reflection multiplier)
PA_ANALYSER_DATABASE = [
    ('PG001', 6.711, 2),
    ('Al110', 2.86349, 2),
    ('Cu111', 2.0871, 1),
    ('Cu110', 2.5425, 2),
    ('Au111', 2.35458, 1),
    ('Ni001', 4.33, 2),
    ('InSb100', 6.4782, 2),
    ('LiF110', 2.84066, 2),
    ('LiF100', 4.0173, 2),
    ('Mo100', 3.1473, 2),
    ('MgO100', 4.213, 1),
    ('MgO111', 2.43122, 1),
    ('MnO100', 4.4449, 2),
    ('Pb111', 2.85214, 1),
    ('Sn100', 5.8197, 2),
    ('Al2O3001', 12.9933, 6),
    ('LAO001', 3.78295, 1),
    ('YSZ100', 5.15463, 2),
    ('GGG001', 12.3829, 4),
    ('Si111', 3.13553, -1),
    ('Ge111', 3.2663, -1),
]
# Detector database
# ('name', tthp_offset_pd, dettrans_offset_pd, use_mtthp)
PA_DETECTOR_DATABASE = [
    ('APD', APD_tthp_offset, APD_dettrans_offset, 0),
    ('Vortex', None, None, 0),
    ('Cam', cam1_tthp_offset, cam1_dettrans_offset, 0),
    ('Diode', diode_tthp_offset, diode_dettrans_offset, 0),
    ('Merlin', merlin_mtthp_offset, None, 1),
]
# new pa offsets
pa_detector_id = pd_offset.Offset('pa_detector_id')
pa_direction_offset = pd_offset.Offset('pa_direction_offset')
pa_thp_offset_0 = pd_offset.Offset('pa_thp_offset_0')
pa_thp_offset_90 = pd_offset.Offset('pa_thp_offset_90')
pa_tthp_offset_0 = pd_offset.Offset('pa_tthp_offset_0')
pa_tthp_offset_90 = pd_offset.Offset('pa_tthp_offset_90')
pa_dettrans_offset_0 = pd_offset.Offset('pa_dettrans_offset_0')
pa_dettrans_offset_90 = pd_offset.Offset('pa_dettrans_offset_90')
pa_mtthp_offset_0 = pd_offset.Offset('pa_mtthp_offset_0')
pa_mtthp_offset_90 = pd_offset.Offset('pa_mtthp_offset_90')
# Instatiate devices

from localStationScripts.startup_offsets import cry_offset, ref_offset
from gdaserver import stokes, thp, tthp, dettrans, mtthp
from localStationScripts.startup_epics_positioners import zp

pa_crystal = AnalyserCrystal('pa_crystal', cry_offset, ref_offset, PA_ANALYSER_DATABASE)
pa_detector = AnalyserDetector('pa_detector', pa_detector_id, PA_DETECTOR_DATABASE)

pol = PolarisationAnalyser(
    name='pol',
    stokes_motor=stokes,
    th_motor=thp,
    tth_motor=tthp,
    zp_motor=zp,
    dettrans_motor=dettrans,
    mtthp_motor=mtthp,
    pa_crystal=pa_crystal,
    pa_detector=pa_detector,
    scattering_direction=pa_direction_offset,
    thp_offset_0=pa_thp_offset_0,
    thp_offset_90=pa_thp_offset_90,
    tthp_offset_0=pa_tthp_offset_0,
    tthp_offset_90=pa_tthp_offset_90,
    dettrans_offset_0=pa_dettrans_offset_0,
    dettrans_offset_90=pa_dettrans_offset_90,
    mtthp_offset_0=pa_mtthp_offset_0,
    mtthp_offset_90=pa_mtthp_offset_90
)
pa_jones = AnalyserJonesMatrix('pa_jones', stokes, pa_crystal)
# sample_moment = CrystalMagneticMoment('sample_moment', hkl)
# charge_scattering = SampleCharge('charge_scattering', sample_moment, stokes_pars, pa_jones)
# magE1E1_scattering = SampleMagE1E1('magE1E1_scattering', sample_moment, stokes_pars, pa_jones)
# magSpin_scattering = SampleMagSpin('magSpin_scattering', sample_moment, stokes_pars, pa_jones)