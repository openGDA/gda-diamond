#!/bin/env python2.4
#
import sys, os, re
import telnetlib
import csv
import logging
from optparse import OptionParser

#Set up the logging for this script. It write to a file /tmp/blenergise.log
logger = logging.getLogger('logger')
hdlr = logging.FileHandler('/tmp/blenergise.log')
formatter = logging.Formatter('%(filename)s %(lineno)d %(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.DEBUG)

def main():

	#constants
	mPMAC1 = "7501"
	mPMAC2 = "7503"
	
	usage = """usage: %prog [options] FILE [AXIS1 AXIS2 ... AXISn]
%prog will energise the axis AXIS1-AXISn\n as specified in arguments where AXISx\n is the EPICS PV name for the axis to energise.\n FILE defines what axis can be energised.
"""
	parser = OptionParser(usage)
	parser.add_option(	"-v", "--verbose",
						action="store_true", dest="verbose", default=False,
						help="Print more details (than necessary in most cases...)")
	parser.add_option(	"-o", "--on",
						action="store_true", dest="on", default=False,
						help="Energise axis all axes defined on command line (power on). If used with '-all' option then all axis defined in FILE are energised.")
	parser.add_option(	"-f", "--off",
						action="store_true", dest="off", default=False,
						help="Deenergise all axes defined on command line (power off). If used with '-all' option then all axis defined in FILE are deenergised.")
	parser.add_option(	"-a", "--all",
						action="store_true", dest="all", default=False,
						help="Energise or deenergise all axis. Use with '-on' or '-off' option.")

	(options, args) = parser.parse_args()

	#Set up the logging for this script. It write to a file /tmp/blenergise.log
	logger = logging.getLogger('logger')
	hdlr = logging.FileHandler('/tmp/blenergise.log')
	print "Log information is in /tmp/blenergise.log"
	formatter = logging.Formatter('%(filename)s %(lineno)d %(asctime)s %(levelname)s %(message)s')
	hdlr.setFormatter(formatter)
	logger.addHandler(hdlr) 
	logger.setLevel(logging.DEBUG)
	
	if (options.verbose):
		print "Reading file:", args[0] 

	#logger.debug("Reading file: ", args[0])
	pv = []
	port = []
	axis = []
	reader = csv.reader(open(args[0], "rb"))

	hostname = reader.next()

	#read following rows and build up index of allowed PVs
	for row in reader:
		pv.append(row[0])
		port.append(row[1])
		axis.append(row[2])
		msg = row[0] + "  " + row[1] + "  " + row[2]
		logger.debug(msg)

	lstRegExps = []

	# 0: Error message
	regexp = re.compile( r'\aERR\d{3}\r' )
	lstRegExps.append(regexp)
		
	# 1: One hex number with leading $
	regexp = re.compile( r'^\$[A-Z0-9]+\r\x06' )
	lstRegExps.append(regexp)
		
	# 2: one decimal number possible sign and possible dot
	regexp = re.compile( r'^-?(\d*\.)?\d+\r\x06' )
	lstRegExps.append(regexp)
		
	# 3: return value of the status, position, velocity, fol. err command #x?PVF
	regexp = re.compile( r'^[A-Z0-9]+\r-?(\d*\.)?\d+\r-?(\d*\.)?\d+\r-?(\d*\.)?\d+\r\x06' )
	lstRegExps.append(regexp)
		
	# 4: everything else... (things not covered above plus commands with no return value)
	regexp = re.compile( r'\x06' )
	lstRegExps.append(regexp)

	#print "options.all",  options.all
	#print "options.verbose",options.verbose
	#print "options.on",options.on
	#print "options.off",options.off

	returnMatchNo = 0
	returnMatch = ''
	returnStr = ''

	cmd = ''
	index = 0

	#if option 'on' and 'all' are set, then energise all motors.
	if (options.on & options.all):
		axes1 = 0xFFFF
		axes2 = 0xFFFF
		#loop over all port numbers in file
		previousPort = 0
		for p in port:
			if not(previousPort == p):
				msg = "Opening telnet connection to " + hostname[0] +  "  port:" + port[index-1]
				print msg
				logger.debug(msg)
				tn = telnetlib.Telnet(hostname[0], port[index-1])
				cmd = "m" + mPMAC1 + "=" + str(axes1) + " m" + mPMAC2 + "=" + str(axes2)
				logger.debug("sending telnet command:")
				logger.debug(cmd)
				tn.write(cmd + '\r\n')
				(returnMatchNo, returnMatch, returnStr) = tn.expect(lstRegExps, 3)
				if returnMatchNo == -1:
					print "Timed out, waiting for expected response. Got only: " + str(returnStr)
				#check values were written correctly
				#Read 1st 16 bits (1st 16 axes)
				newaxes1 = readAxesValues(tn, 'm7501', lstRegExps)
				msg = "read back axes1: " + newaxes1
				logger.debug(msg)
				#Read 2nd 16 bits (2st 16 axes)
				newaxes2 = readAxesValues(tn, 'm7503', lstRegExps)
				msg = "read back axes2: " + newaxes2
				logger.debug(msg)
				if (int(newaxes1) != int(axes1)) or (int(newaxes2) != int(axes2)):
					print "ERROR: Values were not written correctly. Readback does not match."
					logger.error("ERROR: Values were not written correctly. Readback does not match.")

				#Close telnet connection
				msg = "Disconnecting."
				print msg
				logger.debug(msg)
				tn.close()
				previousPort = p

	#if option 'off' and 'all' are set, then de-energise all motors.
	if (options.off & options.all):
		axes1 = 0x0000
		axes2 = 0x0000
		#loop over all port numbers
		previousPort = 0
		for p in port:
			if not(previousPort == p):
				msg = "Opening telnet connection to " + hostname[0] +  "  port:" + port[index-1]
				print msg
				logger.debug(msg)
				tn = telnetlib.Telnet(hostname[0], port[index-1])
				cmd = "m" + mPMAC1 + "=" + str(axes1) + " m" + mPMAC2 + "=" + str(axes2)
				logger.debug("sending telnet command... ")
				logger.debug(cmd)
				tn.write(cmd + '\r\n')
				(returnMatchNo, returnMatch, returnStr) = tn.expect(lstRegExps, 3)
				if returnMatchNo == -1:
					print "Timed out, waiting for expected response. Got only: " + str(returnStr)
				#check values were written correctly
				#Read 1st 16 bits (1st 16 axes)
				newaxes1 = readAxesValues(tn, 'm7501', lstRegExps)
				msg = "read back axes1: " + newaxes1
				logger.debug(msg)
				#Read 2nd 16 bits (2st 16 axes)
				newaxes2 = readAxesValues(tn, 'm7503', lstRegExps)
				msg = "read back axes2: ", newaxes2
				logger.debug(msg)
				if (int(newaxes1) != int(axes1)) or (int(newaxes2) != int(axes2)):
					print "ERROR: Values were not written correctly. Readback does not match."
					logger.error("ERROR: Values were not written correctly. Readback does not match.")

				#Close telnet connection
				msg = "Disconnecting."
				print msg
				logger.debug(msg)
				tn.close()
				previousPort = p

	#If the 'all' option is not set, the loop over all the PVs in the input file,
	#and check against PVs specified on the command line.
	#Build up a list of pvs, port numbers and axes to set.
	pv2 = []
	port2 = []
	axis2 = []
	uniquePort = []
	if (not options.all):
		index = 0
		#Loop over all PVs specified in file
		for pvInFileName in pv:
			index = index + 1
			if (pvInFileName in args):
				pv2.append(pvInFileName)
				port2.append(port[index-1])
				axis2.append(axis[index-1])
				if (port[index-1] not in uniquePort):
					uniquePort.append(port[index-1])

		#print "pv2: ", pv2
		#print "port2: ", port2
		#print "axis2: ", axis2

		index = 0
		previousPort = 0
		#Now loop over each unique port number
		for p in uniquePort:
			#Open a telnet connection
			msg = "Opening telnet connection to " + hostname[0] +  "  port:" + port[index-1]
			print msg
			logger.debug(msg)
			tn = telnetlib.Telnet()
			tn.open(hostname[0], p)

			index = 0
			#Now loop over the PVs in the sublist and only use the ones which have this port number
			for pvSub in pv2:
				index = index + 1
				if (p == port2[index-1]):
					#Don't overwrite already set values, so we need to read back existing values.
					axes1 = readAxesValues(tn, 'm7501', lstRegExps) #Read 1st 16 bits (1st 16 axes)
					axes2 = readAxesValues(tn, 'm7503', lstRegExps) #Read 2nd 16 bits (2st 16 axes)
					msg = "initial readback value: " + str(hex(axes1))
					logger.debug(msg)
					msg = "initial readback value: " + str(hex(axes2))
					logger.debug(msg)
					a = int(axis2[index-1])
					if a < 17:
						if options.on:
							axes1 = axes1 | (1 << a-1)
						elif options.off:
							axes1 = axes1 & ~(1 << a-1)
					if a > 16:
						if options.on:
							axes2 = axes2 | (1 << a-17)
						elif options.off:
							axes2 = axes2 & ~(1 << a-17)
					msg = "value to send: " + str(hex(axes1))
					logger.debug(msg)
					msg = "value to send: " + str(hex(axes2))
					logger.debug(msg)
							
					cmd = "m" + mPMAC1 + "=" + str(axes1) + " m" + mPMAC2 + "=" + str(axes2)
					logger.debug("sending telnet command... ")
					logger.debug(cmd)
					tn.write(cmd + '\r\n')
					(returnMatchNo, returnMatch, returnStr) = tn.expect(lstRegExps, 3)
					if returnMatchNo == -1:
						print "Timed out, waiting for expected response. Got only: " + str(returnStr)

					#check values were written correctly
					#Read 1st 16 bits (1st 16 axes)
					newaxes1 = readAxesValues(tn, 'm7501', lstRegExps)
					msg = "next readback value: " + str(hex(newaxes1))
					logger.debug(msg)
					#Read 2nd 16 bits (2st 16 axes)
					newaxes2 = readAxesValues(tn, 'm7503', lstRegExps)
					msg = "next returned value" + str(hex(newaxes2))
					logger.debug(msg)
					if (int(newaxes1) != int(axes1)) or (int(newaxes2) != int(axes2)):
						print "ERROR: Values were not written correctly. Readback does not match."
						logger.error("ERROR: Values were not written correctly. Readback does not match.")
			
			#Close connection
			msg = "Disconnecting."
			print msg
			logger.debug(msg)
			tn.close()
			

def readAxesValues(tn, cmd, lstRegExps):
	tn.write(cmd + '\r\n')
	(returnMatchNo, returnMatch, returnStr) = tn.expect( lstRegExps, 5 )
	valueList = returnStr.split('\r')
	valueList.remove('\x06')
	axes = valueList[0]
	return int(axes)

if __name__ == "__main__":
	main()
	
