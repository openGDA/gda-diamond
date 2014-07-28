#! /usr/bin/python -tt

import sys, os
import string
from optparse import OptionParser
import fnmatch
import math

usage = "%s file1 file2 ... fileN > output_filename"
parser = OptionParser(usage % "%prog")

#parser.add_option("-m", "--mythen", action="store_true", dest="mythen", help="Sum  mythen frame data taking at the same delta position.")
#parser.add_option("-r", "--rebinned", action="store_false", dest="mythen", help="Sum rebinned mythen data", default=True)

(options, args) = parser.parse_args()

def read_mythen_file(filename):
	f = open(filename, "r")
	lines = f.readlines()
	f.close()
	lines = map(string.split, map(string.strip, lines))
#	if options.mythen:
	lines = [(float(x[0]), float(x[1]), float(x[2])) for x in lines]
#	else:
#		lines = [(float(x[0]), float(x[1])) for x in lines]
	return lines

def sum_datasets(datasets):
	#min_angle = find_min_angle_across_all_datasets(datasets)

	# do slotting (slot number -> angle, counts)
	angle_data = {}
	count_data = {}
	error_data={}
	for dataset in datasets:
		datapoint=0
		for line in dataset:
			if datapoint not in angle_data:
				angle_data[datapoint] = []
			angle_data[datapoint] += [line[0]]
			if datapoint not in count_data:
				count_data[datapoint] = []
			count_data[datapoint] += [line[1]]
			if datapoint not in error_data:
				error_data[datapoint] = []
			error_data[datapoint] += [line[2]]
			datapoint += 1
	
	datapoints = angle_data.keys()
	min_point, max_point = (min(datapoints), max(datapoints))

	# create new dataset (angle -> count)
	new_dataset = []
	for datapoint in range(min_point, max_point+1):
		angles = angle_data[datapoint]
		avg_angle = sum(angles)*1.0/len(angles)
		counts = count_data[datapoint]
		sum_count = sum(counts)
		error_squared=0.0
		for error in error_data[datapoint]:
			error_squared += error * error
		sum_error = math.sqrt(error_squared)
		new_dataset.append((avg_angle, sum_count, sum_error))

	return new_dataset

if len(args) == 0:
	print >>sys.stderr, "usage: %s" % (usage % "mythensum.py")
	sys.exit(1)
	
if len(args) == 1 and str(args[0]).find("*") != -1:
	args = fnmatch.filter(os.listdir('.'), args)
#print args
datasets = map(read_mythen_file, args)
summed_data = sum_datasets(datasets)

# format of count (integer or float) depends on merging function used
output_format = "%f %f %f"

for line in summed_data:
	print output_format % line
