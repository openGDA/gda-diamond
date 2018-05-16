'''
Tool which extracts the data out of a nexus file and into a set of ascii files
'''
import datetime
import re
import os
import sys
import numpy
import logging
import h5py

import shutil

class edxd_data_extractor:

	def __init__(self,filename) :
		print "Initialising Extractor"
		self.filename = filename
		self.nexusfile = h5py.File(self.filename,'r')
		

	def extract_all(self, path, filename) :
		print "Starting Extraction of all elements"
		entries = self.nexusfile['entry1/instrument/'].keys()
		count = 0
		for entry in [a for a in entries if (a.find("EDXD") >= 0)] :
			print "Extracting ", entry
			# make the direcorty
			elementpathname = os.path.join(path,entry)	
			if not os.path.exists(elementpathname):
				os.mkdir(elementpathname)
			self.extract(entry,elementpathname, filename)
			count += 1
		if count==0:
			print " No EDXD element to extract"

	def extract(self, element, path, input_filename) :

		q = self.nexusfile['entry1/instrument/%s/edxd_q'%(element)]

		e = self.nexusfile['entry1/instrument/%s/edxd_energy_approx'%(element)]

		data = self.nexusfile['entry1/instrument/%s/data'%(element)]

		filename = "%s_%s" % (input_filename, element)

		if len(data.shape) == 2 :
			print "Processing 1D scan"
			for x in range(data.shape[0]) :
				d = data[x,:]
				self.write_file(filename, path, [x], e, q, d) 

		if len(data.shape) == 3 :
			print "Processing 2D scan"
			for x in range(data.shape[0]) :
				for y in range(data.shape[1]) :
					d = data[x,y,:]
					self.write_file(filename, path, [x,y], e, q, d) 

		if len(data.shape) == 4 :
			print "Processing 3D scan"
			for x in range(data.shape[0]) :
				for y in range(data.shape[1]) :
					for y in range(data.shape[2]) :
						d = data[x,y,z,:]
						self.write_file(filename, path, [x,y,z], e, q, d) 

	def write_file(self, filename, path, point, e, q, data) :
		
		fullname = "%s_%s.dat" % (filename, "_".join([("%04d"%x) for x in point]))
		
		file = open(os.path.join(path,fullname), "w")

		lines = []

		for i in range(len(e)) :
			lines.append("%5d %.8g %.8g %.8g" % (i,e[i],q[i],data[i]))

		file.write("\n".join(lines))

		file.close

    
if __name__ == '__main__':
	print "EDXD extracting software"

	if len(sys.argv) != 3 :
		print "\n Usage :"
		print " extract file_name.nxs, /out/put/pathname/\n"
		sys.exit(0)

	datafile = sys.argv[1]  
	outpath = sys.argv[2] 

	if not os.path.exists(datafile) :
		raise RuntimeError("input file '%s' does not exist" % datafile)

	if not os.path.exists(outpath) :
		raise RuntimeError("out path '%s' does not exist" % outpath)

	print "File to extract %s" % datafile  
	print "Directory to extract to %s" % outpath  

	# now extract the data
	data_extractor = edxd_data_extractor(datafile)
	data_extractor.extract_all(outpath,os.path.basename(datafile).split('.')[0])

	print "Sucsessfully Extracted the data"



