'''
Bad channel correction module, which handle the case of no bad channel file.
Created on 21 Feb 2014

@author: fy65
'''
from DataFileReader import read_bad_cahnnel_data, read_raw_data

def badChannelCorrection(rawDataFile, badChannels):
    '''remove bad channels from raw data list, if None, just return original raw data as list of tuples (channel-number, count)
        arguments: 1. raw data file name;
                   2. list of bad channels
    '''
    raw_data = read_raw_data(rawDataFile)
    results=[]
    for line in raw_data:
        if badChannels is None or not line[0] in badChannels:
            results.append(line)
    return results

def getBadChannelList(badChannelFilename):
    ''' return a list of bad channels from bad channel data file, can be None if no file provided.
        arguments: 1. bad channel filename.
    '''
    if badChannelFilename is None:
        return None
    return read_bad_cahnnel_data(badChannelFilename)
        