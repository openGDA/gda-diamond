def dumpOscillation(update, controller, index , osc):
	update(controller,"Dump of oscillation information:" + str(index))
	update(controller,"\tEnd = " + str(osc.getEnd()) )
	update(controller,"\tExposure_time = " + str(osc.getExposure_time()) )
	update(controller,"\tNumber_of_images = " + str(osc.getNumber_of_images()) )
	update(controller,"\tNumber_of_passes = " + str(osc.getNumber_of_passes()) )
	update(controller,"\tOverlap = " + str(osc.getOverlap()) )
	update(controller,"\tRange = " + str(osc.getRange()) )
	update(controller,"\tStart = " + str(osc.getStart()) )
	update(controller,"\tStart_image_number = " + str(osc.getStart_image_number()) )

def dumpOscillationSequence(update, controller, osc_seq):
	update(controller,"Number of elements in oscillation sequence :" + str(len(osc_seq)))
	for index in range(0, len(osc_seq)):
		dumpOscillation(update, controller, index, osc_seq[index])

def dumpBeamlineParameters(update, controller, parameters):
	dir(parameters)

def dumpFileinfo(update, controller, fileinfo):
	update(controller,"File info:" )
	update(controller,"\tTemplate = " + str(fileinfo.getTemplate()) )
	update(controller,"\tRun_number = " + str(fileinfo.getRun_number()) )
	update(controller,"\tPrefix = " + str(fileinfo.getPrefix()) )
	update(controller,"\tDirectory = " + str(fileinfo.getDirectory()) )

def dumpSampleReference(update, controller, ref):
	if (ref != None):
		update(controller,"Sample Reference:" )
		update(controller,"\tBlSampleId = " + str(ref.getBlSampleId()) )
		update(controller,"\tCode = " + str(ref.getCode()) )
		update(controller,"\tContainer_code = " + str(ref.getContainer_code()) )
		update(controller,"\tContainer_reference = " + str(ref.getContainer_reference()) )
		update(controller,"\tSample_location= " + str(ref.getSample_location()) )
	else:
		update(controller,"Sample Reference is empty" )

def dumpCollectRequest(update, controller, request):
	dumpOscillationSequence(update, controller, request.getOscillation_sequence())
	dumpBeamlineParameters(update, controller, request.getBeamline_parameters())
	update(controller,"Collection_type = " + str(request.getCollection_type()) )
	update(controller,"Comment = " + str(request.getComment()) )
	dumpFileinfo(update, controller, request.getFileinfo() )
	update(controller,"Resolution.lower = " + str(request.getResolution().getLower()) )
	update(controller,"Resolution.upper = " + str(request.getResolution().getUpper()) )
	update(controller,"Wavelength = " + str(request.getWavelength()) )
	dumpSampleReference(update, controller, request.getSample_reference() )

def dumpExtendedCollectRequest(update, controller, index, extendedRequest):
	update(controller,"Dump of request :" + str(index))
	dumpCollectRequest(update, controller, extendedRequest.request)
	update(controller,"runNumber = ", repr(extendedRequest.runNumber) );
	update(controller,"sampleDetectorDistanceInMM = ", repr(extendedRequest.sampleDetectorDistanceInMM) );
	update(controller,"totalNumberOfImages = ", repr(extendedRequest.totalNumberOfImages) );
	update(controller,"dnaFileDir = ", repr(extendedRequest.dnaFileDir) );
	update(controller,"dnaFileNameTemplate = ", repr(extendedRequest.dnaFileNameTemplate) );
	update(controller,"dnaFilePrefix = ", repr(extendedRequest.dnaFilePrefix) );
	update(controller,"fileNameTemplate = ", repr(extendedRequest.fileNameTemplate) );
	update(controller,"comment = ", repr(extendedRequest.comment) );
	
	if extendedRequest.isHasTransmission():
		update(controller,"transmissionInPerCent = ", repr(extendedRequest.transmissionInPerCent) );
	else:
		update(controller,"transmissionInPerCent is not set")
	
	if extendedRequest.hasBeamSize:
		update(controller,"beamSizeX = ", repr(extendedRequest.beamSizeX) );
		update(controller,"beamSizeY = ", repr(extendedRequest.beamSizeY) );
	else:
		update(controller,"beamSize is not set")
	
	update(controller,"BeamstopPosition = ", repr(extendedRequest.beamstopPosition) )
	update(controller,"AperturePosition = ", repr(extendedRequest.aperturePosition) )
	update(controller,"actualBarcode = ", repr(extendedRequest.actualBarcode) )

def dumpCollectRequestArray(update, controller, collect_request_object_array):
	numberOfRequests = len( collect_request_object_array.getExtendedCollectRequests() )
	update( controller,"Number of requests :" + str( numberOfRequests ) )
	for index in range(0, numberOfRequests ):
		dumpExtendedCollectRequest(update, controller, index, collect_request_object_array.getExtendedCollectRequests()[index])
