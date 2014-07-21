#! /usr/bin/python -tt
'''
Created on 24 Feb 2014

@author: fy65
'''
import fnmatch
from optparse import OptionParser
import os
import sys

from mythen.data.reduction.MythenDataReduction import DataReduction

usage = "%s [options] file1.raw ... fileN.raw"
parser = OptionParser(usage % "%prog")

parser.add_option("-d", "--detectorPosition", type="float", dest="detectorPosition", help="set detector position at which the raw data are taken")
parser.add_option("-o", "--outputDirectory", type="string", dest="outputDirectory", help="set the output data directory for this program")
parser.add_option("-c", "--correctFlatField", action="store_true", dest="flatField", help="apply flat field correction")
parser.add_option("-n", "--notCorrectFlatField", action="store_false", dest="flatField", help="not apply flat field correction", default="True")
parser.add_option("-f", "--flatFieldFile", type="string", dest="flatFieldFile", help="set flat field file to use for calibration", default="/dls_sw/i11/software/mythen/diamond/flatfield/current_flat_field_calibration")
parser.add_option("-b", "--badChannelFile", type="string", dest="badChannelFile", help="set bad channel file for correction", default="/dls_sw/i11/software/mythen/diamond/calibration/badchannel_detector.list")
parser.add_option("-a", "--angularConversionFile", type="string", dest="angularConversionFile", help="set angular calibration file", default="/dls_sw/i11/software/mythen/diamond/calibration/ang.off")

(options, args) = parser.parse_args()

datareduction=DataReduction()
if options.flatField:
    datareduction.setFlatFieldFile(options.flatFieldFile)
else:
    datareduction.setFlatFieldFile(None)
datareduction.setBadChannelFile(options.badChannelFile)
datareduction.setAngularCalibrationFile(options.angularConversionFile)

if len(args) == 0:
    print >>sys.stderr, "usage: %s" % (usage % "datareduction.py")
    sys.exit(1)
    
outputDir=""
if options.outputDirectory is None:
    outputDir='.' # current directory
else:
    outputDir=options.outputDirectory

if len(args) == 1 and str(args[0]).find("*") != -1:
    args = fnmatch.filter(os.listdir('.'), args)
#print fileargs

output_format = "%f %d %d %d\n"
print_format="%f %d %d %d"
for rawfile in args:
    datasets=[]
    print "process file " + str(rawfile)
    if options.detectorPosition is None:
        datasets = datareduction.reprocess(rawfile)
    else:
        datasets= datareduction.process(rawfile,  options.detectorPosition)
    outputFilename=outputDir+"/"+str(rawfile).split(".")[0]+"_reprocessed.dat"
    print "write corrected data to file " + str(outputFilename)
    f=open(outputFilename, "w")
    for line in datasets:
        f.write(output_format % (line[0], int(line[1]), int(line[2]), int(line[3])))
        #print print_format % (line[0], int(line[1]), int(line[2]), int(line[3]))
    f.flush()
    f.close()

