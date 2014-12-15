"""
Unit tests for Peter Beckcocks pgm conversion functions.

For use with GDA on I10 at Diamond Light Source
"""

import unittest
from pgm.pgm import enecff2grating, angles2energy, enecff2mirror, enemirror2grating

class PgmTest1(unittest.TestCase):

    def tearDown(self):
        pass

    def setUp(self):
        #self.grating_density        = 1000.      # BL10I-OP-PGM-01:NLINES2
        self.grating_density        = 400.      # BL10I-OP-PGM-01:NLINES        400 line/mm Au
        self.cff                    = 2.25      # BL10I-OP-PGM-01:CFF            |
        self.grating_offset         = 0.40708   # BL10I-OP-PGM-01:GRTOFFSET    < / > BL10I-OP-PGM-01:GRT1:GOFF
        self.plane_mirror_offset    = 0.002739  # BL10I-OP-PGM-01:MIROFFSET    < / > BL10I-OP-PGM-01:GRT1:MOFF

        self.pgm_energy             = 712.300   # BL10I-OP-PGM-01:ENERGY

        self.grating_pitch          = 88.0151   # BL10I-OP-PGM-01:GRT:PITCH.RBV
        self.mirror_pitch           = 88.2753   # BL10I-OP-PGM-01:MIR:PITCH.RBV

        self.energy_calibration_gradient    = 1.011 # ?                                > BL10I-OP-PGM-01:GRT1:MX
        self.energy_calibration_reference   = 430. # ?                                > BL10I-OP-PGM-01:GRT1:REFERENCE

        self.decimal_places         = 2

    def testEnergy(self):
        energy = angles2energy(gd       = self.grating_density,
                               grang    = self.grating_pitch,
                               pmang    = self.mirror_pitch,
                               groff    = self.grating_offset,
                               pmoff    = self.plane_mirror_offset,
                               ecg      = self.energy_calibration_gradient,
                               ecr      = self.energy_calibration_reference)
        
        self.assertAlmostEqual(energy, self.pgm_energy, self.decimal_places)

    def testGratPitchFromEnergyAndCff(self):
        grat_pitch=enecff2grating(gd     = self.grating_density,
                                  energy = self.pgm_energy,
                                  cff    = self.cff,
                                  groff  = self.grating_offset,
                                  ecg    = self.energy_calibration_gradient,
                                  ecr    = self.energy_calibration_reference)
        
        self.assertAlmostEqual(grat_pitch, self.grating_pitch, self.decimal_places)

    def testMirrPitch(self):
        mirr_pitch=enecff2mirror(gd     = self.grating_density,
                                 energy = self.pgm_energy,
                                 cff    = self.cff,
                                 groff  = self.grating_offset,
                                 pmoff  = self.plane_mirror_offset,
                                 ecg    = self.energy_calibration_gradient,
                                 ecr    = self.energy_calibration_reference)
        
        self.assertAlmostEqual(mirr_pitch, self.mirror_pitch, self.decimal_places)

    def testGratPitch(self):
        grat_pitch=enemirror2grating(gd     = self.grating_density,
                                     energy = self.pgm_energy,
                                     pmang  = self.mirror_pitch,
                                     groff  = self.grating_offset,
                                     pmoff  = self.plane_mirror_offset,
                                     ecg    = self.energy_calibration_gradient,
                                     ecr    = self.energy_calibration_reference)
        
        self.assertAlmostEqual(grat_pitch, self.grating_pitch, self.decimal_places)

class PgmTest2(PgmTest1):

    def setUp(self):
        self.grating_density        = 400.      # BL10I-OP-PGM-01:NLINES
        self.cff                    = 2.25      # BL10I-OP-PGM-01:CFF
        self.grating_offset         = 0.40708   # BL10I-OP-PGM-01:GRTOFFSET
        self.plane_mirror_offset    = 0.002739  # BL10I-OP-PGM-01:MIROFFSET

        self.pgm_energy             = 696.210   # BL10I-OP-PGM-01:ENERGY

        self.grating_pitch          = 87.932    # BL10I-OP-PGM-01:GRT:PITCH.RBV
        self.mirror_pitch           = 88.255    # BL10I-OP-PGM-01:MIR:PITCH.RBV

        self.energy_calibration_gradient    = 1.011 # ?                                > BL10I-OP-PGM-01:GRT1:MX
        self.energy_calibration_reference   = 430. # ?                                > BL10I-OP-PGM-01:GRT1:REFERENCE

        self.decimal_places         = 2

class PgmTest3(PgmTest1):

    def setUp(self):
        self.grating_density        = 400.      # BL10I-OP-PGM-01:NLINES
        self.cff                    = 2.25      # BL10I-OP-PGM-01:CFF
        self.grating_offset         = 0.40708   # BL10I-OP-PGM-01:GRTOFFSET
        self.plane_mirror_offset    = 0.002739  # BL10I-OP-PGM-01:MIROFFSET

        self.pgm_energy             = 697.20    # BL10I-OP-PGM-01:ENERGY

        self.grating_pitch          = 87.933    # BL10I-OP-PGM-01:GRT:PITCH.RBV
        self.mirror_pitch           = 88.256    # BL10I-OP-PGM-01:MIR:PITCH.RBV

        self.energy_calibration_gradient    = 1.011 # ?                                > BL10I-OP-PGM-01:GRT1:MX
        self.energy_calibration_reference   = 430. # ?                                > BL10I-OP-PGM-01:GRT1:REFERENCE

        self.decimal_places         = 2

class PgmTest4(PgmTest1):

    def setUp(self):
        self.grating_density        = 400.      # BL10I-OP-PGM-01:NLINES
        self.cff                    = 2.25      # BL10I-OP-PGM-01:CFF
        self.grating_offset         = 0.40708   # BL10I-OP-PGM-01:GRTOFFSET
        self.plane_mirror_offset    = 0.002739  # BL10I-OP-PGM-01:MIROFFSET

        self.pgm_energy             = 698.21    # BL10I-OP-PGM-01:ENERGY

        self.grating_pitch          = 87.935    # BL10I-OP-PGM-01:GRT:PITCH.RBV
        self.mirror_pitch           = 88.257    # BL10I-OP-PGM-01:MIR:PITCH.RBV

        self.energy_calibration_gradient    = 1.011 # ?                                > BL10I-OP-PGM-01:GRT1:MX
        self.energy_calibration_reference   = 430. # ?                                > BL10I-OP-PGM-01:GRT1:REFERENCE

        self.decimal_places         = 2

"""
Finding files... done.
Importing test modules ... done.

======================================================================
FAIL: testEnergy (pgmTest.PgmTest1)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/dls_sw/i10/software/gda_versions/gda_8.40b/workspace_git/gda-mt.git/configurations/i10-shared/scripts/test/pgm/pgmTest.py", line 41, in testEnergy
    self.assertAlmostEqual(energy, self.pgm_energy, self.decimal_places)
AssertionError: 712.3106769444129 != 712.3 within 2 places

======================================================================
FAIL: testEnergy (pgmTest.PgmTest2)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/dls_sw/i10/software/gda_versions/gda_8.40b/workspace_git/gda-mt.git/configurations/i10-shared/scripts/test/pgm/pgmTest.py", line 41, in testEnergy
    self.assertAlmostEqual(energy, self.pgm_energy, self.decimal_places)
AssertionError: 642.7958796818319 != 696.21 within 2 places

======================================================================
FAIL: testGratPitch (pgmTest.PgmTest2)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/dls_sw/i10/software/gda_versions/gda_8.40b/workspace_git/gda-mt.git/configurations/i10-shared/scripts/test/pgm/pgmTest.py", line 73, in testGratPitch
    self.assertAlmostEqual(grat_pitch, self.grating_pitch, self.decimal_places)
AssertionError: 87.98742861615946 != 87.932 within 2 places

======================================================================
FAIL: testGratPitchFromEnergyAndCff (pgmTest.PgmTest2)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/dls_sw/i10/software/gda_versions/gda_8.40b/workspace_git/gda-mt.git/configurations/i10-shared/scripts/test/pgm/pgmTest.py", line 51, in testGratPitchFromEnergyAndCff
    self.assertAlmostEqual(grat_pitch, self.grating_pitch, self.decimal_places)
AssertionError: 87.98780671618469 != 87.932 within 2 places

======================================================================
FAIL: testEnergy (pgmTest.PgmTest3)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/dls_sw/i10/software/gda_versions/gda_8.40b/workspace_git/gda-mt.git/configurations/i10-shared/scripts/test/pgm/pgmTest.py", line 41, in testEnergy
    self.assertAlmostEqual(energy, self.pgm_energy, self.decimal_places)
AssertionError: 643.1664703010379 != 697.2 within 2 places

======================================================================
FAIL: testGratPitch (pgmTest.PgmTest3)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/dls_sw/i10/software/gda_versions/gda_8.40b/workspace_git/gda-mt.git/configurations/i10-shared/scripts/test/pgm/pgmTest.py", line 73, in testGratPitch
    self.assertAlmostEqual(grat_pitch, self.grating_pitch, self.decimal_places)
AssertionError: 87.98899230012374 != 87.933 within 2 places

======================================================================
FAIL: testGratPitchFromEnergyAndCff (pgmTest.PgmTest3)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/dls_sw/i10/software/gda_versions/gda_8.40b/workspace_git/gda-mt.git/configurations/i10-shared/scripts/test/pgm/pgmTest.py", line 51, in testGratPitchFromEnergyAndCff
    self.assertAlmostEqual(grat_pitch, self.grating_pitch, self.decimal_places)
AssertionError: 87.98951348933139 != 87.933 within 2 places

======================================================================
FAIL: testEnergy (pgmTest.PgmTest4)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/dls_sw/i10/software/gda_versions/gda_8.40b/workspace_git/gda-mt.git/configurations/i10-shared/scripts/test/pgm/pgmTest.py", line 41, in testEnergy
    self.assertAlmostEqual(energy, self.pgm_energy, self.decimal_places)
AssertionError: 644.4299488527497 != 698.21 within 2 places

======================================================================
FAIL: testGratPitch (pgmTest.PgmTest4)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/dls_sw/i10/software/gda_versions/gda_8.40b/workspace_git/gda-mt.git/configurations/i10-shared/scripts/test/pgm/pgmTest.py", line 73, in testGratPitch
    self.assertAlmostEqual(grat_pitch, self.grating_pitch, self.decimal_places)
AssertionError: 87.99057304288202 != 87.935 within 2 places

======================================================================
FAIL: testGratPitchFromEnergyAndCff (pgmTest.PgmTest4)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/dls_sw/i10/software/gda_versions/gda_8.40b/workspace_git/gda-mt.git/configurations/i10-shared/scripts/test/pgm/pgmTest.py", line 51, in testGratPitchFromEnergyAndCff
    self.assertAlmostEqual(grat_pitch, self.grating_pitch, self.decimal_places)
AssertionError: 87.99125102554004 != 87.935 within 2 places

----------------------------------------------------------------------
Ran 16 tests in 0.027s

FAILED (failures=10)

"""