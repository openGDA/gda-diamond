#! /usr/bin/python -tt
'''append multiple files' contents into one file'''

import sys, os
from optparse import OptionParser
import fnmatch
import shutil

usage = "%s file1 file2 ... fileN output_filename"
parser = OptionParser(usage % "%prog")

(options, args) = parser.parse_args()

if len(args) == 0:
	print >>sys.stderr, "usage: %s" % (usage % "fileappender.py")
	sys.exit(1)
	
filenames=[]
if str(args[0]).find("*") != -1:
	filenames = fnmatch.filter(os.listdir('.'), args[0])
else:
	filenames = args[:-1]
	
#concatenate files into one.
fdst=open(args[-1], "w")
for each in filenames:
	fsrc=open(each, "r")
	shutil.copyfileobj(fsrc, fdst)
	fsrc.close()
fdst.close()
