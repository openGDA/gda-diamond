class DiffractionAppenderManager:
    """
    This class can be used to set calibration and mask files
    used by the appenders configured against a diffraction device.
    """
    def __init__(self, calibration_appender_name, mask_appender_name):
        from gda.data import ServiceHolder # @UnresolvedImport
        nds = ServiceHolder.getNexusDeviceService()
        
        self.calib_appender = nds.getDecorator(calibration_appender_name)
        self.mask_appender = nds.getDecorator(mask_appender_name)

    def set_calibration_file(self, filepath):
        self.calib_appender.setExternalFilePath(filepath)

    def set_mask_file(self, filepath):
        self.mask_appender.setExternalFilePath(filepath)
