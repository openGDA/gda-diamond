'''
define class that performs the data reduction process and the default correction and calibration files:
BADCHANNELLISTFILE="/dls_sw/i11/software/mythen/diamond/calibration/badchannel_detector.list"
FlatFieldDataFile="/dls_sw/i11/software/mythen/diamond/flatfield/current_flat_field_calibration"
ANGULARCONVERSIONFILE="/dls_sw/i11/software/mythen/diamond/calibration/ang.off"

Created on 24 Feb 2014

@author: fy65
'''
from BadChannelCorrection import badChannelCorrection, getBadChannelList
from FlatFieldCorrection import calculateFlatFieldScalingFactors, getFlatFieldData, flatFieldCorrection
from AngularCalibration import applyAngularConversion
from DataFileReader import read_processed_data
from AngularCalibration import BEAMLINE_OFFSET

BADCHANNELLISTFILE="/dls_sw/i11/software/mythen/diamond/calibration/badchannel_detector.list"
FlatFieldDataFile="/dls_sw/i11/software/mythen/diamond/flatfield/current_flat_field_calibration"
ANGULARCONVERSIONFILE="/dls_sw/i11/software/mythen/diamond/calibration/ang.off"

class DataReduction(object):
    '''
    objects to perform data reduction for mythen detector raw data. Applied processes include:
        1. bad channel correction - remove only, not interpolated
        2. flat field correction - scaling intensity
        3. angular conversion - from channel number to angle in degree.
    Methods available:
        1. process(rawDataFile, detectorPosition) - do the actual data reduction processes
        2. setBadChannelFile(filename), getBadChannelFile() - default to "/dls_sw/i11/software/mythen/diamond/calibration/badchannel_detector.list"
        3. setFlatFieldFile(filename), getFlatFieldFile() - default to "/dls_sw/i11/software/mythen/diamond/flatfield/current_flat_field_calibration"
        4. setAngularCalibrationFile(filename), getAngularCalibrationFile() - default to "/dls_sw/i11/software/mythen/diamond/calibration/ang.off"
        5. reprocess(rawDataFile) - re-do the actual data reduction processes, previous process data file must exist alongside of the raw data file.
    '''

    def __init__(self, badChannelFile=BADCHANNELLISTFILE, flatFieldFile=FlatFieldDataFile, angularCalibrationFile=ANGULARCONVERSIONFILE):
        '''
        Constructor with default correction and calibration filenames
        '''
        self.badChannelFile=badChannelFile
        self.flatFieldFile=flatFieldFile
        self.angularCalibrationFile=angularCalibrationFile
        
    def process(self, rawDataFile, detectorPosition):
        '''
        perform data reduction processes that convert RAW data (channel versus count) to PROCESSED data (angle versus count channel)
        inputs: 1. raw data file to be corrected,
                2. the detector position at which the raw data are collected.
        outputs: dataset which contains a list of tuple (angle, count, error, channel)
        '''
        bad_channel_corrected_data = badChannelCorrection(rawDataFile, getBadChannelList(self.badChannelFile))
        calculate_flat_field_scaling_factors = calculateFlatFieldScalingFactors(getFlatFieldData(self.flatFieldFile, self.badChannelFile))
        flat_field_corrected_data = flatFieldCorrection(bad_channel_corrected_data, calculate_flat_field_scaling_factors)
        data = applyAngularConversion(self.angularCalibrationFile, detectorPosition, flat_field_corrected_data)
        return data
    
    def reprocess(self, rawDataFile):
        ''' redo Mythen data reduction processes that convert RAW data (channel versus count) to PROCESSED data (angle versus count)
        required parameters:
            1. the raw data file to be processed
        Note: for this to work, you must already have corresponding reduced data files from this process can pick up detector position. 
        '''
        split = str(rawDataFile).split('.')[0]
        datFile=split+".dat"
        processed_data = read_processed_data(datFile)
        detectorPos=processed_data[0][0]-BEAMLINE_OFFSET
        print "PSD detector position %f" % detectorPos
        return self.process(rawDataFile, detectorPos)
        

    def setBadChannelFile(self, value):
        self.badChannelFile=value
        
    def getBadChannelFile(self):
        return self.badChannelFile
    
    def setFlatFieldFile(self,value):
        self.flatFieldFile=value
        
    def getFlatFieldFile(self):
        return self.flatFieldFile
    
    def setAngularCalibrationFile(self, value):
        self.angularCalibrationFile=value
        
    def getAngularCalibrationFile(self):
        return self.angularCalibrationFile