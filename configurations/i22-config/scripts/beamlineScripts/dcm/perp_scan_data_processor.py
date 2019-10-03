import scisoftpy as dnp
from gda.data import NumTracker
from gda.jython import InterfaceProvider
from gda.analysis.io import NexusLoader
from math import cos
from math import acos
from math import sin
from math import radians
from gdaserver import dcm_finepitch
i22NumTracker = NumTracker("i22");
i22NumTracker.getCurrentFileNumber()

'''
The purpose of this script is to determine Mono dcm_perp positions for each energy to give fixed exit height from the monochromator
Set up:
Drive VFM and HFM out of beam
Centre S2 y blades and close gap to 0.250mm
Centre S3 y blades and close gap to 0.250mm
dcm_pitch scans done on D3 inline diode
dcm_perp scans done on D4 Inline Diode HFM position
'''
# 
# filePath = (InterfaceProvider.getPathConstructor().createFromDefaultProperty()+"/perp_parameters_"+time.strftime("%Y-%m-%d-%H_%M")+".csv")
# outfile = open(filePath,"a")
# outfile.write("File, Energy , bragg, 1/cos(bragg), dcm_perp1, dcm_perp2, dcm_perp3, pitch1, pitch2\n")
# 
# fileNumber = 509065

for x in dnp.linspace(1.14992,1.004898,20,True):
    energyPos = (12.3985/6.2695)/sin(acos((1/x)))
    print energyPos
#     pos energy energyPos
#     braggAngle = dcm_bragg.getPosition()
#     braggInRad = radians(braggAngle)
#     oneOverCosBragg = 1 / cos(braggInRad)
# 
#     
#     process1d(fileNumber)
#     dcm_perp1 = results.peak.pos
#     dcm_perp2 = results.maxval.maxpos
#     dcm_perp3 = results.edges.centre


    # save the data back out
#     # file = open(filePath,"a")
#     outfile.write("%f, %f , %f, %f, %f, %f, %f\n" % (fileNumber, energyPos,braggAngle,oneOverCosBragg,dcm_perp1, dcm_perp2, dcm_perp3))
#     fileNumber += 4

# outfile.close()
print "All done"
