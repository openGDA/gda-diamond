# run 'scannable/continuous/try_continuous_energy.py'
# When reloading, you may need to run this twice

from datetime import datetime
from future.scannable.scaler import McsController, McsChannelScannable
from future.scannable.binpoint import BinpointController, BinpointChannelScannable
from gda.device.detector.hardwaretriggerable import \
                    DummyHardwareTriggerableDetector
#from gda.scan import ConstantVelocityScanLine
from gdascripts.scan import trajscans
from gdascripts.scan.scanListener import ScanListener
from scannable.continuous.ContinuousPgmEnergyMoveController import \
                          ContinuousPgmEnergyMoveController
from scannable.continuous.ContinuousPgmEnergyScannable import \
                          ContinuousPgmEnergyScannable

global pgm_energy

cemc = ContinuousPgmEnergyMoveController('cemc', pgm_energy)
egy = ContinuousPgmEnergyScannable('egy', cemc)

st = DummyHardwareTriggerableDetector('st')
st.setHardwareTriggerProvider(cemc)

# I branch counter:  BL10I-DI-SCLR-01:MCA01:
counterIBasePv =    'BL10I-DI-SCLR-01:MCA01:'
# RASOR counter:     ME01D-EA-SCLR-01:MCA01:         ME01D-EA-SCLR-01:MCA01:StartAll
counterRBasePv =    'ME01D-EA-SCLR-01:MCA01:'
# J branch counter:  BL10J-DI-SCLR-01:MCAJ01:        BL10J-DI-SCLR-01:MCAJ01:StartAll
counterJBasePv =    'BL10J-DI-SCLR-01:MCAJ01:'

mcsic  = McsController(               'mcsic',counterJBasePv)
mcsi16 = McsChannelScannable('mcsi16', mcsic, counterIBasePv, 17)
mcsi16.setHardwareTriggerProvider(cemc)
mcsi17 = McsChannelScannable('mcsi17', mcsic, counterIBasePv, 18)
mcsi17.setHardwareTriggerProvider(cemc)
mcsi18 = McsChannelScannable('mcsi18', mcsic, counterIBasePv, 19)
mcsi18.setHardwareTriggerProvider(cemc)
mcsi19 = McsChannelScannable('mcsi19', mcsic, counterIBasePv, 20)
mcsi19.setHardwareTriggerProvider(cemc)

mcsrc  = McsController(               'mcsrc',counterRBasePv)
mcsr16 = McsChannelScannable('mcsr16', mcsrc, counterRBasePv, 17)
mcsr16.setHardwareTriggerProvider(cemc)
mcsr17 = McsChannelScannable('mcsr17', mcsrc, counterRBasePv, 18)
mcsr17.setHardwareTriggerProvider(cemc)
mcsr18 = McsChannelScannable('mcsr18', mcsrc, counterRBasePv, 19)
mcsr18.setHardwareTriggerProvider(cemc)
mcsr19 = McsChannelScannable('mcsr19', mcsrc, counterRBasePv, 20)
mcsr19.setHardwareTriggerProvider(cemc)

# This doesn't appear to support MCA mode yet...
mcsjc  = McsController(               'mcsjc',counterJBasePv)
mcsj16 = McsChannelScannable('mcsj16', mcsjc, counterJBasePv, 17)
mcsj16.setHardwareTriggerProvider(cemc)
mcsj17 = McsChannelScannable('mcsj17', mcsjc, counterJBasePv, 18)
mcsj17.setHardwareTriggerProvider(cemc)
mcsj18 = McsChannelScannable('mcsj18', mcsjc, counterJBasePv, 19)
mcsj18.setHardwareTriggerProvider(cemc)
mcsj19 = McsChannelScannable('mcsj19', mcsjc, counterJBasePv, 20)
mcsj19.setHardwareTriggerProvider(cemc)

binpointBasePV = 'BL10I-CS-CSCAN-01:'
binpointc           = BinpointController(                            'binpointc',binpointBasePV, 'IDPGM:BINPOINTALL:')
binpointGrtPitch    = BinpointChannelScannable('binpointGrtPitch',    binpointc, binpointBasePV, 'GRT:PITCH:')
binpointGrtPitch.setHardwareTriggerProvider(cemc)
binpointMirPitch    = BinpointChannelScannable('binpointMirPitch',    binpointc, binpointBasePV, 'MIR:PITCH:')
binpointMirPitch.setHardwareTriggerProvider(cemc)
binpointPgmEnergy   = BinpointChannelScannable('binpointPgmEnergy',   binpointc, binpointBasePV, 'PGM:ENERGY:')
binpointPgmEnergy.setHardwareTriggerProvider(cemc)
binpointId1JawPhase = BinpointChannelScannable('binpointId1JawPhase', binpointc, binpointBasePV, 'ID1:JAWPHASE:')
binpointId1JawPhase.setHardwareTriggerProvider(cemc)
binpointId2JawPhase = BinpointChannelScannable('binpointId2JawPhase', binpointc, binpointBasePV, 'ID2:JAWPHASE:')
binpointId2JawPhase.setHardwareTriggerProvider(cemc)
binpointMcaTime     = BinpointChannelScannable('binpointMcaTime',     binpointc, binpointBasePV, 'MCA:ELAPSEDTIME:')
binpointMcaTime.setHardwareTriggerProvider(cemc)
binpointCustom1     = BinpointChannelScannable('binpointCustom1',     binpointc, binpointBasePV, 'CUSTOM1:')
binpointCustom1.setHardwareTriggerProvider(cemc)
binpointCustom2     = BinpointChannelScannable('binpointCustom2',     binpointc, binpointBasePV, 'CUSTOM2:')
binpointCustom2.setHardwareTriggerProvider(cemc)

# cvscan egy 695 705 1 mcs1 mcs17 mcs16 2 binpointGrtPitch binpointMirPitch binpointPgmEnergy binpointId1JawPhase binpointId2JawPhase binpointMcaTime 

class TrajectoryControllerHelper(ScanListener):
    
    def prepareForScan(self):
        print str(datetime.now()), "TrajectoryControllerHelper.prepareForScan"

    def update(self, scanObject):
        print str(datetime.now()), "TrajectoryControllerHelper.update"


trajscans.DEFAULT_SCANNABLES_FOR_TRAJSCANS = [meta] # @UndefinedVariable

trajectory_controller_helper = TrajectoryControllerHelper()

print "Creating gda cvscan commands:"
# These will need more classes added to /uk.ac.gda.core/scripts/gdascripts/scan/trajscans.py
#trajcscan=trajscans.TrajCscan([scan_processor, trajectory_controller_helper]) #@UndefinedVariable
#trajrscan=trajscans.TrajRscan([scan_processor, trajectory_controller_helper]) #@UndefinedVariable
cvscan=trajscans.CvScan([scan_processor, trajectory_controller_helper]) #@UndefinedVariable
alias('cvscan') #@UndefinedVariable

# E.g. cvscan egy 695 705 1 mcs1 mcs17 mcs16 2

""" Tests:
    10ev at 2 seconds per 1ev 'step & 10ev at .2 seconds per .1ev 'step:

    scan pgm_energy 695 705 1 macr1 macr16 macr17 2       11 points, 28 seconds (18:32:36 to 18:33:24)
    scan pgm_energy 695 705 .1 macr1 macr16 macr17 .2    101 points, 3 minutes 15 seconds (18:35:57 to 18:39:12
    
    cvscan egy 695 705 1 mcs1 mcs16 mcs17 2                11 points, 34 seconds (18:41:48 to 18:42:22)
    cvscan egy 695 705 .1 mcs1 mcs16 mcs17 .2            101? points, 36 seconds (18:45:09 to 18:45:45)

>>>run "scannable/continuous/try_continuous_energy.py"
>>>pgm_energy.speed
0.5
>>>scan pgm_energy 695 705 1 macr1 macr16 macr17 2
Writing data to file:/dls/i10/data/2013/cm5934-3/i10-51743.dat
pgm_energy    ips_field    demand_field         itc2    sensor_temp    magj1yins    magj1yrot    m6_pitch    macr1    macr16    macr17    macj117    macj118
    694.99     0.000000        0.000000    67.560000      67.560000       19.358       0.0000     -596.69        0    142394       284          0          0
    696.00     0.000000        0.000000    67.560000      67.560000       19.358       0.0000     -596.69        0    142503       285          0          0
    697.00     0.000000        0.000000    67.560000      67.560000       19.358       0.0000     -596.69        0    142536       285          0          0
    698.00     0.000000        0.000000    67.560000      67.560000       19.358       0.0000     -596.69        0    142654       284          0          0
    698.99     0.000000        0.000000    67.560000      67.560000       19.358       0.0000     -596.69        0    142649       286          0          0
    700.00     0.000000        0.000000    67.560000      67.560000       19.358       0.0000     -596.69        0    142128       285          0          0
    701.00     0.000000        0.000000    67.560000      67.560000       19.358       0.0000     -596.69        0    142430       284          0          0
    702.00     0.000000        0.000000    67.560000      67.560000       19.358       0.0000     -596.69        0    142269       284          0          0
    703.00     0.000000        0.000000    67.560000      67.560000       19.358       0.0000     -596.69        0    142265       284          0          0
    703.99     0.000000        0.000000    67.560000      67.560000       19.358       0.0000     -596.69        0    141794       284          0          0
    705.01     0.000000        0.000000    67.560000      67.560000       19.358       0.0000     -596.69        0    141666       284          0          0
Scan complete.
Error processing scan file: Traceback (most recent call last):
  File "/dls_sw/i10/software/gda_versions/gda_8.30a/workspace_git/gda-core.git/uk.ac.gda.core/scripts/gdascripts/scan/process/ScanDataProcessor.py", line 76, in processScan
    yscannable = determineScannableContainingField(yfieldname, allscannables)
  File "/dls_sw/i10/software/gda_versions/gda_8.30a/workspace_git/gda-core.git/uk.ac.gda.core/scripts/gdascripts/scan/process/ScanDataProcessorResult.py", line 11, in determineScannableContainingField
    raise KeyError("targetFieldname %s not found in scannables: %s" % (targetFieldname, [scn.getName() for scn in scannables]))
KeyError: u"targetFieldname macr17 not found in scannables: [u'pgm_energy', u'macr1', u'macr16', u'macr17']"

<< No exception raised >>>
'Error processing scan file: Traceback (most recent call last):\n  File "/dls_sw/i10/software/gda_versions/gda_8.30a/workspace_git/gda-core.git/uk.ac.gda.core/scripts/gdascripts/scan/process/ScanDataProcessor.py", line 76, in processScan\n    yscannable = determineScannableContainingField(yfieldname, allscannables)\n  File "/dls_sw/i10/software/gda_versions/gda_8.30a/workspace_git/gda-core.git/uk.ac.gda.core/scripts/gdascripts/scan/process/ScanDataProcessorResult.py", line 11, in determineScannableContainingField\n    raise KeyError("targetFieldname %s not found in scannables: %s" % (targetFieldname, [scn.getName() for scn in scannables]))\nKeyError: u"targetFieldname macr17 not found in scannables: [u\'pgm_energy\', u\'macr1\', u\'macr16\', u\'macr17\']"\n\n<< No exception raised >>>'
>>>scan pgm_energy 695 705 .1 macr1 macr16 macr17 .2
Writing data to file:/dls/i10/data/2013/cm5934-3/i10-51744.dat
pgm_energy    ips_field    demand_field         itc2    sensor_temp    magj1yins    magj1yrot    m6_pitch    macr1    macr16    macr17    macj117    macj118
    695.01     0.000000        0.000000    67.560000      67.560000       19.358       0.0000     -596.69        0     14107        28          0          0
    695.08     0.000000        0.000000    67.560000      67.560000       19.358       0.0000     -596.69        0     14070        28          0          0
    695.20     0.000000        0.000000    67.560000      67.560000       19.358       0.0000     -596.69        0     14155        29          0          0
    695.32     0.000000        0.000000    67.560000      67.560000       19.358       0.0000     -596.69        0     14102        29          0          0
...
    704.60     0.000000        0.000000    67.560000      67.570000       19.358       0.0000     -596.69        0     14044        28          0          0
    704.70     0.000000        0.000000    67.560000      67.560000       19.358       0.0000     -596.69        0     13992        29          0          0
    704.81     0.000000        0.000000    67.560000      67.560000       19.358       0.0000     -596.69        0     13851        28          0          0
    704.90     0.000000        0.000000    67.560000      67.560000       19.358       0.0000     -596.69        0     13879        28          0          0
    705.00     0.000000        0.000000    67.560000      67.560000       19.358       0.0000     -596.69        0     13989        29          0          0
Scan complete.
Error processing scan file: Traceback (most recent call last):
  File "/dls_sw/i10/software/gda_versions/gda_8.30a/workspace_git/gda-core.git/uk.ac.gda.core/scripts/gdascripts/scan/process/ScanDataProcessor.py", line 76, in processScan
    yscannable = determineScannableContainingField(yfieldname, allscannables)
  File "/dls_sw/i10/software/gda_versions/gda_8.30a/workspace_git/gda-core.git/uk.ac.gda.core/scripts/gdascripts/scan/process/ScanDataProcessorResult.py", line 11, in determineScannableContainingField
    raise KeyError("targetFieldname %s not found in scannables: %s" % (targetFieldname, [scn.getName() for scn in scannables]))
KeyError: u"targetFieldname macr17 not found in scannables: [u'pgm_energy', u'macr1', u'macr16', u'macr17']"

<< No exception raised >>>
'Error processing scan file: Traceback (most recent call last):\n  File "/dls_sw/i10/software/gda_versions/gda_8.30a/workspace_git/gda-core.git/uk.ac.gda.core/scripts/gdascripts/scan/process/ScanDataProcessor.py", line 76, in processScan\n    yscannable = determineScannableContainingField(yfieldname, allscannables)\n  File "/dls_sw/i10/software/gda_versions/gda_8.30a/workspace_git/gda-core.git/uk.ac.gda.core/scripts/gdascripts/scan/process/ScanDataProcessorResult.py", line 11, in determineScannableContainingField\n    raise KeyError("targetFieldname %s not found in scannables: %s" % (targetFieldname, [scn.getName() for scn in scannables]))\nKeyError: u"targetFieldname macr17 not found in scannables: [u\'pgm_energy\', u\'macr1\', u\'macr16\', u\'macr17\']"\n\n<< No exception raised >>>'
>>>pgm_energy.speed
20.0
>>>cvscan egy 695 705 1 mcs1 mcs16 mcs17 2
2013-06-18 18:41:48.627000 TrajectoryControllerHelper.prepareForScan
2013-06-18 18:41:48.630000 mcs17 setCollectionTime(2.0)
2013-06-18 18:41:48.848999 mcs1 atScanLineStart...
2013-06-18 18:41:48.851999 mcsc erase_and_start...
2013-06-18 18:41:48.865000 mcsc ...erase_and_start
2013-06-18 18:41:48.867000 mcs1 ...atScanLineStart
2013-06-18 18:41:48.869999 mcs16 atScanLineStart...
2013-06-18 18:41:48.872999 mcsc erase_and_start...
2013-06-18 18:41:49.019999 mcsc ...erase_and_start
2013-06-18 18:41:49.022000 mcs16 ...atScanLineStart
2013-06-18 18:41:49.025000 mcs17 atScanLineStart...
2013-06-18 18:41:49.026999 mcsc erase_and_start...
2013-06-18 18:41:49.173000 mcsc ...erase_and_start
2013-06-18 18:41:49.174999 mcs17 ...atScanLineStart
2013-06-18 18:41:49.177999 cemc stopAndReset
2013-06-18 18:41:49.181999 egy :asynchronousMoveTo(695)...
2013-06-18 18:41:49.184000 egy :waitWhileBusy...
2013-06-18 18:41:49.187000 egy :waitWhileBusy...
2013-06-18 18:41:49.188999 egy :getPositionCallable...
2013-06-18 18:41:49.191999 cemc :getPositionCallableFor(695.0)...
2013-06-18 18:41:49.194999 cemc 695.0 DelayableCallable:__init__(u'cemc', 695.0)...
2013-06-18 18:41:49.198999 mcs1 getPositionCallable
2013-06-18 18:41:49.201999 mcs16 getPositionCallable
2013-06-18 18:41:49.203999 mcs17 getPositionCallable
2013-06-18 18:41:49.207000 cemc 695.0  2013-06-18 18:41:49.210000DelayableCallable:call...
egy 2013-06-18 18:41:49.211999 :asynchronousMoveTo(696.0)...
cemc  2013-06-18 18:41:49.213999695.0 wait()...
egy :waitWhileBusy...
2013-06-18 18:41:49.217999 egy :waitWhileBusy...
2013-06-18 18:41:49.220999 egy :getPositionCallable...
2013-06-18 18:41:49.223000 cemc :getPositionCallableFor(696.0)...
2013-06-18 18:41:49.226000 cemc 696.0 DelayableCallable:__init__(u'cemc', 696.0)...
2013-06-18 18:41:49.230000 mcs1 getPositionCallable
2013-06-18 18:41:49.233000 mcs16 getPositionCallable
2013-06-18 18:41:49.236000 mcs17 getPositionCallable
2013-06-18 18:41:49.240000 egy :asynchronousMoveTo(697.0)...
2013-06-18 18:41:49.243000 egy :waitWhileBusy...
2013-06-18 18:41:49.244999 egy :waitWhileBusy...
2013-06-18 18:41:49.249000 egy :getPositionCallable...
2013-06-18 18:41:49.250999 cemc :getPositionCallableFor(697.0)...
2013-06-18 18:41:49.253999 cemc 697.0 DelayableCallable:__init__(u'cemc', 697.0)...
2013-06-18 18:41:49.256999 mcs1 getPositionCallable
2013-06-18 18:41:49.259999 mcs16 getPositionCallable
2013-06-18 18:41:49.262000 mcs17 getPositionCallable
2013-06-18 18:41:49.266000 egy :asynchronousMoveTo(698.0)...
2013-06-18 18:41:49.267999 egy :waitWhileBusy...
2013-06-18 18:41:49.270999 egy :waitWhileBusy...
2013-06-18 18:41:49.273000 egy :getPositionCallable...
2013-06-18 18:41:49.275000 cemc :getPositionCallableFor(698.0)...
2013-06-18 18:41:49.278000 cemc 698.0 DelayableCallable:__init__(u'cemc', 698.0)...
2013-06-18 18:41:49.280999 mcs1 getPositionCallable
2013-06-18 18:41:49.283999 mcs16 getPositionCallable
2013-06-18 18:41:49.286000 mcs17 getPositionCallable
2013-06-18 18:41:49.289999 egy :asynchronousMoveTo(699.0)...
2013-06-18 18:41:49.292000 egy :waitWhileBusy...
2013-06-18 18:41:49.293999 egy :waitWhileBusy...
2013-06-18 18:41:49.296999 egy :getPositionCallable...
2013-06-18 18:41:49.299000 cemc :getPositionCallableFor(699.0)...
2013-06-18 18:41:49.302000 cemc 699.0 DelayableCallable:__init__(u'cemc', 699.0)...
2013-06-18 18:41:49.305999 mcs1 getPositionCallable
2013-06-18 18:41:49.308000 mcs16 getPositionCallable
2013-06-18 18:41:49.311000 mcs17 getPositionCallable
2013-06-18 18:41:49.315000 egy :asynchronousMoveTo(700.0)...
2013-06-18 18:41:49.316999 egy :waitWhileBusy...
2013-06-18 18:41:49.319000 egy :waitWhileBusy...
2013-06-18 18:41:49.322000 egy :getPositionCallable...
2013-06-18 18:41:49.323999 cemc :getPositionCallableFor(700.0)...
2013-06-18 18:41:49.326999 cemc 700.0 DelayableCallable:__init__(u'cemc', 700.0)...
2013-06-18 18:41:49.329999 mcs1 getPositionCallable
2013-06-18 18:41:49.332000 mcs16 getPositionCallable
2013-06-18 18:41:49.335000 mcs17 getPositionCallable
2013-06-18 18:41:49.338999 egy :asynchronousMoveTo(701.0)...
2013-06-18 18:41:49.341000 egy :waitWhileBusy...
2013-06-18 18:41:49.344000 egy :waitWhileBusy...
2013-06-18 18:41:49.345999 egy :getPositionCallable...
2013-06-18 18:41:49.348000 cemc :getPositionCallableFor(701.0)...
2013-06-18 18:41:49.351000 cemc 701.0 DelayableCallable:__init__(u'cemc', 701.0)...
2013-06-18 18:41:49.355000 mcs1 getPositionCallable
2013-06-18 18:41:49.357000 mcs16 getPositionCallable
2013-06-18 18:41:49.359999 mcs17 getPositionCallable
2013-06-18 18:41:49.362999 egy :asynchronousMoveTo(702.0)...
2013-06-18 18:41:49.365999 egy :waitWhileBusy...
2013-06-18 18:41:49.368000 egy :waitWhileBusy...
2013-06-18 18:41:49.371000 egy :getPositionCallable...
2013-06-18 18:41:49.372999 cemc :getPositionCallableFor(702.0)...
2013-06-18 18:41:49.375000 cemc 702.0 DelayableCallable:__init__(u'cemc', 702.0)...
2013-06-18 18:41:49.378999 mcs1 getPositionCallable
2013-06-18 18:41:49.381000 mcs16 getPositionCallable
2013-06-18 18:41:49.384000 mcs17 getPositionCallable
2013-06-18 18:41:49.387000 egy :asynchronousMoveTo(703.0)...
2013-06-18 18:41:49.390000 egy :waitWhileBusy...
2013-06-18 18:41:49.391999 egy :waitWhileBusy...
2013-06-18 18:41:49.394999 egy :getPositionCallable...
2013-06-18 18:41:49.397000 cemc :getPositionCallableFor(703.0)...
2013-06-18 18:41:49.398999 cemc 703.0 DelayableCallable:__init__(u'cemc', 703.0)...
2013-06-18 18:41:49.403000 mcs1 getPositionCallable
2013-06-18 18:41:49.404999 mcs16 getPositionCallable
2013-06-18 18:41:49.407999 mcs17 getPositionCallable
2013-06-18 18:41:49.411999 egy :asynchronousMoveTo(704.0)...
2013-06-18 18:41:49.414000 egy :waitWhileBusy...
2013-06-18 18:41:49.415999 egy :waitWhileBusy...
2013-06-18 18:41:49.418999 egy :getPositionCallable...
2013-06-18 18:41:49.421000 cemc :getPositionCallableFor(704.0)...
2013-06-18 18:41:49.424000 cemc 704.0 DelayableCallable:__init__(u'cemc', 704.0)...
2013-06-18 18:41:49.427000 mcs1 getPositionCallable
2013-06-18 18:41:49.430000 mcs16 getPositionCallable
2013-06-18 18:41:49.431999 mcs17 getPositionCallable
2013-06-18 18:41:49.436000 egy :asynchronousMoveTo(705.0)...
2013-06-18 18:41:49.437999 egy :waitWhileBusy...
2013-06-18 18:41:49.440000 egy :waitWhileBusy...
2013-06-18 18:41:49.443000 egy :getPositionCallable...
2013-06-18 18:41:49.444999 cemc :getPositionCallableFor(705.0)...
2013-06-18 18:41:49.447999 cemc 705.0 DelayableCallable:__init__(u'cemc', 705.0)...
2013-06-18 18:41:49.451999 mcs1 getPositionCallable
2013-06-18 18:41:49.453999 mcs16 getPositionCallable
2013-06-18 18:41:49.456000 mcs17 getPositionCallable
2013-06-18 18:41:49.460000 cemc stopAndReset
2013-06-18 18:41:49.461999 cemc start= 694.5
2013-06-18 18:41:49.464999 cemc end= 704.5
2013-06-18 18:41:49.467999 cemc step= 1.0
2013-06-18 18:41:49.470999 cemc setTriggerPeriod(2.0)
2013-06-18 18:41:49.473999 cemc prepareForMove...
2013-06-18 18:41:49.476000 cemc getNumberTriggers= 10.0 10
2013-06-18 18:41:49.482000 cemc asynchronousMoveTo(694.45)
2013-06-18 18:41:49.493000 cemc waitWhileMoving...
2013-06-18 18:41:49.494999 cemc isMoving
2013-06-18 18:41:50.499000 cemc isMoving
2013-06-18 18:41:51.335999 cemc 696.0 DelayableCallable:call...
2013-06-18 18:41:51.338999 cemc 696.0 wait()...
2013-06-18 18:41:51.503999 cemc isMoving
2013-06-18 18:41:52.509000 cemc isMoving
2013-06-18 18:41:53.358999 cemc 697.0 DelayableCallable:call...
2013-06-18 18:41:53.361999 cemc 697.0 wait()...
2013-06-18 18:41:53.513999 cemc isMoving
2013-06-18 18:41:54.519000 cemc isMoving
2013-06-18 18:41:54.520999 cemc ...waitWhileMoving
2013-06-18 18:41:54.523999 cemc ...prepareForMove
2013-06-18 18:41:54.526999 2013-06-18 18:41:54.528000mcs1  2013-06-18 18:41:54.526999collectData()
 mcs17 collectData()
mcs16 collectData()
2013-06-18 18:41:54.533999 cemc startMove...
2013-06-18 18:41:54.536999 2013-06-18 18:41:54.536999 cemc2013-06-18 18:41:54.536999 2013-06-18 18:41:54.539000 696.0 cemc...wait() cemc
695.0 ...wait()
cemc 697.02013-06-18 18:41:54.542000 2013-06-18 18:41:54.543999 cemc getNumberTriggers= asynchronousMoveTo(704.55)
10.0 ...wait()
cemc10 
getNumberTriggers= 2013-06-18 18:41:54.549999 cemc getNumberTriggers= 10.0 2013-06-18 18:41:54.55200010.0 10
10
cemc 2013-06-18 18:41:54.556999 2013-06-18 18:41:54.558000 695.0 sleeping... cemc1.22013-06-18 18:41:54.558000  cemccemc  0.016 ...startMove
696.0 sleeping... 697.0 sleeping... 1.1842013-06-18 18:41:54.563999
5.2 3.2cemc  waitWhileMoving...
0.0209990.019999 2013-06-18 18:41:54.569999 cemc isMoving
 3.180001
5.179001
2013-06-18 18:41:55.384000 cemc 698.0 DelayableCallable:call...
2013-06-18 18:41:55.387000 cemc 698.0 start_time= 2013-06-18 18:41:54.536000
2013-06-18 18:41:55.391000 cemc getNumberTriggers= 10.0 10
2013-06-18 18:41:55.394999 cemc 698.0 sleeping... 7.2 0.858 6.342
2013-06-18 18:41:55.575999 cemc isMoving
2013-06-18 18:41:55.753999 cemc 695.0 ...DelayableCallable:call
Writing data to file:/dls/i10/data/2013/cm5934-3/i10-51745.dat
       egy         mcs1    mcs16     mcs17
694.601437    100000000        0    141134
2013-06-18 18:41:56.581000 cemc isMoving
2013-06-18 18:41:57.378000 cemc 699.0 DelayableCallable:call...
2013-06-18 18:41:57.381000 cemc 699.0 start_time= 2013-06-18 18:41:54.536000
2013-06-18 18:41:57.384999 cemc getNumberTriggers= 10.0 10
2013-06-18 18:41:57.390000 cemc 699.0 sleeping... 9.2 2.852999 6.347001
2013-06-18 18:41:57.585999 cemc isMoving
2013-06-18 18:41:57.756999 cemc 696.0 ...DelayableCallable:call
695.576888    100000000        0    141090
2013-06-18 18:41:58.589999 cemc isMoving
2013-06-18 18:41:59.384000 cemc 700.0 DelayableCallable:call...
2013-06-18 18:41:59.388000 cemc 700.0 start_time= 2013-06-18 18:41:54.536000
2013-06-18 18:41:59.391000 cemc getNumberTriggers= 10.0 10
2013-06-18 18:41:59.394999 cemc 700.0 sleeping... 11.2 4.858 6.342
2013-06-18 18:41:59.594000 cemc isMoving
2013-06-18 18:41:59.756000 cemc 697.0 ...DelayableCallable:call
696.648572    100000000        0    141233
2013-06-18 18:42:00.598999 cemc isMoving
2013-06-18 18:42:01.384999 cemc 701.0 DelayableCallable:call...
2013-06-18 18:42:01.388000 cemc 701.0 start_time= 2013-06-18 18:41:54.536000
2013-06-18 18:42:01.391000 cemc getNumberTriggers= 10.0 10
2013-06-18 18:42:01.394999 cemc 701.0 sleeping... 13.2 6.858999 6.341001
2013-06-18 18:42:01.602999 cemc isMoving
2013-06-18 18:42:01.743000 cemc 698.0 ...DelayableCallable:call
697.652006    100000000        0    141019
2013-06-18 18:42:02.607000 cemc isMoving
2013-06-18 18:42:03.371000 cemc 702.0 DelayableCallable:call...
2013-06-18 18:42:03.374000 cemc 702.0 start_time= 2013-06-18 18:41:54.536000
2013-06-18 18:42:03.377000 cemc getNumberTriggers= 10.0 10
2013-06-18 18:42:03.381000 cemc 702.0 sleeping... 15.2 8.845 6.355
2013-06-18 18:42:03.611000 cemc isMoving
2013-06-18 18:42:03.743999 cemc 699.0 ...DelayableCallable:call
698.697947    100000000        0    140911
2013-06-18 18:42:04.615999 cemc isMoving
2013-06-18 18:42:05.371999 cemc 703.0 DelayableCallable:call...
2013-06-18 18:42:05.375000 cemc 703.0 start_time= 2013-06-18 18:41:54.536000
2013-06-18 18:42:05.378000 cemc getNumberTriggers= 10.0 10
2013-06-18 18:42:05.381999 cemc 703.0 sleeping... 17.2 10.845999 6.354001
2013-06-18 18:42:05.619999 cemc isMoving
2013-06-18 18:42:05.743000 cemc 700.0 ...DelayableCallable:call
699.824377    100000000        0    140937
2013-06-18 18:42:06.625000 cemc isMoving
2013-06-18 18:42:07.371999 cemc 704.0 DelayableCallable:call...
2013-06-18 18:42:07.375000 cemc 704.0 start_time= 2013-06-18 18:41:54.536000
2013-06-18 18:42:07.378999 cemc getNumberTriggers= 10.0 10
2013-06-18 18:42:07.381999 cemc 704.0 sleeping... 19.2 12.845999 6.354001
2013-06-18 18:42:07.628999 cemc isMoving
2013-06-18 18:42:07.743000 cemc 701.0 ...DelayableCallable:call
700.875296    100000000        0    141516
2013-06-18 18:42:08.634000 cemc isMoving
2013-06-18 18:42:09.371999 cemc 705.0 DelayableCallable:call...
2013-06-18 18:42:09.375000 cemc 705.0 start_time= 2013-06-18 18:41:54.536000
2013-06-18 18:42:09.378000 cemc getNumberTriggers= 10.0 10
2013-06-18 18:42:09.381999 cemc 705.0 sleeping... 21.2 14.845 6.355
2013-06-18 18:42:09.638000 cemc isMoving
2013-06-18 18:42:09.740999 cemc 702.0 ...DelayableCallable:call
701.926549    100000000        0    141590
2013-06-18 18:42:10.641999 cemc isMoving
2013-06-18 18:42:11.645999 cemc isMoving
2013-06-18 18:42:11.742000 cemc 703.0 ...DelayableCallable:call
703.007399    100000000        0    141346
2013-06-18 18:42:12.650000 cemc isMoving
2013-06-18 18:42:13.654999 cemc isMoving
2013-06-18 18:42:13.743000 cemc 704.0 ...DelayableCallable:call
704.063798    100000000        0    141556
2013-06-18 18:42:14.660000 cemc isMoving
2013-06-18 18:42:15.664000 cemc isMoving
2013-06-18 18:42:15.742000 cemc 705.0 ...DelayableCallable:call
705.002786    100000000        0    141583
2013-06-18 18:42:16.667999 cemc isMoving
2013-06-18 18:42:17.671999 cemc isMoving
2013-06-18 18:42:18.676000 cemc isMoving
2013-06-18 18:42:19.680999 cemc isMoving
2013-06-18 18:42:20.686000 cemc isMoving
2013-06-18 18:42:21.690000 cemc isMoving
2013-06-18 18:42:22.694000 cemc isMoving
2013-06-18 18:42:22.697000 cemc ...waitWhileMoving
2013-06-18 18:42:22.700000 mcs1 atScanLineEnd
2013-06-18 18:42:22.701999 mcs16 atScanLineEnd
2013-06-18 18:42:22.704999 mcs17 atScanLineEnd
Exception
(most recent call last):
  File "<input>", line 1, in <module>
  File "/dls_sw/i10/software/gda_versions/gda_8.30a/workspace_git/gda-core.git/uk.ac.gda.core/scripts/gdascripts/scan/concurrentScanWrapper.py", line 151, in __call__
    scan.runScan()
  File "/dls_sw/i10/software/gda_versions/gda_8.30a/workspace_git/gda-core.git/uk.ac.gda.core/scripts/gdascripts/scan/concurrentScanWrapper.py", line 151, in __call__
    scan.runScan()
  File "/dls_sw/i10/software/gda/i10-config/scripts/scannable/continuous/energy.py", line 236, in atScanEnd
    raise Exception()
Exception
>>>pgm_energy.speed
0.5
>>>pgm_energy.speed = 20
>>>cvscan egy 695 705 .1 mcs1 mcs16 mcs17 .2
...
>>>pgm_energy.speed
0.5
"""