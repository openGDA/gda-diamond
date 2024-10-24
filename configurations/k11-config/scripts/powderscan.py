import time
from gdaserver import beam_selector
from java.util import Set  # @UnresolvedImport

from gda.epics import LazyPVFactory  # @UnresolvedImport

from org.eclipse.dawnsci.analysis.dataset.roi import PointROI  # @UnresolvedImport
from org.eclipse.scanning.sequencer import ScanRequestBuilder  # @UnresolvedImport
from org.eclipse.scanning.api.points.models import TwoAxisPointSingleModel  # @UnresolvedImport
from org.eclipse.scanning.api.device import IRunnableDeviceService  # @UnresolvedImport
from org.eclipse.scanning.api.scan import IFilePathService  # @UnresolvedImport

from uk.ac.diamond.osgi.services import ServiceProvider  # @UnresolvedImport
from mapping_scan_commands import submit


class PowderScan:

    def __init__(self, rot_stage, rot_zero_pv, det, x_scannable, y_scannable, fov_centre_x, fov_centre_y):

        '''
        Create object to perform a powder scan, that is, a single diffraction
        collected while the rotation stage is continually spinning.

        params:
            `rot_stage`: stage to continuously rotate during the acquisition
            `rot_zero_pv`: PV for zeroing the rotation stage when in a zeroable position after the scan
            `det`: name of acquiring detector
            `x_scannable`: name of x axis
            `y_scannable`: name of y axis
            `fov_centre_x`: X pixel coordinate for centre of the imaging field of view
            `fov_centre_y`: Y pixel coordinate for centre of the imaging field of view
        '''

        self.rot_stage = rot_stage
        self.rot_zero_pv = LazyPVFactory.newIntegerPV(rot_zero_pv)
        self.det = det
        self.x_scannable = x_scannable
        self.y_scannable = y_scannable
        self.fov_centre_x = fov_centre_x
        self.fov_centre_y = fov_centre_y


    def start(self, beam_type, exposure, rpm):
        '''
        Begin a powder scan

        params:
            `beam_type`: one of 'Diffraction' or 'Imaging'
            `exposure`: in seconds
            `rpm`: velocity of rotation stage
        '''
        
        self._verify_params(beam_type, rpm)
        self._select_beam(beam_type)
        self._start_stage_rotation(rpm)
        self._submit_powderscan(exposure)
        self._stop_and_zero_rotation_stage()


    def _verify_params(self, beam_type, rpm):

        if beam_type not in ('Diffraction', 'Imaging'):
            raise TypeError("`beam_type` must be one of ['Diffraction', 'Imaging']")

        max_rpm = self._get_max_rpm()
        if rpm <= 0 or rpm > max_rpm:
            raise ValueError("rpm must be in range (0, %d]" % max_rpm)

    def _select_beam(self, beam_type):
        beam_selector(beam_type)
        print("%s beam selected" % beam_type)
        

    def _start_stage_rotation(self, rpm):
        '''
        Spin rotation stage at given rpm, return when constant velocity reached
        '''
        self._set_rpm(rpm)
        self.rot_stage.asynchronousMoveTo(self.rot_stage.getUpperInnerLimit() - 0.5)
        time.sleep(0.5)  # (guess) wait for constant velocity
        print("Rotation stage spinning at %d rpm" % rpm)

    def _stop_and_zero_rotation_stage(self):
        '''
        Stop stage, move to nearest multiple of 360 and zero
        '''
        self.rot_stage.stop()
        p = self.rot_stage.getPosition()
        nearest_zero = round(p/360.0) * 360
        self.rot_stage.waitWhileBusy()
        self.rot_stage.moveTo(nearest_zero)
        self.rot_zero_pv.putWait(1)
        print("Rotation stage reset")

    def _submit_powderscan(self, exposure):
        scan_request = self._create_scan_request(exposure)

        print("Scanning...")
        submit(scan_request)
        print("Scan complete")

    def _create_scan_request(self, det_exposure):
        '''
        The only thing special with this scan request is the nexus template,
        which creates a 'diffraction' group similar to that produced by Malcolm.
        This allows the nexus file to be processed using the same pipeline.
        '''
        region, path = self._get_region_and_path()
        detector_map = self._get_detector_conf(det_exposure)
        template_path = ServiceProvider.getService(IFilePathService).getPersistenceDir() + "/nexus_templates/powderscan.yaml"
        
        return ScanRequestBuilder()\
            .withPathAndRegion(path, region)\
            .withDetectors(detector_map)\
            .withTemplateFilePaths(Set.of(template_path))\
            .build()

    def _get_region_and_path(self):
        '''
        A single point at the centre of the field of view
        '''

        region = PointROI([self.fov_centre_x, self.fov_centre_y])

        path = TwoAxisPointSingleModel()
        path.setxAxisName(self.x_scannable)
        path.setyAxisName(self.y_scannable)
        path.setX(self.fov_centre_x)
        path.setY(self.fov_centre_y)

        return (region, path)

    def _get_detector_conf(self, exposure):
        '''
        Creates the detector map required by ScanRequestBuilder
        '''
        
        det_model = ServiceProvider.getService(IRunnableDeviceService).getRunnableDevice(self.det).getModel()
        det_model.setExposureTime(exposure)
        detector_map = {self.det: det_model}
        return detector_map
        
    def _set_rpm(self, rpm):
        """
        rot_stage speed is in deg/s
        """
        rps = rpm / 60.0
        dps = rps * 360
        self.rot_stage.setSpeed(dps)

    def _get_max_rpm(self):
        max_speed = self.rot_stage.getMotor().getMaxSpeed()  # in deg/s
        max_rps = max_speed / 360.0
        return max_rps * 60.0