from gda.configuration.properties import LocalProperties
def FindScanPeak(ordinateName, printNameList=[], abscissaNameList=[], scanID=0, ToPrint=1):
	""" Values= FindScanPeak(ordinateName, printNameList=[], scanID='null', ToPrint=1)
	Finds the peak value within a scan (currently just the maximum value). Returns all
	values from this line as dictionary. If enabled prints some values from this line.
  
	Keyword arguements:
	ordinateName -- the header name of the value whose peak is to be found
	printNameList -- a list of header names to print (if enabled),
    abscissaNameList --  NOT USED. may later be used for more advanced peak finding algorithms
	scanID -- leave empty to read most recent scan. Else a scan number or an absolute
		file path. If negative (-n), will find the peak of the scan n scans old.
	ToPrint -- Set to 0 to disable printing
  
	Returns:
	The values of all elements from the selected line in a dictionary with header
	names as keys

	Example:
	run FindScanPeak  (as import is unreliable!)
	peakValues = FindScanPeak("y", ["x","y"], scanID = 15) #loads scan number 15, finds max y,
		prints x and y, and returns all values.

	"""

	# ----- Generate path -----
	filepath=scanDataPath(scanID)

	if ToPrint == 1:    
		print "In file: %s" % filepath

	# ----- Read the file -----
	(headerList, columnList) = readSRSDataFile(filepath)

	# ----- Turn these into dictionary objects with header names as keys -----
	dataDict = {}

	for i in range(0, len(headerList)):
		dataDict[headerList[i]]=columnList[i]

	# ----- Find the index of the point -----
	iPeak = findMaxPointNonInterp(dataDict[ordinateName])

	# ----- Print some stuff unless ToPrint passed in as 0 -----
	if ToPrint == 1:   
		print "Max %s occurs at point %i (starting from 0) where:" % (ordinateName, iPeak)
		for i in range(0, len(printNameList)):
			tempList = dataDict[printNameList[i]]                    
			print "%s  =  %f" % (printNameList[i],tempList[iPeak])

	# ----- Return a dict object of values line where max occured -----
	maxPeak = {}
	for i in range(0, len(headerList)):
		tempList = dataDict[headerList[i]]
		maxPeak[headerList[i]] = tempList[iPeak]
	return maxPeak


def findMaxPointNonInterp(ordinateList):
	"""index = rindMaxPointNonInterp(ordinateList): Returns index of maximum value in list"""
	runningMaxVal = ordinateList[0]
	runningMaxI = 0
	for i in range (0, len(ordinateList)):
		if ordinateList[i] > runningMaxVal:
			runningMaxI = i
			runningMaxVal = ordinateList[i]

	return runningMaxI

def FindScanCentroid(ordinateName, abscissaName, printNameList=[], scanID=0, ToPrint=1):
	""" Values= FindScanCentroid(ordinateName, abscissaName, printNameList=[], scanID='null', ToPrint=1)
	Finds the centroid of a scan. Returns all values from the nearest line as dictionary. 
	If enabled prints some values from this line.
	
	Keyword arguements:
	ordinateName -- the header name of the measure value
                  abscissaName --  the header name of the swept parameter
	printNameList -- a list of header names to print (if enabled),
	scanID -- leave empty to read most recent scan. Else a scan number or an absolute
		file path. If negative (-n), will find the peak of the scan n scans old.
	ToPrint -- Set to 0 to disable printing

	Returns:
	The values of all elements from the selected line in a dictionary with header
	names as keys.
	
	Example:
	run FindScanCentroid (as import is dodgy!)
	centroidValues = FindScanCentroid("y", "x", ["x","y"]) # finds the centroid of
	the data y swept over the parameter x and prints the xand y values
	
	"""

	# ----- Generate path -----
 	filepath=scanDataPath(scanID)

	if ToPrint == 1:
		print "In file: %s" % filepath


	# ----- Read the file -----
	(headerList, columnList) = readSRSDataFile(filepath)


	# ----- Turn these into dictionary objects with header names as keys -----
	dataDict = {}

	for i in range(0, len(headerList)):
		#print "headerlist[i]", headerList[i]
		#print "columnlist[i]", columnList[i]
		dataDict[headerList[i]]=columnList[i]


	# ----- Find the index of the point -----
	(iCentroid, actualCentroid) = findCentroidPoint(dataDict[abscissaName], dataDict[ordinateName])
	
	# Get the value of the peak
	#tempList = dataDict[ordinateName]
	#peakValue = tempList[iPeak] 

	
	# ----- Print some stuff unless ToPrint passed in as 0 -----
	if ToPrint == 1:   
		print "Centroid of data is %f, which is closest to point %i (starting from 0) where:" % (actualCentroid, iCentroid)
		for i in range(0, len(printNameList)):
			tempList = dataDict[printNameList[i]]                    
			print "%s  =  %f" % (printNameList[i], tempList[iCentroid])
			
			
	# ----- Return a dict object of values line where centroid occured -----
	toReturn = {}
	for i in range(0, len(headerList)):
		tempList = dataDict[headerList[i]]
		toReturn[headerList[i]] = tempList[iCentroid]
	return toReturn

def findCentroidPoint(xList, yList):
	"""(iNearestPoint, actualCentroid)  = rindMaxPointNonInterp(ordinateList): Returns index of maximum value in list"""
	# Calculate the actual centroid
	xSum = sum(xList)
	ySum = sum(yList)
	xySum = 0
	for i in range(0, len(xList)):
		xySum = xySum + xList[i]*yList[i]
	if ySum==0:
		actualCentroid = sum(xList) / len(xList)
	else:
		actualCentroid = xySum / ySum	
	
	# Find the nearest point
	ddelta= range(0, len(xList))		#centroid will occur where ddelta is minimum
	for i in range(0, len(xList)):
		ddelta[i] = abs( xList[i] - actualCentroid )
	iCentroid = 0 # Assume first point has minimum ddelta (is centroid)	
	for i in range(0, len(xList)):
		if ddelta[i] < ddelta[iCentroid]:
			iCentroid = i
			
	return (iCentroid, actualCentroid)

def scanDataPath(scanID):
	# Use scanID as path if it is a string
	if type(scanID) == type('gda rocks'):
		filepath = scanID 
	else:  # Assemble a path from the scan number, using current scan if not given
		# If no scanID given, use current scan number
		if scanID <= 0:
			import gda.data.NumTracker
			numtracker = gda.data.NumTracker(LocalProperties.GDA_BEAMLINE_NAME)
			scanID = numtracker.getCurrentFileNumber() + scanID
		
		# Implicit else: scanID must be a positive number

		# scanID now contains the number of a scan
		import gda.configuration.properties   
		filepath = gda.configuration.properties.LocalProperties.get("gda.data.scan.datawriter.datadir")
		filepath = filepath + '/' + str(scanID) + '.dat'  
	return filepath

def readSRSDataFile(filepath):
	"""(headerList, data) = readSRSDataFile(filepath): Reads an SRS data file.

	Keyword arguments:
	filepath -- the absolute path of file to open.
    
	Returns:
	headerList -- Column headers as an array of strings
	data -- An list of columns data. Each column a list of doubles.

	"""

	# Read the entire file into an array of strings called lines
	try:
		f = open(filepath, "r")
		lines = f.readlines()
		f.close()
	except Exception, e:
		raise IOError, 'Failed to read SRS data file: Could not open file' + `filepath` + " : " +str(e)
	
	fileLength = len(lines)

	# Move lineIndex to first line after the line with END (The header line)
	lineIndex = 0;
	while lineIndex < fileLength:
		if lines[lineIndex].find('END')!=-1:
			break      
		if (lineIndex == (fileLength - 1)):
			raise IOError, 'Failed to read SRS data file: No END found'
		lineIndex = lineIndex + 1
	lineIndex = lineIndex + 1    

	# Read headers and leave lineIndex on first line of data
	lines[lineIndex] = lines[lineIndex].strip("\n")
	headerList = lines[lineIndex].split("\t")
	lineIndex = lineIndex + 1
	noColumns = len(headerList)

	# Make an array to hold data for each column
	data=[]
	for i in range(0, noColumns):
		data.append([])

	# Fill in each line of data
	while lineIndex < fileLength:
		rowData = lines[lineIndex].split("\t")
		for i in range(0, noColumns):
			data[i].append(float(rowData[i]))
		lineIndex = lineIndex + 1

	# Return the header list, and the array of column lists
	

	return (headerList, data)



