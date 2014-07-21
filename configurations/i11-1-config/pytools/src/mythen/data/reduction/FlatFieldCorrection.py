# -*- coding: utf-8 -*-
"""
Flat field correction module which handles flat field file is none.

Created on Fri Feb 21 15:07:07 2014

@author: fy65
"""
import math
from BadChannelCorrection import getBadChannelList, badChannelCorrection

def calculateFlatFieldScalingFactors(flatFieldData):
    ''' the input flatFieldData is a list of tuples with 1st column is channel number, 2nd column is counts'''
    if flatFieldData is None:
        return None
    flatFieldMean=0.0
    for line in flatFieldData:
        flatFieldMean += float(line[1]) #second column is count
    flatFieldMean = float(flatFieldMean)/float(len(flatFieldData))
    corrections=[]
    for line in flatFieldData:
        corrections.append(flatFieldMean/float(line[1]))
    return corrections

def getFlatFieldData(flatFieldFilename, badChannelFilename):
    ''' remove bad channels from flat field raw data file, return a list of bad channel corrected raw data
        arguments: 1. flat field raw data file name
                   2. bad channel file name
    '''
    bad_channel_list = getBadChannelList(badChannelFilename)
    if flatFieldFilename is None:
        return None
    return badChannelCorrection(flatFieldFilename, bad_channel_list)
   
def flatFieldCorrection(badChannelCorrectedRawData, flatFieldCorrections):
    ''' apply flat field correction to raw data list, return a list of tuples (channel-number, count, error)
        required parameters:
            1. raw data to be corrected,
            2. flat field correction scaler factors - if None, no flat field correction is applied
    '''
    results=[]
    if flatFieldCorrections is None: #No flat field correction
        for line in badChannelCorrectedRawData:
            results.append((line[0], float(line[1]), int(math.sqrt(line[1]))))
    else: 
        data=zip(badChannelCorrectedRawData, flatFieldCorrections)
        for line in data:
            count=line[0][1]*float(line[1])
            results.append((line[0][0], count, int(math.sqrt(count))))
            #print line[0][0], count, int(math.sqrt(count))
    return results

