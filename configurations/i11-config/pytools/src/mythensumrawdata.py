#! /usr/bin/python -tt

import sys, os
import string
from optparse import OptionParser
import fnmatch
import math
PSD_FLATFIELD_DIR="/dls_sw/i11/software/mythen/diamond/flatfield"

usage = "%s file1 file2 ... fileN > output_filename"
parser = OptionParser(usage % "%prog")

(options, args) = parser.parse_args()

def read_raw_data(filename):
    ''' Reads the lines from the specified Mythen raw data file, 
    and returns an array of (channel, count) tuples'''
    f=open(filename,"rb")
    lines=f.readlines()
    f.close()
    return [tuple(map(int, l.strip().split(" "))) for l in lines]

def sumRawData(data):
    dataset=[]
    for channel in range(len(data[0])):
        values = [data[i][channel][1] for i in range(len(data))]
        dataset.append((channel, sum(values)))
    return dataset


if len(args) == 0:
	print >>sys.stderr, "usage: %s" % (usage % "mythensumrawdata.py")
	sys.exit(1)
	
if len(args) == 1 and str(args[0]).find("*") != -1:
	args = fnmatch.filter(os.listdir('.'), args)
#print args
datasets = map(read_raw_data, args)
summed_data = sumRawData(datasets)

# format of count (integer or float) depends on merging function used
output_format = "%d %d"

for line in summed_data:
	print output_format % line

