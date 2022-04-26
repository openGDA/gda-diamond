from time import sleep
import math
from gdascripts.utils import caget
from gda.device.detector.nxdetector.roi import ImutableRectangularIntegerROI
from gda.device.detector import NXDetector
from gda.device.detector.nxdetector.plugin.areadetector import ADRoiStatsPair
from gda.scan import ScanInformation
from gda.factory import Finder
from beam.AreaDetectorROIs import RoiStatPairClass
from gda.device.controlpoint import EpicsControlPoint

exec("[m4fpitch, m5fpitch]=[None, None]")

m4fpitch = EpicsControlPoint()
m4fpitch.setName('m4fpitch')
m4fpitch.setPvName('BL06I-EA-SGEN-01:CH1:OFF')
m4fpitch.setOutputFormat(['%f'])
m4fpitch.configure()
m5fpitch = EpicsControlPoint()
m5fpitch.setName('m5fpitch')
m5fpitch.setPvName('BL06I-EA-SGEN-01:CH2:OFF')
m5fpitch.setOutputFormat(['%f'])
m5fpitch.configure()

Derived_class_must_override_this_method = "Derived class must override this method."
Input_must_be_a_list_of_ROIs = "Input must be a list of ROIs, each provides a list specifies [x_start,y_start,x_size,y_size]"

class BeamStabilisation(object):

    def __init__(self, rois, leem_fov, leem_rot, m4fpitch, m5fpitch, psphi, roistat_index=None, pv_root_name="BL06I-EA-DET-01"):
        self.rois = rois
        self.leem_fov = leem_fov
        self.leem_rot = leem_rot
        self.m4fpitch = m4fpitch
        self.m5fpitch = m5fpitch
        self.psphi = psphi
        self.pv_root_name = pv_root_name
        self.roistat_index = roistat_index
        self.m4_mum_to_volt = 50
        self.m5_mum_to_volt = 150
        self.max_iterations = 20
        self.max_error = 0.0035
        self.stotred_beam_positions = None
        
    def get_vertical_asymmetry(self):
        top_roi = self.get_roi_average(self.roistat_index[0]) - 99
        bottom_roi = self.get_roi_average(self.roistat_index[2]) - 99
        return -(top_roi - bottom_roi) / (top_roi + bottom_roi)
    
    def get_horizontal_asymmetry(self):
        left_roi = self.get_roi_average(self.roistat_index[3]) - 99
        right_roi = self.get_roi_average(self.roistat_index[1]) - 99
        return -(right_roi - left_roi) / (right_roi + left_roi)
    
    def store_beam_positions(self):
        self.stotred_beam_positions = self.get_current_beam_positions() 
        return self.stotred_beam_positions
    
    def get_current_beam_positions(self):
        return [self.get_horizontal_asymmetry(), self.get_vertical_asymmetry()]
    
    def get_stored_beam_positions(self):
        return self.stotred_beam_positions
    
    def get_displacement_from_stored_positions(self):
        '''return the beam displacement relative to the stored position in pixel units
        '''
        new_pos = self.get_current_beam_positions()
        return [new_pos[0] - self.storedPos[0], new_pos[1] - self.storedPos[1] ]
    
    def pixel_to_volts(self, ds_rotated):
        '''convert the rotated displacement vector in pixel into mirror fine pitch units (Volts)
        '''
        self.fov = float(self.leem_fov.getPosition())
        self.fov_rot = self.leem_rot.getPosition()
        conv_factors = [self.m4_mum_to_volt * 1 / self.fov, self.m5_mum_to_volt * 1 / self.fov]
        ds_rot_volt = [-ds_rotated[0] / conv_factors[0], ds_rotated[1] / conv_factors[1]]
        return ds_rot_volt
    
    def move_beam(self, ds_rot_volt):
        current_m4 = float(self.m4fpitch.getPosition())
        current_m5 = float(self.m5fpitch.getPosition())
        self.m4fpitch.asynchronousMoveTo(current_m4 + ds_rot_volt[0])
        self.m5fpitch.asynchronousMoveTo(current_m5 + ds_rot_volt[1])
        sleep(0.5)

    def get_beam_shift(self):
        displacement = self.get_displacement_from_stored_positions()
        displacement_rotated = self.rot_displacement(displacement)
        fov = float(self.leem_fov())
        return [displacement_rotated[0] / 1000.0 * fov, displacement_rotated[1] / 1000.0 * fov]
                
    def center_beam_single(self, dummy_move_flag):
        displacement = self.get_displacement_from_stored_positions()
        displacement_rotated = self.rot_displacement(displacement)
        displacement_rot_volt = self.pixel_to_volts(displacement_rotated)
        # this is just to reduce the motion as a test
        displacement_rot_volt[0] *= 0.5
        displacement_rot_volt[1] *= 0.5
        ####
        if not(dummy_move_flag):
            print("moving %f" % displacement_rot_volt)
            self.move_beam(displacement_rot_volt)
            sleep(3)
        return displacement_rot_volt
    
    def center_beam_auto(self, dummy_move_flag):
        print("KB fine pitch start positions: m4fpitch = %f,   m5fpitch  = %f " % (m4fpitch.getPosition(), m5fpitch.getPosition()))
        self.setup_rois()
        i = 0
        last_ds_rot = [1.0, 1.0]
        sum_rot = 1
        print("iteration = %d, error = %f" % (i, sum_rot))
        try:
            self.prepare_rois_for_collection()
            while ((i < self.max_iterations)and(sum_rot > self.max_error)):
                i += 1
                last_ds_rot = self.center_beam_single(dummy_move_flag)
                sum_rot = abs(last_ds_rot[0]) + abs(last_ds_rot[1])
                print("iteration = %d, error = %f" % (i, sum_rot))
        except Exception, e:
            print(e)
            self.stop_roistats_pair()
        finally:
            self.complete_collection_from_roistats_pair()
            
        if i >= self.max_iterations:
            print("maximum iteration reached!.")
            
        return i < self.max_iterations
    
    def get_roi_average(self, roi_num):
        roi_avg_pv = self.pv_root_name + ":STAT" + str(roi_num) + ":MeanValue_RBV"
        return float(caget(roi_avg_pv))

    def calculate_rotated_displacement(self, displacement, rot_ang_rad):
        displacement_rotated = [0.0, 0.0]
        displacement_rotated[0] = displacement[0] * math.cos(rot_ang_rad) + displacement[1] * math.sin(rot_ang_rad)
        displacement_rotated[1] = -displacement[0] * math.sin(rot_ang_rad) + displacement[1] * math.cos(rot_ang_rad)
        return displacement_rotated

    def rot_displacement(self, displacement):
        # rotate the beam displacement vector
        raise NotImplementedError(Derived_class_must_override_this_method)
    
    def setup_rois(self):
        raise NotImplementedError(Derived_class_must_override_this_method)
        
    def clear_rois(self):
        raise NotImplementedError(Derived_class_must_override_this_method)
    
    def get_roistats_pair_4_detector_from_gda(self):
        raise NotImplementedError(Derived_class_must_override_this_method)
    
    def prepare_rois_for_collection(self):
        raise NotImplementedError(Derived_class_must_override_this_method)
    
    def stop_roistats_pair(self):
        raise NotImplementedError(Derived_class_must_override_this_method)
    
    def complete_collection_from_roistats_pair(self):
        raise NotImplementedError(Derived_class_must_override_this_method)


class BeamStablisationUsingAreaDetectorRoiStatPair(BeamStabilisation):
    
    def __init__(self, rois, leem_fov, leem_rot, m4fpitch, m5fpitch, psphi, roistat_index=[1, 2, 3, 4], pv_root_name="BL06I-EA-DET-01", detector=None, roi_provider_name=None):
        '''use the 1st 4 area detector's ROI-STAT pairs
        '''
        BeamStabilisation.__init__(self, rois, leem_fov, leem_rot, m4fpitch, m5fpitch, psphi, roistat_index, pv_root_name)
        self.detector = detector
        self.roi_provide_name = roi_provider_name
        self.roiProvider = Finder.find(roi_provider_name)
        
    def rot_displacement(self, ds):
        # rotate the beam displacement vector
        rot_ang_rad = -float(self.leem_rot.getPosition()) / 180.0 * math.pi
        rot_ang_rad += float(self.psphi.getPosition()) / 180.0 * math.pi
        ds_rotated = self.calculate_rotated_displacement(ds, rot_ang_rad)  
        return ds_rotated

    def setup_rois(self):
        '''update ROIs list in GDA ROI provider object but not yet send to EPICS
        This must be called when ROI is changed, and before self.prepare_rois_for_collection()
        @param rois: list of rois i.e. [[x_start,y_start,x_size,y_size],[x_start,y_start,x_size,y_size],[x_start,y_start,x_size,y_size],[x_start,y_start,x_size,y_size]]
        '''
        if isinstance(self.rois, list):
            raise TypeError(Input_must_be_a_list_of_ROIs)
        i = 1
        new_rois = []
        for roi in self.rois:
            new_roi = ImutableRectangularIntegerROI(roi[0], roi[1], roi[2], roi[3], 'Region' + str(i))
            i += 1
            new_rois.append(new_roi)
        if self.roiProvider is not None:
            self.roiProvider.updateRois(new_rois)
        else:
            raise RuntimeError("ROI provider %s is not found" % self.roi_provide_name)
        
    def clear_rois(self):
        '''remove all ROIs from the ROI provider
        '''
        if self.roiProvider is not None:
            self.roiProvider.updateRois([])
        else:
            raise RuntimeError("ROI provider %s is not found" % self.roi_provide_name)
    
    def get_roistats_pair_4_detector_from_gda(self):
        ''' retrieve GDA ROI and STAT pairs for a given detector
        '''
        if not isinstance(self.detector, NXDetector):
            raise TypeError("'%s' detector is not a NXDetector! " % (self.detector.getName()))
        additional_plugin_list = self.detector.getAdditionalPluginList()
        roi_stat_pairs = []
        for each in additional_plugin_list:
            if isinstance(each, ADRoiStatsPair):
                roi_stat_pairs.append(each)
        return roi_stat_pairs
    
    def prepare_rois_for_collection(self):
        '''configure ROIs and STATs plugins in EPICS for data collection with regions of interests
        '''
        for each in self.get_roistats_pair_4_detector_from_gda():
            # update ROIs and enable and configure EPICS rois and stats plugins
            try:
                each.prepareForCollection(1, ScanInformation.EMPTY)
            except Exception, e:
                print(e)
                each.atCommandFailure()
    
    def stop_roistats_pair(self):
        '''stop or abort ROI and STAT plug-in processes. 
        This must be called when users interrupt or abort beam stabilisation process!
        '''
        for each in self.get_roistats_pair_4_detector_from_gda():
            each.stop()
    
    def complete_collection_from_roistats_pair(self):
        '''must be called when beam stabilisation process completed!
        '''
        for each in self.get_roistats_pair_4_detector_from_gda():
            each.completeCollection()
            

class BeamStablisationUsingExtraRoiStatPair(BeamStabilisation):
    
    def __init__(self, rois, leem_fov, leem_rot, m4fpitch, m5fpitch, psphi, roistat_index=[7, 8, 9, 10], pv_root_name="BL06I-EA-DET-01"):
        '''use the 1st 4 area detector's ROI-STAT pairs
        '''
        BeamStabilisation.__init__(self, rois, leem_fov, leem_rot, m4fpitch, m5fpitch, psphi, roistat_index, pv_root_name)
        self.roistatpair = RoiStatPairClass(pv_root_name)
        
    def rot_displacement(self, ds):
        # rotate the beam displacement vector
        rot_ang_rad = -float(self.leem_rot.getPosition()) / 180.0 * math.pi
        rot_ang_rad += float(self.psphi.getPosition()) / 180.0 * math.pi
        ds_rotated = self.calculate_rotated_displacement(ds, rot_ang_rad)    
        return ds_rotated

    def setup_rois(self):
        '''configure ROIs and STATs plug-ins in EPICS with regions of interests and its index
        '''
        if isinstance(self.rois, list):
            raise TypeError(Input_must_be_a_list_of_ROIs)

        for index, roi in zip(self.roistat_index, self.rois):
            self.roistatpair.set_roi(index, roi[0], roi[1], roi[2], roi[3])
        
    def prepare_rois_for_collection(self):
        if isinstance(self.rois, list):
            raise TypeError(Input_must_be_a_list_of_ROIs)
        
        for index in self.roistat_index:
            self.roistatpair.activate_roi(index)
            self.roistatpair.activate_stat(index)        
    
    def stop_roistats_pair(self):
        '''stop or abort ROI and STAT plug-in processes. 
        This must be called when users interrupt or abort beam stabilisation process!
        '''
        if isinstance(self.rois, list):
            raise TypeError(Input_must_be_a_list_of_ROIs)
        for index in self.roistat_index:
            self.roistatpair.deactivate_roi(index)
            self.roistatpair.deactivate_stat(index)
    
    def complete_collection_from_roistats_pair(self):
        '''must be called when beam stabilisation process completed!
        '''
        self.stop_roistats_pair()
