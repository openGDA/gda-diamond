'''
A template script to do an UNEVENLY spaced scan data point with DIFFERENT exposure time at each scan data point. 
It uses a detector exposure control scannable to modify detector expsoure time at each scan data point, so the 
exposure time given after detector object in scan command will be override.

It uses PATH scan idea, and support multiple image collection at each data point if the detector is an area detector.

Created on 08 Jan 2019

@author: fy65
'''
from utils.dRangeUtil import drange
from scan.miscan import miscan
from scannables.DetectorExposureChanger import DetectorExposureScannable

Region_1_points=drange(2.597, 4.78, 0.1)
Region_1_exposures=[0.1 for x in Region_1_points]
#print "Region_1_points: ",Region_1_points

Region_2_points=drange(5.0, 10.001, 0.04728)
Region_2_exposures=[1.0 for x in Region_2_points]
#print "Region_2_points: ",Region_2_points

Region_3_points=drange(5.0, 10.001, 0.5)
Region_3_exposures=[0.2 for x in Region_3_points]
#print "Region_3_points: ",Region_3_points

all_regions_points=Region_1_points + Region_2_points + Region_3_points
all_regions_exposures=Region_1_exposures + Region_2_exposures + Region_3_exposures

path=zip(all_regions_points, all_regions_exposures)
print path
scanpath=[]
for l in path:
    scanpath.append(list(l))
scanpath=tuple(scanpath)
print "scan path: ", scanpath

# replace 'pv' with the actual detector's Exposure Time PV string
detector_exposure_scannable= DetectorExposureScannable('detector_exposure_scannable', "pv")

# replace 'motor' with scannable which you want to scan with, 'detector' with the detector you want to collect data from.
miscan((motor,detector_exposure_scannable), scanpath, detector, 1.0)  # @UndefinedVariable
