from gda.device.detector.nexusprocessor.roistats import RoiStatsProcessor
from org.eclipse.dawnsci.analysis.dataset.roi import RectangularROI

class RequiredRoiManager:
	""" Class for managing rois in RoiStatsProcessor beans
	"""
	def __init__(self, detector):
		""" Create a RequiredRoiManager for a given detector.

		The detector must be a NexusDetectorProcessor with a processor of type
		SwmrHdfDatasetProviderProcessor, containing a RoiStatsProcessor.
		"""
		self.detector = detector
		self.roistats = self._processors()[0]

	def _processors(self):
		return [x for x in self.detector.getProcessor().getProcessors() if isinstance(x, RoiStatsProcessor)]

	def _roi_list(self):
		return self.roistats.getRequiredRectangularRoiList()  # Returns List<RectangularROI>
		# name, plot, fixed, X Start, Y Start, Width, Height, Angle

	def _roi_dict(self):
		return {roi.name: roi for roi in self._roi_list()}

	def active(self, name=None, active=None):
		""" Get or, optionally set, whether a roi is active (processed in scans).
		"""
		rois = self._roi_dict()
		if name == None or not name in rois:
			if name == None:
				print "To activate or deactivate a roi, a name is required:"
			else:
				print "'%s' not found in the list of required rois:" % name
			self.rois()
			return
		if active == None:
			return rois[name].plot
		if isinstance(active, bool):
			rois[name].plot = active
		else:
			print "Cannot activate or deactivate '%s' as '%r' is neither True nor False" % (name, active)

	def remove(self, name):
		""" Remove a roi by name
		"""
		rois = self._roi_list()
		matching_indices = [index for index, roi in enumerate(rois) if roi.name == name]
		if len(matching_indices) == 0:
			print "'%s' not found in the list of required rois:" % name
			self.rois()
			return
		# Since ROIBase.hashCode() ignores name, we can't do
		#self._roi_list().remove(rois[name])
		# as we may end up with first_roi in list being removed rather than last_roi
		# if we try to remove last_roi but first_roi is identical other than the name
		rois.remove(matching_indices[0])

	def rois(self, name_contains=""):
		""" List all rois, or optionally a subset of rois.
		
		For each roi, show the name, whether it is active (will be processed in
		scans) and start/end/length values.
		"""
		lines = [("Roi name", "Active", "x", "y", "x1", "y1", "width", "length")]
		for roi in self._roi_list():
			if name_contains in roi.name:
				lines.append((roi.name, "True" if roi.plot else "False",
					roi.getPoint()[0], roi.getPoint()[1],
					roi.getEndPoint()[0], roi.getEndPoint()[1],
					roi.getLengths()[0], roi.getLengths()[1]))
		if len(lines) > 1:
			for line in lines:
				print('{:>20}  {:^6}  {:6}  {:6}  {:6}  {:6}  {:6}  {:6}'.format(*line))
		elif name_contains == "":
			print("No required ROIs")
		else:
			print("No required ROIs with names containing '%s'" % name_contains)

	def roi(self, name=None, x=None,  y=None, x1=None, y1=None, width=None, length=None):
		""" Show, update or create a single roi

		Examples:

		roi('roi1', width=45)           would set the width of roi1, while
		                                leaving all other values the same
		roi('roi2', 233)                would set just x

		Assuming roi3 and roi4 did not already exist

		roi('roi3', 232, 98, 245, 113)  would create 'roi3' with x, y, x1 & y1
		roi('roi3', 232, 98, width=13, length=15)
		                                would create the same using width/
		                                length instead of x1 & y1
		roi('roi4', 234, 55)            would refuse to create an incomplete roi
		"""
		if name == None:
			print "To update or create a roi, a name is required:"
			self.rois()
			return
		errors = []
		rois = self._roi_dict()
		if name in rois:
			if (x == None and y == None and x1 == None and y1 == None and
					width == None and length == None):
				self.rois(name)
				return
			roi = rois[name]
		else:
			roi = RectangularROI()
			roi.name = name
			roi.plot = True
			roi.fixed = True
			if x == None or y == None:
				errors.append("To create '%s' please specify both 'x' and 'y'" % name)
			if x1 == None and width == None:
				errors.append("To create '%s' please specify only one of 'x1' or 'width'" % name)
			if y1 == None and length == None:
				errors.append("To create '%s' please specify only one of 'y1' or 'length'" % name)

		if x1 != None and width != None:
			errors.append("Ambiguous width, please specify either 'x1' or 'width', not both")
		if y1 != None and length != None:
			errors.append("Ambiguous length, please specify either 'y1' or 'length', not both")

		if len(errors) == 0:
			if (x != None or y != None):
				spt = roi.getPoint()
				spt[0] = x if x != None else spt[0]
				spt[1] = y if y != None else spt[1]
				roi.setPoint(spt)
			if (x1 != None or y1 != None):
				ept = roi.getEndPoint()
				ept[0] = x1 if x1 != None else ept[0]
				ept[1] = y1 if y1 != None else ept[1]
				roi.setEndPoint(ept)
			if (width != None or length != None):
				lengths = roi.getLengths()
				lengths[0] = width if width != None else lengths[0]
				lengths[1] = length if length != None else lengths[1]
				roi.setLengths(lengths)
			if not name in rois:
				self._roi_list().add(roi)

		if len(errors) > 0:
			print("Errors setting roi '%s':\n  %s" % (name, "\n  ".join(errors)))

"""
pil3_required.rois()
pil3_required.rois('roi')
pil3_required.rois('roi1')
pil3_required.roi()
pil3_required.roi('roi')
pil3_required.roi('roi1')
pil3_required.roi('roi3', *roi2params)
pil3_required.roi('roi3', x=214.1)
pil3_required.roi('roi3', y=81.2)
pil3_required.roi('roi3', x1=264.3)
pil3_required.roi('roi3', y1=131.4)
pil3_required.roi('roi3', width=50.5)
pil3_required.roi('roi3', length=50.6)
pil3_required.active()
pil3_required.active('roi')
pil3_required.active('roi1')
pil3_required.active('roi1', False)
pil3_required.active('roi1', True)
pil3_required.remove('roi')
pil3_required.remove('roi3')
"""
