'''
Created on 3 Jan 2024

@author: grc37356
'''

from gda.factory import Finder

class CombinedNormaliser:

    def __init__(self, step_normaliser, continuous_normaliser):
        self.step_norm = step_normaliser
        self.cts_norm = continuous_normaliser

    def enable(self) :
        self.step_norm.setEnable(True)
        self.cts_norm.setEnabled(True)

    def disable(self) :
        self.step_norm.setEnable(False)
        self.cts_norm.setEnabled(False)

    def setNorm(self, enabled=True):
        self.step_norm.setNorm(enabled)
        self.cts_norm.setNorm(enabled)

    def setBackgroundSubtractionEnabled(self, enabled=True):
        self.step_norm.setBackgroundSubtractionEnabled(enabled)
        self.cts_norm.setBackgroundSubtractionEnabled(enabled)

    def setScale(self, scale):
        self.step_norm.setScale(scale)
        self.cts_norm.setScale(scale)

    def setSignalRoiIndex(self, index):
        self.step_norm.setSignalRoiIndex(index)
        self.cts_norm.setSignalRoiIndex(index)

    def setBackgroundRoiIndices(self, indices):
        self.step_norm.setBackgroundRoiIndices(indices)
        self.cts_norm.setBackgroundRoiIndices(indices)

    def setMonitorScannable(self, scannable_to_normalise_by):
        self.step_norm.setMonitorScannable(scannable_to_normalise_by)
        self.cts_norm.setMonitorScannable(scannable_to_normalise_by)

ex_norm = CombinedNormaliser(Finder.find("excalibur_norm"), Finder.find("MalcNormProcExc"))
p2_norm = CombinedNormaliser(Finder.find("pilatus2_norm"), Finder.find("MalcNormProcPil2"))
p3_norm = CombinedNormaliser(Finder.find("pilatus3_norm"), Finder.find("MalcNormProcPil3"))