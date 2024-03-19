
#run "beamline/beamCur.py"
#run "beamline/BindScannables.py"
#run "beamline/BindScannablesDelayed.py"
#run "beamline/average.py"
#run "beamline/Virtual_Detectors.py"
#run "beamline/VirtualMirrors.py"
run "beamline/ZPE.py"

#d7current.setUpperThreshold(9.5)
#d7average.setUpperThreshold(9.5)
#dj7current.setUpperThreshold(9.5)
#dj7average.setUpperThreshold(9.5)
#d3current.setUpperThreshold(9.5)
#d3average.setUpperThreshold(9.5)
dj9current.setUpperThreshold(9.5)
dj9average.setUpperThreshold(9.5)

#d7current.setAutoGain(False)
#d7average.setAutoGain(False)
#dj7current.setAutoGain(False)
#dj7average.setAutoGain(False)
#d3current.setAutoGain(False)
#d3average.setAutoGain(False)
dj9current.setAutoGain(False)
dj9average.setAutoGain(False)

smx.setUpperGdaLimits(6500)
smx.setLowerGdaLimits(-7000)
smy.setLowerGdaLimits(-7000)
smy.setUpperGdaLimits(6500)
smz.setUpperGdaLimits(7000)
smz.setLowerGdaLimits(-7500)

ssx.setUpperGdaLimits(6500)
ssx.setLowerGdaLimits(-7000)
ssy.setLowerGdaLimits(-7000)
ssy.setUpperGdaLimits(6500)
ssz.setUpperGdaLimits(7000)
ssz.setLowerGdaLimits(-7500)

print 'ran masterj'
