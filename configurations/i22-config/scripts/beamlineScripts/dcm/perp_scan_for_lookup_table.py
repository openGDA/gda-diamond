import java
import time
import scisoftpy as dnp
from gda.data import NumTracker
from gda.data import PathConstructor
from gda.analysis.io import NexusLoader
from math import cos
from math import acos
from math import sin
from math import radians
i22NumTracker = NumTracker("i22");
i22NumTracker.getCurrentFileNumber()

'''
The purpose of this script is to determine Mono perp positions for each energy to give fixed exit height from the monochromator
Set up:
Drive VFM and HFM out of beam
Centre S2 y blades and close gap to 0.250mm
Centre S3 y blades and close gap to 0.250mm
Pitch scans done on D3 inline diode
Perp scans done on D4 Inline Diode HFM position
'''

file = open(PathConstructor.createFromDefaultProperty()+"perp_parameters_"+time.strftime("%Y-%m-%d")+".csv","a")
file.write("File, Energy , bragg, 1/cos(bragg), perp, pitch1, pitch2\n")
file.close()

for x in dnp.linspace(1.14992,1.004898,10,True):
    energyPos = (12.3985/6.2695)/sin(acos((1/x)))
    print energyPos
    pos bkeV energyPos
    pos calibrated_ID energyPos
    braggAngle = bragg.getPosition()
    braggInRad = radians(braggAngle)
    oneOverCosBragg = 1 / cos(braggInRad)
    
    pos d3filter "Inline Diode"
    pos finepitch 0
    pos pitch -26
    pos finepitch -150
    sleep(2)
    scan finepitch -150 150 1 d3d2
    go maxval
    scan perp 12.0 15.0 0.05 d3d2
    go maxval
    pos finepitch 0
    pos pitch -26
    pos finepitch -150
    sleep(2)
    scan finepitch -150 150 1 d3d2
    go maxval
    scan perp 12.0 15.0 0.05 d3d2
    go maxval
    pitchPos_start = pitch.getPosition()
    pos d3filter "Clear"
    scan perp 12.0 15.0 0.02 d4d1
    perpPosition = peak.result.pos
    pitchPos_end = pitch.getPosition()
    fileNumber = int(i22NumTracker.getCurrentFileNumber())
    
    # save the data back out
    file = open(PathConstructor.createFromDefaultProperty()+"perp_parameters_"+time.strftime("%Y-%m-%d")+".csv","a")
    file.write("%f, %f , %f, %f, %f, %f, %f\n" % (fileNumber, energyPos,braggAngle,oneOverCosBragg,perpPosition, pitchPos_start, pitchPos_end))
    file.close()

print "All done" 
