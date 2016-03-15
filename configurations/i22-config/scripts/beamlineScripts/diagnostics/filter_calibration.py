import gda.device.scannable.ScannableBase
from gda.data import PathConstructor

def flux(filename, numberOfCount):
	file=PathConstructor.createFromProperty("gda.data.scan.datawriter.datadir")+"/"+filename
	fid=open(file,'w')

	processD1(fid, numberOfCount , bsdiode)
	processD2(fid, numberOfCount , bsdiode)
	processD3(fid, numberOfCount , bsdiode)
		
	fid.close()
	print "All diagnostic done"	
	
	pos shutter 'Close'

def processD1( fid, numberOfCount , detector):

	d1Positions = d1filter.getPositions()

	nPositions = len(d1Positions)
	for i in range (nPositions):
	
		feedback.off()
		pos d1filter d1Positions[i]
		feedback.on()

		sum = 0.0
		iosum = 0.0
		fid.write( "D1 "+d1filter.getPosition()+"   ")
		for j in range (numberOfCount):
			diode = detector.getPosition()
			ioValue = iO.getPosition()
			sum = sum + diode
			iosum = iosum + ioValue 
			fid.write(" %5.5f %5.5f " % (diode , ioValue) )
			sleep(1)
		sum = sum/numberOfCount	
		iosum = iosum/numberOfCount
		fid.write(" %5.5f %5.5f \n" % (sum , iosum) )
		print "D1 "+d1filter.getPosition()+"   sum="+str(sum)+"   io=  "+str(iosum)
	
	feedback.off()		
	print "moving D1 to EMPTY position"
	pos d1filter 'Empty'		
	print "D1 at EMPTY position"
	feedback.on()		
	print "D1 done"

def processD2( fid, numberOfCount, detector):

	d2Positions = getD2Positions()
	d2Filters = getD2Filters()

	nPositions = len(d2Positions)
	for i in range (nPositions):
	
		feedback.off()
		pos d2motor d2Positions[i]
		feedback.on()

		sum = 0.0
		iosum = 0.0
		fid.write( "D2 "+d2Filters[i]+"   ")
		for j in range (numberOfCount):
			diode = detector.getPosition()
			ioValue = iO.getPosition()
			sum = sum + diode
			iosum = iosum + ioValue 
			fid.write("%5.5f %5.5f " % (diode , ioValue) )
			sleep(1)
		sum = sum/numberOfCount	
		iosum = iosum/numberOfCount
		fid.write("%5.5f %5.5f \n" % (sum , iosum) )
		print "D2 "+d2Filters[i]+"   sum="+str(sum)+"   io=  "+str(iosum)

	feedback.off()		
	print "moving D2 to 0.2mm Pyrocarbon position"
	pos d2motor 9.0625		
	print "D2 at 0.2mm Pyrocarbon position"
	feedback.on()		
	print "D2 done"

def processD3( fid, numberOfCount, detector):

	d3Positions = d3filter.getPositions()

	nPositions = len(d3Positions)-2
	for i in range (nPositions):
			
		pos d3filter d3Positions[i]	

		sum = 0.0
		iosum = 0.0
		fid.write( "D3 "+d3filter.getPosition()+"   ")
		for j in range (numberOfCount):
			diode = detector.getPosition()
			ioValue = iO.getPosition()
			sum = sum + diode
			iosum = iosum + ioValue 
			fid.write("%5.5f %5.5f " % (diode , ioValue) )
			sleep(1)
		sum = sum/numberOfCount	
		iosum = iosum/numberOfCount
		fid.write("%5.5f %5.5f \n" % (sum , iosum) )
		print "D3 "+d3filter.getPosition()+"   sum="+str(sum)+"   io=  "+str(iosum)
			
	print "moving D3 to CLEAR position"
	pos d3filter 'Clear'		
	print "D3 at Clear position"	
	print "D3 done"

def getD2Positions():
	d2Positions=[]
	d2Positions.append(9.0625)
	d2Positions.append(25.925)
	d2Positions.append(42.9)
	d2Positions.append(59.9)
	d2Positions.append(76.8)
	d2Positions.append(94.175)
	return d2Positions

def getD2Filters():
	d2Filters=[]
	d2Filters.append('Pyrocarbon 0.2mm')
	d2Filters.append('CVD 0.2mm')
	d2Filters.append('Empty')
	d2Filters.append('CVD 2.0mm')
	d2Filters.append('Pyrocarbon 0.6mm')
	d2Filters.append('Pyrocarbon 2.0mm')
	return d2Filters

