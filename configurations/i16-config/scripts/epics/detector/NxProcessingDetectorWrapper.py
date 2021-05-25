import gda.device.detector.addetector.filewriter.MultipleImagesPerHDF5FileWriter
from gdascripts.scannable.detector.ProcessingDetectorWrapper import ProcessingDetectorWrapper, SwitchableHardwareTriggerableProcessingDetectorWrapper
from scisoftpy.external import create_function
from gda.configuration.properties import LocalProperties
from gda.device import DeviceException

class NxProcessingDetectorWrapper(SwitchableHardwareTriggerableProcessingDetectorWrapper):

    def __init__( self,
                name,
                detector,
                hardware_triggered_detector,
                detector_for_snaps,
                processors = [],
                panel_name = None,
                toreplace = None,
                replacement = None,
                iFileLoader = None,
                root_datadir = None,
                fileLoadTimout = None,
                printNfsTimes = False,
                returnPathAsImageNumberOnly = False,
                panel_name_rcp = None,
                return_performance_metrics = False,
                array_monitor_for_hardware_triggering = None):

        SwitchableHardwareTriggerableProcessingDetectorWrapper.__init__( self,
                name,
                detector,
                hardware_triggered_detector,
                detector_for_snaps,
                processors,
                panel_name,
                toreplace,
                replacement,
                iFileLoader,
                root_datadir,
                fileLoadTimout,
                printNfsTimes,
                returnPathAsImageNumberOnly,
                panel_name_rcp,
                return_performance_metrics,
                array_monitor_for_hardware_triggering )

        self.linkFunction = create_function("detectorLinkInserter", "nexusHDFLink", dls_module='python/ana')
        self.lastReadout = None


    def atScanEnd(self):
        SwitchableHardwareTriggerableProcessingDetectorWrapper.atScanEnd(self)
        plugins = self.det.getAdditionalPluginList()
        writers = [ wr for wr in plugins if isinstance(wr, gda.device.detector.addetector.filewriter.MultipleImagesPerHDF5FileWriter) ]
        if len(writers) == 0:
            print "Warning: No HDF file writers present"
            return
        if not LocalProperties.get("gda.scan.endscan.neworder", "True").lower() == "true":
            print "Warning: gda.scan.endscan.neworder must be True to create hdf links"
            return
        writer = writers[0]
        ndfile = writer.getNdFile()
        detectorFileName = ndfile.getFileTemplate_RBV() % (ndfile.getFilePath_RBV(), ndfile.getFileName_RBV(), ndfile.getFileNumber_RBV())
        nexusPaths = ["/entry1/instrument/%s" % self.name, "/entry1/%s" % self.name]
        datadirectory = LocalProperties.get("gda.data.scan.datawriter.datadir")
        nexusFileName = "%s/%d.nxs" % (datadirectory, ndfile.getFileNumber_RBV())
        detectorPath = "/entry/instrument/detector/data"
        detectorFileName = detectorFileName.replace(datadirectory, "")
        if detectorFileName[0] == '/':
            detectorFileName = detectorFileName.split('/', 1)[1]
        print "Creating HDF Links"
        # Comment this out with gda.data.scan.datawriter.dataFormat = NexusScanDataWriter 
        self.linkFunction(nexusFileName, detectorFileName, nexusPaths, detectorPath)

    def getExtraNames(self):
        return ['count_time'] + SwitchableHardwareTriggerableProcessingDetectorWrapper.getExtraNames(self)[1:]

    def _readout(self):
        #we need "something" from _readout even if a scan is canceled (used to get the filepath)
        #this is perhaps really terrible and could hide problems
        try:
            out = SwitchableHardwareTriggerableProcessingDetectorWrapper._readout(self)
            # MBB Should ^^^ be vvv ?
            #out = SwitchableHardwareTriggerableProcessingDetectorWrapper.getPositionCallable(self).call()
            self.lastReadout = out
            return out
        except DeviceException:
            if self.lastReadout == None:
                raise #this is getting silly
            return self.lastReadout

