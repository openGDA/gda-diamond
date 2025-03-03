from gdascripts.scan.scanListener import ScanListener
from gdascripts.metadata.nexus_metadata_class import meta
from gda.device import Scannable #@UnresolvedImport
from gda.device.scannable.scannablegroup import ScannableGroup #@UnresolvedImport
from org.eclipse.scanning.device import CommonBeamlineDevicesConfiguration #@UnresolvedImport
import logging

log = logging.getLogger(__name__)

class DynamicScanMetadata(ScanListener):
    """
    A scan listener which will dynamically alter the metadata collected per scan. Provide a metadata_dict with the keys being the name of
    the metadata group and the values being a 2 element list. The first element is a list of scannables to look for within a scan.
    The second element is the list of device names to enable if any of the first element scannables are found to be taking part in the scan command.

    Only compatible with NexusScanDataWriter.
    """

    logger = log.getChild("DynamicScanMetadata")

    SCANNABLE_KEY = 0
    DEVICE_NAMES_KEY = 1

    def __init__(self, metadata_dict, sequence_detector = None):
        #Unique detector which be can use I-branch, J-branch or both.
        self.sequence_detector = sequence_detector
        self.METADATA_DICT = metadata_dict

        config =  CommonBeamlineDevicesConfiguration.getInstance()
        for key in self.METADATA_DICT:
            value = self.METADATA_DICT[key]
            device_names = value[DynamicScanMetadata.DEVICE_NAMES_KEY]
            scannables = value[DynamicScanMetadata.SCANNABLE_KEY]

            #Sync up with config and add our devices to monitor
            config.addAdditionalDeviceNames(device_names)
            #Add all scannable group members to metadata. Reduces setup required as only need to give group rather than each group member + group
            value[DynamicScanMetadata.SCANNABLE_KEY] = self.flatten_scannable_group_members(scannables)
            #Disable both branch metadata initially. Also checks to see if the device names exist.
            self.update_meta_devices(device_names, False)

    def flatten_scannable_group_members(self, metadata):
        new_metadata = []
        for m in metadata:
            new_metadata.append(m)
            if isinstance(m, ScannableGroup):
                for scannable_member in m.getGroupMembers():
                    new_metadata.append(scannable_member)
        return new_metadata

    def update_meta_devices(self, device_names, enable):
        done_work = False
        for name in device_names:
            if meta.isEnabled(name) is not enable:
                done_work = True
                meta.enable(name) if enable else meta.disable(name)

        #Only log once if any devices needed to be updated
        if done_work:
            DynamicScanMetadata.logger.info(("Enabled" if enable else "Disabled") + " the following metadata devices: " + str(device_names))

    #Called at start of the scan
    def prepareForScan(self):
        #Disable metadata initially in case any weren't correctly set
        for key in self.METADATA_DICT:
            value = self.METADATA_DICT[key]
            meta_device_names = value[DynamicScanMetadata.DEVICE_NAMES_KEY]
            self.update_meta_devices(meta_device_names, False)

        scan_command = self.getContext()
        for arg in scan_command:
            if isinstance(arg, Scannable):
                self.check_scannable(arg)

    #Called at the end of a scan (not if aborted though)
    def update(self, scan_object):
        for key in self.METADATA_DICT:
            value = self.METADATA_DICT[key]
            meta_device_names = value[DynamicScanMetadata.DEVICE_NAMES_KEY]
            self.update_meta_devices(meta_device_names, False)

    def check_scannable(self, scannable):
        for key, value in self.METADATA_DICT.iteritems():
            meta_device_names = value[DynamicScanMetadata.DEVICE_NAMES_KEY]
            meta_scannables = value[DynamicScanMetadata.SCANNABLE_KEY]

            if scannable in meta_scannables:
                DynamicScanMetadata.logger.debug("Enabling " + key + " metadata due to scan arg: " + scannable.toString())
                self.update_meta_devices(meta_device_names, True)

            #Check detector by getting region data and checking which excitation energy source scannable they are using to determine which metadata to use
            if self.sequence_detector is not None and scannable is self.sequence_detector:
                sequence = self.sequence_detector.getSequence()
                regions = sequence.getEnabledRegions()

                for region in regions:
                    excitation_energy_source = sequence.getExcitationEnergySourceByRegion(region)
                    excitation_energy_source_scannable = excitation_energy_source.getScannable()

                    if excitation_energy_source_scannable in meta_scannables:
                        DynamicScanMetadata.logger.debug("Enabling " + key + " metadata due to region: " + region.getName())
                        self.update_meta_devices(meta_device_names, True)
