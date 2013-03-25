from gda.jython.commands import Input

def diodeTime(diode):
	"""
	eg/ diodeScanTime(d3)
	
	This will set the diode time directly.
	Set diode D1 integration time to 1 seconds with:
	beamline.setValue("Top","-DI-PHDGN-01:I.SCAN","1 second")
	Diode Integration times are limited to:
		10 seconds
		5 seconds
		2 seconds
		1 second
		0.5 seconds
		0.2 seconds
		0.1 seconds
	"""
	from gdascripts.parameters import beamline_parameters
	jythonNameMap = beamline_parameters.JythonNameSpaceMapping()
	beamline = jythonNameMap.beamline
	
	print "Diode ", str(diode),", integration times available: 10,5,2,1,0.5,0.2,0.1 seconds."
	time = Input.requestInput("Please enter the number of seconds you wish to integrate for: ")
	if (time=="10"):
		tag = "3"
		print "You have entered ", str(time)," seconds, set to tag ",str(tag)
	if (time=="5"):
		tag = "4"
		print "You have entered ", str(time)," seconds, set totag ",str(tag)
	if (time=="2"):
		tag = "5"
		print "You have entered ", str(time)," seconds, set to tag ",str(tag)
	if (time=="1"):
		tag = "6"
		print "You have entered ", str(time)," seconds, set to tag ",str(tag)
	if (time=="0.5"):
		tag = "7"
		print "You have entered ", str(time)," seconds, set to tag ",str(tag)
	if (time=="0.2"):
		tag = "8"
		print "You have entered ", str(time)," seconds, set to tag ",str(tag)
	if (time=="0.1"):
		tag = "9"
		print "You have entered ", str(time)," seconds, set to tag ",str(tag)

	#Construct PV:
	PV = "-DI-PHDGN-0"+diode.name[1]+":I.SCAN"
	beamline.setValue("Top",PV,tag)
	a = beamline.getValue(None,"Top",PV)
	print "Diode "+diode.name[1]+" has been set to tag ",str(a)
