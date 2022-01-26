# Use scanID as path if it is a string
def createSrsPath(scanID):
	if type(scanID) == str:
		return scanID
	# Assemble a path from the scan number, using current scan if not given
	# If no scanID given, use current scan number
	if scanID <= 0:
		import gda.data.NumTracker
		numtracker = gda.data.NumTracker('tmp')
		scanID = numtracker.getCurrentFileNumber() + scanID

	# scanID now contains the number of a scan
	import gda.configuration.properties
	filepath = gda.configuration.properties.LocalProperties.get("gda.data.scan.datawriter.datadir")
	filepath = filepath + '/' + str(scanID) + '.dat'  
	return filepath




def readSrsDataFile(filepath):
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
		raise IOError, 'Failed to read SRS data file: Could not open file'
	
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
			try:
				data[i].append(float(rowData[i]))
			except ValueError:
				data[i].append(str(rowData[i]).strip())
		lineIndex = lineIndex + 1

	# Return the header list, and the array of column lists
	

	return (headerList, data)