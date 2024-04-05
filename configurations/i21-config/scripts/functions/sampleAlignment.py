'''
functions used to perform sample alignment

Created on Jun 29, 2023

@author: fy65
'''
from shutters.detectorShutterControl import fsxas
from gdascripts.scan.installStandardScansWithProcessing import cscan
from time import sleep
from gdaserver import diff1_i  # @UnresolvedImport

def halfcut(x_range, x_step, amplifier = diff1_i, amplifier_gain = "10^5 low noise" ):
    from gdaserver import th, difftth, x, m4c1    # @UnresolvedImport
    fsxas()
    th.asynchronousMoveTo(0)
    difftth.asynchronousMoveTo(0)
    if amplifier.getName() not in ['diff1', 'diff1_i']:
        raise NameError("halfcut method requires object 'diff1_i' or 'diff1', but '%s' is given!" % amplifier.getName())
    # initialise gain setting
    if amplifier.getName() == "diff1":
        amplifier.setGain(amplifier_gain)
    if amplifier.getName() == "diff1_i":
        amplifier.setFemtoMode("Low Noise")
        amplifier.setGain(1e5)
    while th.isBusy() or difftth.isBusy():
        sleep(0.1)
    cscan(x, x_range, x_step, amplifier, m4c1)