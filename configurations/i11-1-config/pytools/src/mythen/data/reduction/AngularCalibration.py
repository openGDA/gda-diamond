'''
implement method to provide module-based angular conversion function for mythen detector data.
Created on 21 Feb 2014

@author: fy65
'''
GLOBAL_OFFSET=0.0
BEAMLINE_OFFSET=0.08208

from DataFileReader import read_angular_calibration_data
import math

def applyAngularConversion(angularCalibrationFile, detectorPosition, channeldata):
    ''' convert channel number to actual angle in degree based on angular calibration file provided, return a list of tuples (angle, count, error, channel)
        required input parameters:
            1. angular calibration file, if None raise exception
            2. detector position at which the raw data is taken, if None raise exception
            3. flat field corrected data list of tuples (channel-number, count, error) 
    '''
    if angularCalibrationFile is None:
        raise Exception("Angular calibration file is not available for converting channel numbers to angles.")
    if detectorPosition is None:
        raise Exception("PSD detector position in degree must be provided for angular conversion to proceed.")
    angular_calibration_data = read_angular_calibration_data(angularCalibrationFile)
    results=[]
    for data in channeldata:
        moduleindex=data[0]/1280
        channelmodule=data[0]%1280
        moduleparameters=angular_calibration_data[moduleindex]
        centre=moduleparameters[0]
        conversion=moduleparameters[1]
        offset=moduleparameters[2]
        angle=2.404350+offset+math.degrees(math.atan((channelmodule-centre)*conversion))+detectorPosition+GLOBAL_OFFSET+BEAMLINE_OFFSET
        results.append((angle, data[1], data[2], data[0]))
    return results
