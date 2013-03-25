"""
Unit tests for PerkinElmerAxisWrapper & DetectorAxisWrapperNew
for use with GDA at Diamond Light Source
"""

import unittest
from mock import Mock
from scannables.detectors.perkinElmer import DummyCAClient
from scannables.fastShutter import FastShutterFeedback

class FastShutterFeedbackTest(unittest.TestCase):
    def setUp(self):
        self.fs = FastShutterFeedback(Mock())

    def test__str__(self):
        self.assertEquals(str(self.fs),
            "")

    def test__repr__(self):
        self.assertEquals(repr(self.fs),
            "")