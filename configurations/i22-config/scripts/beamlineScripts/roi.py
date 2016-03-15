"""
To create single roi scannable

run this script
r1 = RoiWithStats('r1', 'BL22I-EA-PILAT-01', 1)
	where 'r1' is the name (can be anything - usually matches the variable name)
	'BL22I-...' is the base pv of the detector (up to first colon)
	1 is the roi to use (from areadetector 1-6)
		if creating multiple roi scannables, this must be changed or 
		they will report the same values

r1 can be used as a scannable as normal eg 
	scan showtime 0 10 1 r1

To use ROIs from a plot create a RoiPlotter object
from Jython run 
	rp = RoiPlotter('BL22I-EA-PILAT-01', 'Saxs Plot')
	BL22I-... is as above
	'Saxs Plot' is name of plot to create regions on

On plot view named above open region editor
create regions and resize/rename/move as required
to use in a scan add *rp.getRois() to the end of the scan command instead of r1 etc
eg 
	scan showtime 0 10 1 *rp.getRois()


NB. - if *rp.getRois() is used, values set in r1 (and others) will be overwritten by the drawn regions
	- stat values will only be updated when an image is taken. Multiple frames count as a single image
"""

from gda.device.scannable import ScannableBase
from gda.epics import CAClient
import scisoftpy as dnp

def stringToInt(s):
    return int(float(s))

def sort(a, b):
    if a < b:
        return a, b
    else:
        return b, a


class RoiWithStats(ScannableBase, object):
    '''Position roi, readback stats'''
    def __init__(self, name, basePV, roi, singleUse=False):
        self.singleUse = singleUse
        self.used = False
        self.name = name
        self.roiExts = {'min_x': 'MinX', 'size_x': 'SizeX', 'min_y': 'MinY', 'size_y': 'SizeY'}
        self.statExts = {'min_value': 'MinValue_RBV', 'max_value': 'MaxValue_RBV',\
                     'x_min': 'MinX_RBV', 'x_max': 'MaxX_RBV', 'y_min': 'MinY_RBV', 'y_max': 'MaxY_RBV', }

        self.inputs = ['min_x', 'min_y', 'size_x', 'size_y']
        self.outputs = ['min_value', 'max_value', 'x_min', 'x_max', 'y_min', 'y_max']
        self.inputNames = ["%s_%s" %(name,input) for input in self.inputs]
        self.extraNames = ["%s_%s" %(name,output) for output in self.outputs]
        self.outputFormat = ['%d']*10
        
        
        roiBasePV = "%s:ROI%d:" %(basePV, roi)
        statBasePV = "%s:STAT%d:" %(basePV, roi)

        def roiPV(ext):
            cac = CAClient(roiBasePV + ext)
            cac.configure()
            return cac
        def statPV(ext):
            cac = CAClient(statBasePV + ext)
            cac.configure()
            return cac

        self.roiPvs = dict([(k, roiPV(v)) for k, v in self.roiExts.items()])
        self.statPvs = dict([(k, statPV(v)) for k, v in self.statExts.items()])

        self.roiPvs['enable'] = roiPV('EnableCallbacks')
        self.roiPvs['enableX'] = roiPV('EnableX')
        self.roiPvs['enableY'] = roiPV('EnableY')
        self.roiPvs['port'] = roiPV('PortName_RBV')
        
        self.roiPvs['name'] = roiPV('Name')
        self.roiPvs['name'].caput(name)

        self.statPvs['enable'] = statPV('EnableCallbacks')
        self.statPvs['inputPort'] = statPV('NDArrayPort')

        self.level = 3
        
    def isBusy(self):
        return 0
    
    def atScanStart(self):
        if self.used:
            raise RoiException("ROI has been disconnected")
        self.statPvs['inputPort'].caput(self.roiPvs['port'].caget())
        self.enable(True)
        
    def atScanEnd(self):
        if self.singleUse:
            self.used = True
            for _, cac in self.roiPvs.items():
                cac.clearup()
            for _, cac in self.statPvs.items():
                cac.clearup()

    def rawAsynchronousMoveTo(self,new_position):
        """minx, miny, maxx, maxy"""
        minx, miny, maxx, maxy = new_position
#         print new_position
        minx, maxx = sort(minx, maxx)
        miny, maxy = sort(miny, maxy)
        new_position = [minx, miny, maxx-minx, maxy-miny]
#         print new_position
        for i in range(4):
            var = self.inputs[i]
#             print "moving %s to %d" %(var, new_position[i]) 
            self.roiPvs[var].caput(new_position[i])
            
    def rawGetPosition(self):
        sleep(0.5)
        return [stringToInt(self.roiPvs[i].caget()) for i in self.inputs] + [stringToInt(self.statPvs[i].caget()) for i in self.outputs]
    
    def enable(self, enable=True):
        self.roiPvs['enable'].caput(1 if enable else 0)
        self.roiPvs['enableX'].caput(1 if enable else 0)
        self.roiPvs['enableY'].caput(1 if enable else 0)
        self.statPvs['enable'].caput(1 if enable else 0)
    
    def isEnabled(self):
        return bool(stringToInt(self.roiPvs['enable'].caget())),\
            bool(stringToInt(self.statPvs['enable'].caget())),\
            bool(stringToInt(self.roiPvs['enableX'].caget())),\
            bool(stringToInt(self.roiPvs['enableY'].caget()))

    def __str__(self):
        enabled = self.isEnabled()
        warning = ""
        if not enabled[0]:
            warning += "ROI is not enabled\n"
        elif not all(enabled[2:]):
            warning += "Not all ROI dimensions are enabled\n"
        if not enabled[1]: warning += "STATS are not enabled\n"
        message = warning + ScannableBase.__str__(self)
        return message
    
    def __del__(self):
#         print "closing channels"
        for _, cac in self.roiPvs.items():
            cac.clearup()
        for _, cac in self.statPvs.items():
            cac.clearup()
    
class RoiPlotter:
    MAX_ROIS = 6
    def __init__(self, basePV, plotname="roiPlot"):
#         self.ad = addet
#         self.ad_base = addet.getAdBase()
#         self.ad_array = addet.getNdArray()
        
        self.basepv = basePV
        self.ad_rois = [RoiWithStats("roi_" + str(i+1), self.basepv, i+1) for i in range(self.MAX_ROIS)]
#         self.rois = dict([(r, "%s_roi" % r.getName()) for r in rois])
        
#         self.basepv = addet.getAdBase().getBasePVName().split(':')[0]
        self.plotname = plotname
    
#     def _getArraySize(self):
#         ad_array_plugin_base = self.ad_array.getPluginBase()
#         size_x = ad_array_plugin_base.getArraySize0_RBV()
#         size_y = ad_array_plugin_base.getArraySize1_RBV()
#         return size_x, size_y
#     
#     def _getData(self):
#         dims = self._getArraySize()
#         data = dnp.array(self.ad_array.getImageData(dims[0] * dims[1]))
#         data.shape = dims[::-1]
#         return data
#     
#     def plotImage(self):
#         data = self._getData()
#         dnp.plot.clear(name=self.plotname)
#         dnp.plot.image(data, name=self.plotname)
#         to_plot = []
#         for roi in self.ad_rois:
#             roi_pos = roi.rawGetPosition()
#             droi = dnp.roi.rectangle(point=(roi_pos[:2]), lengths=roi_pos[2:], name=roi.name)
#             to_plot.append(droi)
#         if to_plot:
#             dnp.plot.setrois(to_plot, name=self.plotname)
    
    def getRois(self):
        rois = dnp.plot.getrois(name=self.plotname)
        count = min(len(rois), self.MAX_ROIS)
        roiWithStatsList = []
        roi_count = 1
        for name, roi in rois.items():
            if roi.isPlot():
                rws = RoiWithStats(name + "_roi", self.basepv, roi_count, True)
                point = list(roi.getPoint())
#                 print point
                lengths = list(roi.getLengths())
#                 print lengths
                new_pos = point[0], point[1], lengths[0] + point[0], lengths[1] + point[1]
#                 print new_pos
                rws.rawAsynchronousMoveTo((new_pos))
                roiWithStatsList.append(rws)
            roi_count += 1
        return roiWithStatsList

class RoiException(BaseException):
    pass
#     def plotRois(self):
#         pass

# if __name__ == "__main__":
#     base = 'ws140-AD-SIM-01'
#     g = globals()
#     if "r1" in g:
#         del r1,r2,r3,r4,r5,r6
#     r1 = RoiWithStats('r1', base, 1)
#     r2 = RoiWithStats('r2', base, 2)
#     r3 = RoiWithStats('r3', base, 3)
#     r4 = RoiWithStats('r4', base, 4)
#     r5 = RoiWithStats('r5', base, 5)
#     r6 = RoiWithStats('r6', base, 6)
