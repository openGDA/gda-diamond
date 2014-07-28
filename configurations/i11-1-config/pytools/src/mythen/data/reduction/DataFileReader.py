# -*- coding: utf-8 -*-
"""
methods for reading different types of Mythen data file and calibration files.

Created on Fri Feb 21 15:16:12 2014

@author: fy65
"""

def read_raw_data(filename):
    ''' Reads the lines from the specified Mythen raw data file, 
    and returns an array of (channel, count) tuples'''
    lines=readlines(filename)
    return [tuple(map(int, l.strip().split(" "))) for l in lines]

def read_processed_data(filename):
    ''' read lines from processed Mythen data file, and return a list of tuples (angle, count, error)'''
    lines=readlines(filename)
    data=[tuple(map(str, l.strip().split(" "))) for l in lines]
    results=[]
    for line in data:
        results.append((float(line[0]), int(line[1]), int(line[2])))
    return results

def read_bad_cahnnel_data(filename):
    ''' read bad channel list'''
    lines=readlines(filename)
    return [int(x) for x in lines]

def readlines(filename):
    f=open(filename,"rb")
    lines=f.readlines()
    f.close()
    return lines

def read_angular_calibration_data(filename):
    ''' read angular calibration file'''
    lines=readlines(filename)
    results = [tuple(map(str, l.strip().split(" "))) for l in lines]
    moduleConversionParameters={}
    for line in results:
        module=int(line[1])
        centre=float(line[3])
        conversion=float(line[7])
        offset=float(line[11])
        moduleConversionParameters[module]=(centre, conversion, offset)
    return moduleConversionParameters
        