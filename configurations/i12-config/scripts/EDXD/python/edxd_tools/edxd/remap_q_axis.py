'''
Quick tool to allow for the modification of the q axis of edxd files
given a file with the correct calibration in.  Generaly for use when 
things go wrong somehow.
'''
import datetime
import re
import os
import sys
import numpy, nxs
import logging

import shutil

class edxd_q_extractor:

	def __init__(self,filename) :
		self.filename = filename
		self.nexusfile = nxs.open(self.filename)

	def extract(self) :

		q_axis = {}
	
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
		entries = self.nexusfile.getentries()

		for entry in [a for a in entries if (a.find("EDXD") >= 0)] :
			
			# open the next group, get the data
			self.nexusfile.opengroup(entry)
			self.nexusfile.opendata("edxd_q")

			# put it in a dictionary, 
			q_axis[entry] = self.nexusfile.getdata()

			# close the path
			self.nexusfile.closedata()
			self.nexusfile.closegroup()

		# finaly make a check
		if not len(q_axis) == 24 :
			print "Only %d elements found, the calibration file '%s' may not be good" % (len("q_axis"),self.filename)

		return q_axis


class edxd_q_injector:

	def __init__(self,filename) :
		self.filename = filename
		self.nexusfile = nxs.open(self.filename, 'rw')

	def inject(self, q_axis_values) :
	
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
		entries = self.nexusfile.getentries()

		for entry in [a for a in entries if (a.find("EDXD") >= 0)] :
			
			# open the next group, get the data
			self.nexusfile.opengroup(entry)
					
			self.nexusfile.opendata("edxd_q")
			
			# now try to replace the data with the data from the dictionary thats passed in
			try :
				self.nexusfile.putdata(q_axis_values[entry])
			except KeyError :
				raise RuntimeError("Cannot find EDXD element %s in the correct calibration file" % entry) 

			# close the path
			self.nexusfile.closedata()
			self.nexusfile.closegroup()

    
if __name__ == '__main__':
	print "EDXD q remapping software"

	if len(sys.argv) != 4 :
		print "\n Usage :"
		print " remap_q_axis file_to_correct.nxs file_with_correct_q_values.nxs corrected_output_file.nxs\n"
		sys.exit(0)

	datafile = sys.argv[1]  
	qaxisfile = sys.argv[2] 
	outfile = sys.argv[3] 

	if not os.path.exists(datafile) :
		raise RuntimeError("input file '%s' does not exist" % datafile)

	if not os.path.exists(qaxisfile) :
		raise RuntimeError("QAxis file '%s' does not exist" % qaxisfile)

	print "File to correct %s" % datafile  
	print "Correct q axis file %s" % qaxisfile 
	print "Output file %s" % outfile

	# first copy the incorrect file into the output file
	shutil.copy(datafile, outfile)

	# now extracty the q values from the good file
	q_axis_extractor = edxd_q_extractor(qaxisfile)
	q_axis = q_axis_extractor.extract()

	# now pop those values back into the copied version
	q_axis_injector = edxd_q_injector(outfile)
	q_axis = q_axis_injector.inject(q_axis)

	print "Sucsessfully applied Q axis"



