

"""CameraExposureChanger.py: Contains a class that allows changing/reading of camera exposure through
obtaining the adBase of the camera."""

__author__ = "Olly King"


class CameraExposureChanger ():
    """ Class to facilitate changing beamline camera exposure from a GDA client
    """

    def __init__(self, cam_object):
        try:
            self.ad_base = (cam_object
                            .getCollectionStrategy()
                            .getDecoratee()
                            .getDecoratee()
                            .getDecoratee()
                            .getAdBase())
        except:
            print ("Could not get Area detector base for {}, changing exposure time will be unavailable."
                   .format(cam_object.getName()))

    def get_exposure_time(self):
        """ Returns the exposure time (seconds) for the camera object associated with the class.
        On error returns -1
        """
        if (self.ad_base):
            try:
                time = self.ad_base.getAcquireTime()
            except:
                print "Problem getting exposure time from EPICS for camera."
                time = -1
            return time

    def set_exposure_time(self, time):
        """ Set an exposure time (seconds) for the camera object associated with the class"""
        if (self.ad_base):
            try:
                self.ad_base.setAcquireTime(time)
                if (self.get_exposure_time() == time):
                    print "Exposure time changed to {} seconds".format(time)
                else:
                    print "Problem setting exposure time, please try again."
            except:
                print "Problem setting exposure time over EPICS for camera."
