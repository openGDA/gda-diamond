#! /usr/bin/python -tt
'''
merge columns from several data files together into a single file horizontally, i.e. side-by-side columns
Created on 25 Feb 2011

@author: fy65
'''
import sys, os
import string
from optparse import OptionParser
import fnmatch

usage = "%s file1 file2 ... fileN  output_filename"
parser = OptionParser(usage % "%prog")

(options, args) = parser.parse_args()

def read_data_file(filename):
    print "reading file %s" % filename
    f = open(filename, "r")
    lines = f.readlines()
    f.close()
    lines = map(string.strip, lines)
    return lines

if len(args) == 0:
    print >>sys.stderr, "usage: %s" % (usage % "mergecolumns.py")
    sys.exit(1)
    
filenames=[]
if str(args[0]).find("*") != -1:
    filenames = fnmatch.filter(os.listdir('.'), args[0])
else:
    filenames = args[:-1]

datasets = map(read_data_file, filenames)
result=zip(*tuple(datasets))
    
# format of count (integer or float) depends on merging function used
output_format = "%s\t%s\n"

file=open(args[-1], "w")
for line in result:
    for each in line:
        file.write("%s\t"%each)
    file.write('\n')
#file.write('\n'.join('%s\t%s' % x for x in result))
file.close()