# To use this code type:
#
# from relscan import relscan
# As a hack to force changes if you've made them to this code type "run relscan"

import gda.jython.scannable.DOFAdapter
import gda.scan.ConcurrentScan

def relscan(*args):
		
	# visit each arg
	# if a scannable name on the list is found
	# a) add it to a list of things that will be moved relatively,
	#    along with its current position
	#  b)  i) if there are no args then move on    
	# b)  ii) if there is one value add the current position to it.
	#    iii) if there are two values andd the current position to the first
	#   iiii) if there are three position add the current position to first two
	# Create and run the scan
	# wait a second for luck, and then move the motors on the list back to their old position
	numArgs = len(args)
	
	
	modifiedArgs = []
	PDsToMoveRelatively =[]
	initialPositions = []
	i = 0
	while (i < (numArgs-1)):
		# This arg should be a scannable. check if it is a DOF adapter too
		if isinstance(args[i], gda.jython.scannable.DOFAdapter):
			PDsToMoveRelatively += [ args[i] ]
			thisPDsPosition = args[i].getPosition()
			initialPositions += [ thisPDsPosition ]
			modifyFollowingNumbers = 1
		else:
			modifyFollowingNumbers = 0
		
		#Add it to the list
		modifiedArgs.append(args[i])
		#print i, " ", args[i].getName(), "mod:", modifyFollowingNumbers
		
		# Get the numbers following it if any	
		followingNumbers=[]
		i += 1
		while (i<numArgs) and (isinstance(args[i],int ) or isinstance(args[i],float )):
			followingNumbers.append(args[i])
			i += 1
		
		if modifyFollowingNumbers==1:
			
			# 0 following numbers (this PD is to be read)
			if len(followingNumbers) == 0:
				pass
			# 1 following numbers (this PD is to be moved and held), Make relative
			elif len(followingNumbers) == 1:
				followingNumbers[0] = followingNumbers[0] + thisPDsPosition
			# 2 following numbers, Make first relative
			elif len(followingNumbers) == 2:
				followingNumbers[0] = followingNumbers[0] + thisPDsPosition
			# 3 following numbers, Make first and second relative
			elif len(followingNumbers) == 3:
				followingNumbers[0] = followingNumbers[0] + thisPDsPosition
				followingNumbers[1] = followingNumbers[1] + thisPDsPosition
				
		for aNumber in followingNumbers:
			modifiedArgs.append(aNumber)
							
	# Display the new scan command for ease of mind
	argsToPrint = ''
	for arg in modifiedArgs:
		if (isinstance(arg, gda.jython.scannable.DOFAdapter)):
			argsToPrint += (arg.getName().split('.')[1] + ' ')
		else:
			argsToPrint += (str(arg) + ' ')
	print "Running:  scan", argsToPrint.rstrip(',') , "..."

	# Perform the scan
	
	theScan = gda.scan.ConcurrentScan(modifiedArgs)
	#theScan = gda.scan.ConcurrentScan(args))
	theScan.doCollection()
	
	# Return the other motors back to their old positions
	print "Returning motors to original positions... "
	
	
	for i in range(len(PDsToMoveRelatively)):
		PDsToMoveRelatively[i].asynchronousMoveTo(initialPositions[i])

	# Wait for motors to finish
	for i in range(len(PDsToMoveRelatively)):
		PDsToMoveRelatively[i].waitReady()
		
	# Display positions
	for i in range(len(PDsToMoveRelatively)):
		print "%s at %.4f" % (PDsToMoveRelatively[i].getName().split('.')[1],\
							 PDsToMoveRelatively[i].getPosition() )
		