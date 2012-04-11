import scisoftpy.plot as pl
def show_detector_view_roi():
	bean=pl.getbean("Detector Image")
	rois=pl.getrects(bean)
	if len(rois) > 0:
		roi  = rois[0]
		start=roi.getPoint()
		lengths = roi.getLengths()
		start1=start[0]
		start2 = start[1]
		end1=start1+lengths[0]
		end2=start2+lengths[1]
		print "ROI startX:%d endX:%d startY:%d endY:%d" %(start1, end1, start2, end2)
	else:
		print "No ROI selected"
		
		
	
	
