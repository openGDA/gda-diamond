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
        self.grating_density                = 400.              # caget BL10I-OP-PGM-01:NLINES
        self.cff                            = 2.25              # caget BL10I-OP-PGM-01:CFF
        self.grating_offset                 = 0.40708           # caget BL10I-OP-PGM-01:GRTOFFSET
        self.plane_mirror_offset            = 0.002739          # caget BL10I-OP-PGM-01:MIROFFSET

        self.pgm_energy                     = 712.300           # caget BL10I-OP-PGM-01:ENERGY

        self.grating_pitch                  = 88.0151063265128  # caget -g15 BL10I-OP-PGM-01:GRT:PITCH
        self.mirror_pitch                   = 88.2753263680692  # caget -g15 BL10I-OP-PGM-01:MIR:PITCH

        self.energy_calibration_gradient    = 1.011             # caget BL10I-OP-PGM-01:MX
        self.energy_calibration_reference   = 430.              # caget BL10I-OP-PGM-01:REFERENCE

        self.decimal_places                 = 5                 # The accuracy possible is determined by the accuracy of the pitch values.

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

"""
class PgmTest2(PgmTest1):

    def setUp(self):
        self.grating_density                = 400.              # caget BL10I-OP-PGM-01:NLINES
        self.cff                            = 2.25              # caget BL10I-OP-PGM-01:CFF
        self.grating_offset                 = 0.40708           # caget BL10I-OP-PGM-01:GRTOFFSET
        self.plane_mirror_offset            = 0.002739          # caget BL10I-OP-PGM-01:MIROFFSET

        self.pgm_energy                     = 712.300           # caget BL10I-OP-PGM-01:ENERGY

        self.grating_pitch                  = 88.0151063265128  # caget -g15 BL10I-OP-PGM-01:GRT:PITCH
        self.mirror_pitch                   = 88.2753263680692  # caget -g15 BL10I-OP-PGM-01:MIR:PITCH

        self.energy_calibration_gradient    = 1.011             # caget BL10I-OP-PGM-01:MX
        self.energy_calibration_reference   = 430.              # caget BL10I-OP-PGM-01:REFERENCE

        self.decimal_places         = 6
"""