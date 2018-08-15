from gda.data import PathConstructor
from gda.data import NumTracker

print "Script started"

diode = d10d2

lensStartPos = 905
lensEndPos = 925
lensStep = .2
lensPoints = ( (lensEndPos - lensStartPos) / lensStep ) + 1 

scanStart = 1.82
scanEnd = 1.92
scanStep = 0.001 

results = []

for i in range(lensPoints) :
	position = lensStartPos + i*(lensStep)
	pos mflensz position
	print "Moved lens to new position " + str(position)
	sleep(2)
	pos mfstage_y scanStart
	print "Moved wire to start position"
	sleep(2)
	scan mfstage_y scanStart scanEnd scanStep diode
	print "Finished scan, waiting to move lens" 
	results += [(position, edge.result.fwhm, edge.result.slope, edge.result.pos)]
	filename = NumTracker("i22")
	fileNumber = filename.getCurrentFileNumber() 
	print str(position)+" , "+str(edge.result.fwhm)+" , "+str(edge.result.slope)+" , "+str(edge.result.pos)+" , "+str(fileNumber)
	
		# save the data back out
	file = open(PathConstructor.createFromDefaultProperty()+"lens_scan_prep.csv","a")
	file.write("%f , %f , %f , %f , %d\n" % (position, edge.result.fwhm, edge.result.slope, edge.result.pos , fileNumber) )
	file.close()

print "Number of results " + str(len(results))
print "pos, fwhm, slope, peak position"
numberOfResults = len(results)
for i in range(numberOfResults) :
	print str(results[i][0])+" , "+str(results[i][1])+" , "+str(results[i][2])+" , "+str(results[i][3])

print results
print "All done"


