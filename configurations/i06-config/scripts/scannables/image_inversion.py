'''
Created on 12 Feb 2026

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from i06shared import installation

class ImageInversion(ScannableMotionBase):
    '''
    classdocs
    '''


    def __init__(self, name, roi_pv, hdf_port_pv):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([])
        self.setExtraNames([name])
        self.roi_pv_ch = CAClient(roi_pv)
        self.port_pv_ch = CAClient(hdf_port_pv)
        self.roi_pv_ch.configure()
        self.port_pv_ch.configure()

    def getPosition(self):
        roi_pv_value = self.roi_pv_ch.caget()
        port_pv_value = self.port_pv_ch.caget()
        if roi_pv_value == "Yes" and port_pv_value == "mpx.roi":
            return "Yes"
        else:
            return "No"

    def asynchronousMoveTo(self, val):
        raise ValueError("%s is a Read-Only scannable object!" % self.getName())

    def isBusy(self):
        return False

if installation.isLive():
    x_inversion = ImageInversion("x_inversion", "BL06I-EA-DET-02:ROI:ReverseX", "BL06I-EA-DET-02:HDF5:NDArrayPort_RBV")
else:
    from java.net import InetAddress  # @UnresolvedImport
    host_name = InetAddress.getLocalHost().hostName.split('.')[0]
    roi_pv = host_name + "-AD-SIM-01:ROI:ReverseX"
    port_pv = host_name + "-AD-SIM-01:HDF5:NDArrayPort_RBV"
    print(str(roi_pv), str(port_pv))
    x_inversion = ImageInversion("x_inversion", str(roi_pv), str(port_pv))
