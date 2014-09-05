
run "beamline/beamCur.py"
run "beamline/BindScannables.py"
run "beamline/average.py"
run "beamline/Virtual_Detectors.py"
run "beamline/VirtualMirrors.py"

d7current.setUpperThreshold(0.95)
d7average.setUpperThreshold(0.95)
dj7current.setUpperThreshold(0.95)
dj7average.setUpperThreshold(0.95)
d3current.setUpperThreshold(0.95)
d3average.setUpperThreshold(0.95)
d9current.setUpperThreshold(0.95)
d9average.setUpperThreshold(0.95)

d7current.setAutoGain(False)
d7average.setAutoGain(False)
dj7current.setAutoGain(False)
dj7average.setAutoGain(False)
d3current.setAutoGain(False)
d3average.setAutoGain(False)
d9current.setAutoGain(False)
d9average.setAutoGain(False)