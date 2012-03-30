'''
Tool which extracts the data out of a nexus file and into a set of ascii files
'''
import datetime
import re
import os
import sys
import numpy, nxs
import logging

import shutil

class edxd_data_extractor:

	def __init__(self,filename) :
		print "Initialising Extractor"
		self.filename = filename
		self.nexusfile = nxs.open(self.filename)

		# initialy open the file
		# ok navigate to the correct place in the structure
		entries = self.nexusfile.getentries()
		if len(entries) != 1:
			self.logger.warning("unexpected number of root entries, reading first one only")
		
		# open entry1
		self.nexusfile.opengroup(entries.keys()[0])
		entries = self.nexusfile.getentries()

		if not "instrument" in entries:
			raise RuntimeError("No instrument definition missing")

		# open the instrument data
		self.nexusfile.opengroup("instrument")

	def extract_all(self, path, filename) :
		print "Starting Extraction of all elements"
		entries = self.nexusfile.getentries()
		count = 0;
		for entry in [a for a in entries if (a.find("EDXD") >= 0)] :
			print "Extracting ", entry
			# make the direcorty
			elementpathname = os.path.join(path,entry)	
			os.mkdir(elementpathname)
			self.extract(entry,elementpathname, filename)
			count += 1
		if count==0:
			print " No EDXD element to extract"

	def extract(self, element, path, filename) :

		self.nexusfile.opengroup(element)

		q = self.extract_q()
		print "q is ", q

		e = self.extract_energy()
		print "e is ", e

		shape = self.extract_data_shape()
		#print "shape is ", shape

		if len(shape) == 2 :
			print "Processing 1D scan"
			for x in range(shape[0]) :
				point = [x]
				#print "point ", point
				data = self.extract_data_point(point, shape[-1])[0,:]
				self.write_file(filename, path, point, e, q, data) 

		if len(shape) == 3 :
			print "Processing 2D scan"
			for x in range(shape[0]) :
				for y in range(shape[1]) :
					point = [x,y]
					#print "point ", point
					data = self.extract_data_point(point, shape[-1])[0,:]
					self.write_file(filename, path, point, e, q, data) 

		if len(shape) == 4 :
			print "Processing 3D scan"
			for x in range(shape[0]) :
				for y in range(shape[1]) :
					for y in range(shape[2]) :
						point = [x,y,z]
						#print "point ", point
						data = self.extract_data_point([x,y,z], shape[-1])[0,:]
						self.write_file(filename, path, point, e, q, data) 

		self.nexusfile.closegroup()
		

	def write_file(self, filename, path, point, e, q, data) :
		
		fullname = "%s_%s.dat" % (filename, "_".join([("%04d"%x) for x in point]))
		
		file = open(os.path.join(path,fullname), "w")

		lines = []

		for i in range(len(e)) :
			lines.append("%5d %.8g %.8g %.8g" % (i,e[i],q[i],data[i]))

		file.write("\n".join(lines))

		file.close


	def extract_q(self) :

		# open the q group, get the data
		
		self.nexusfile.opendata("edxd_q")

		# return the result 
		q_axis = self.nexusfile.getdata()

		# close the path
		self.nexusfile.closedata()

		return q_axis


	def extract_energy(self) :

		# open the q group, get the data
		
		self.nexusfile.opendata("edxd_energy_approx")

		# return the result 
		energy_axis = self.nexusfile.getdata()

		# close the path
		self.nexusfile.closedata()

		return energy_axis


	def extract_data_shape(self) :

		# open the next group, get the data
		
		self.nexusfile.opendata("data")

		# return the result 
		info = self.nexusfile.getinfo()

		# close the path
		self.nexusfile.closedata()

		return info[0]

	def extract_data_point(self, point, length) :

		# open the next group, get the data
		#print "point is", point
		#print "length is", length
		
		self.nexusfile.opendata("data")

		startpoint = point+[0]
		#print "startpoint is ", startpoint
		datarange = []
		for i in range(len(point)):
			datarange.append(1)
		datarange.append(length)
		#print "datarange is ", datarange

		# put it in a dictionary, 
		#data = self.nexusfile.getdata()
		data = self.nexusfile.getslab(startpoint, datarange)

		# close the path
		self.nexusfile.closedata()

		return data


    
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
	data_extractor.extract_all(outpath,"test")

	print "Sucsessfully Extracted the data"



