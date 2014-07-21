#! /usr/bin/python -tt

import sys
import string
from optparse import OptionParser
import math

usage = "%s [OPTIONS] files... > output_filename"
parser = OptionParser(usage % "%prog")
parser.add_option("-b", "--binsize", action="store", dest="binsize", type="float", help="Bin size in degrees (default: 0.004)", default=0.004, metavar="DEGREES")
parser.add_option("-f", "--function", action="store", dest="function", help="Function to use for merging datasets - 'max' (default) or 'mean'", default="max")
parser.add_option("-g", "--fillgaps", action="store_true", dest="fillgaps", help="Fill gaps in binned data (default: off)", default=False)

(options, args) = parser.parse_args()

def read_mythen_file(filename):
	f = open(filename, "r")
	lines = f.readlines()
	f.close()
	lines = map(string.split, map(string.strip, lines))
	lines = [(float(x[0]), float(x[1]), float(x[2])) for x in lines]
	return lines

def bin_datasets(datasets, binsize, fillgaps, function):
	min_angle = find_min_angle_across_all_datasets(datasets)

	# do binning (bin number -> counts)
	binned_data = {}
	binned_error={}
	for dataset in datasets:
		for line in dataset:
			bin = determine_bin(line[0], min_angle, options.binsize)
			if bin not in binned_data:
				binned_data[bin] = []
			binned_data[bin] += [line[1]]
			if bin not in binned_error:
				binned_error[bin] = []
			binned_error[bin] += [line[2]]

	bins = binned_data.keys()
	min_bin, max_bin = (min(bins), max(bins))

	# create new dataset (angle -> count)
	new_dataset = []
	for bin in range(min_bin, max_bin+1):
		bin_angle = min_angle + bin * binsize
		if bin in binned_data:
			counts = binned_data[bin]
			errors = binned_error[bin]
			if function == "mean":
				count = sum(counts) * 1.0 / len(counts)
				e_squared=0
				for e in errors:
					e_squared +=e*e
				error = math.sqrt(e_squared)*1.0/len(errors)
			elif function == "max":
				count = max(counts)
				index = counts.index(count)
				error = errors[index]
			new_dataset.append((bin_angle, count, error))
		elif fillgaps:
			new_dataset.append((bin_angle, 0))

	return new_dataset

def find_min_angle_across_all_datasets(datasets):
	min_angle = datasets[0][0][0]
	for dataset in datasets:
		for line in dataset:
			if line[0] < min_angle:
				min_angle = line[0]
	return min_angle

def determine_bin(angle, min_angle, binsize):
	return int((angle - min_angle) / binsize)
	
if len(args) == 0:
	print >>sys.stderr, "usage: %s" % (usage % "mythenbin.py")
	sys.exit(1)

if options.function not in ("mean", "max"):
	print >>sys.stderr, "don't recognise function '%s' - use 'mean' or 'max'" % options.function
	sys.exit(1)

datasets = map(read_mythen_file, args)
binned_data = bin_datasets(datasets, options.binsize, options.fillgaps, options.function)

# format of count (integer or float) depends on merging function used
if options.function == "max":
	output_format = "%f %f %f"
else:
	output_format = "%f %f %f"

for line in binned_data:
	print output_format % line
