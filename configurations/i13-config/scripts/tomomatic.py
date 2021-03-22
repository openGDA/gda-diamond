from __future__ import with_statement
import csv
import os
import collections
from itertools import islice
from time import sleep, strftime
import datetime

from gdascripts.parameters import beamline_parameters
from i13i_utilities import interruptable
from tomographyScan import tomoFlyScan

import re
#from Malte.GDAscripts.PinTipCentring_I13 import autoCentrePin
# from gda.epics import CAClient
# move_rot = CAClient('BL13I-MO-HEX-01:SAMPLEROT.MOVN')
# move_hexy = CAClient('BL13I-MO-HEX-01:Y.MOVN')
# move_samx = CAClient('BL13I-MO-HEX-01:SAMPLEX.MOVN')
# move_samz = CAClient('BL13I-MO-HEX-01:SAMPLEZ.MOVN')
# for chan in [move_rot, move_hexy, move_samx, move_samz]:
#     if not chan.isConfigured():
#         chan.configure()

def natural_key(astr):
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', astr)]

#CSV_HEADERS = {
#    PUCK_ID: 'puck_id',
#    INPUCK_SLOT_ID: 'inpuck_slot_id',
#}

#prompt for user input/for confirmation
def confirm_continue():
    """
    Check if user wants to continue.
    Returns:
        True - if user wishes to continue
        False - if user wishes not to continue (wishes to abort)
    Raises:
        Exception - if user wishes to abort
    """
    answer = None
    while answer not in {'y', 'n'}:
        answer = raw_input("\n Confirm there's currently NO sample on the rotation stage!\n Type in 'Y(es)' or 'y(es)' if the rotation stage is currently EMPTY and you wish to continue: Y(es)/y(es)/N(o)/n(o)?")
        try:
            answer = answer.lower()[0]
        except:
            print(' Type in either Y(es)/y(es) or N(o)/n(o)!')
            answer = None
    if answer.startswith('n'):
        raise Exception('Sample on the rotation stage - aborting!')
    else:
        return answer.startswith('y')

def _confirm_continue(msg, ex_msg):
    """
    Check if user wants to continue.
    Returns:
        True - if user wishes to continue
        False - if user wishes not to continue (wishes to abort)
    Raises:
        Exception - if user wishes to abort
    """
    answer = None
    while answer not in {'y', 'n'}:
        answer = raw_input(msg)
        try:
            answer = answer.lower()[0]
        except:
            print(' Type in either Y(es)/y(es) or N(o)/n(o)!')
            answer = None
    if answer.startswith('n'):
        raise Exception(ex_msg)
    else:
        return answer.startswith('y')
    
TOMOMATIC_SLOT_PRIORITY = {
    1:  'lowest',
    2:  'second lowest',
    3:  'low',
    4:  'low to medium',
    5:  'medium bottom',
    6:  'medium top',
    7:  'medium to high',
    8:  'high',
    9:  'second highest',
    10: 'highest'
}

TOMOMATIC_DEFAULT = {
    'slot_priority':        10,
    'auto_centring_policy': 0,
    'ang_range_deg':        180.0,
    'pin_barcode':          'unknown'
}

#OP_DURATION_SEC = {
#    'HTL_TO_SMP':	11,
#    'SMP_EXCHANGE': 	18,
#    'SMP_TO_HTL':	10
#}

#in alphabetical order
TOMOMATIC_SUPPORTED_FIELDNAMES = {
    'ang_range_deg':        'angular range in deg',
    'ang_step_deg':         'angular step in deg',
    'auto_centring_policy': 'abandon_on_fail=-1; scan_on_fail=0; re-do_on_fail=1',
    'description':          'any text deemed useful',
    'exposure_time_sec':    'exposure time in sec',
    'inpuck_slot_id':       'position number of the slot in the puck: 1-16',
    'nflats':               'number of flats',
    'ndarks':               'number of darks',
    'pin_barcode':          'barcode on the base of the pin holder',
    'puck_id':              'position number of the puck on the hotel plate: 1-7',
    'slot_priority':        'the smaller the number, the higher the priority: 1-10'
}

MASKS = {}
# STA1
MASKS['playMode'] = 1<<6
MASKS['teachMode'] = 1<<5
MASKS['safetySpeedOp'] = 1<<4
MASKS['running'] = 1<<3
MASKS['autoMode'] = 1<<2
MASKS['oneCycleMode'] = 1<<1
MASKS['stepMode'] = 1<<0
# STA2
MASKS['servoOn'] = 1<<7
MASKS['errorState'] = 1<<6
MASKS['alarmState'] = 1<<5
MASKS['holdCommand'] = 1<<4
MASKS['holdExternal'] = 1<<3
# 1<<2 is not used
MASKS['holdPanel'] = 1<<1


class Tomomatic:
    
    next_puck_pv ='BL13I-MO-ROBOT-01:D083'
    next_pin_pv = 'BL13I-MO-ROBOT-01:D084'
    rbt_job_pv = 'BL13I-MO-ROBOT-01:JOBTGT'
    rbt_stop_pv = 'BL13I-MO-ROBOT-01:HOLDON'
    pin_barcode_pv = 'BL13I-MO-ROBOT-01:BARCODE'
    
    op_time_intervals_sec = {
        'HTL_TO_SMP':       22, #13, #11,
        'SMP_EXCHANGE':     36, #21, #18,
        'SMP_TO_HTL':       17, #12, #10
    }
    auto_centring_policy_opt = {
        'do not scan on fail':  -1,
        'scan_on_fail':         0,
        'attempt again':        1
    }
    auto_centring_attempt_count_lt = 2
    slot_priority_opt = {
        'highest':          1,
        'higher':           2,
        'high':             3,
        'high_to_medium':   4,
        'medium_to_high':   5,
        'medium_to_low':    6,
        'low_to_medium':    7,
        'low':              8,
        'lower':            9,
        'lowest':           10
    }
    default_params = {
        'slot_priority':        slot_priority_opt['lowest'],
        'auto_centring_policy': auto_centring_policy_opt['scan_on_fail'],
        'ang_range_deg':        180.0,
        'pin_barcode':          'unknown'
    }
    raw_input_msg = {
        'is_rotation_stage_empty?': "\n Confirm there is currently NO sample on the rotation stage!\n Type in 'Y(es)' or 'y(es)' if the rotation stage is currently EMPTY and you wish to continue: Y(es)/y(es)/N(o)/n(o)?",
        'on_rotation_stage_being_empty_NOT': "Obstacle on the rotation stage - aborting!",
        'is_auto_centring_camera_acquiring?': "\n Confirm GigE camera, required by auto-centring, is currently acquiring images!\n Type in 'Y(es)' or 'y(es)' if the camera is currently ACQUIRING and you wish to continue: Y(es)/y(es)/N(o)/n(o)?",
        'on_auto_centring_camera_acquiring_NOT': "Auto-centring camera not acquiring - aborting!",
        'is_the_visit_directory_correct?': "\n Confirm the above visit directory is correct!\n Type in 'Y(es)' or 'y(es)' if the visit directory is CORRECT and you wish to continue: Y(es)/y(es)/N(o)/n(o)?",
        'on_the_visit_directory_being_correct_NOT': "The visit directory not correct - aborting!",
        'are_tomography_mappings_correct?': "\n Confirm the above tomography mappings are correct!\n Type in 'Y(es)' or 'y(es)' if the tomography mappings are CORRECT and you wish to continue: Y(es)/y(es)/N(o)/n(o)?",
        'on_tomography_mappings_being_correct_NOT': "One or more tomography mappings are not correct - aborting!"
    }
    
    class LoopStatus:
        def __init__(self, pause_msg=None, pause_poll_interval_sec=5):
            self.pause_msg = pause_msg
            self.pause_poll_interval_sec = pause_poll_interval_sec
            self._pause = 0     #False        # paused_by_user/user_pause
            self._prev_pause = 0
        
        def reset(self):
            self.pause = 0
            self._prev_pause = self.pause
            
        @property
        def pause(self):
            return self._pause
        
        @pause.setter
        def pause(self, p):
            #self._prev_pause = self.pause
            self._pause = p
            
        def _on_change(self):
            out = False
            if self.pause==0 and self._prev_pause==0:
                pass # still OK to loop
                print 'OK to loop'
            if self.pause==0 and self._prev_pause==1:
                msg = "*** Loop resumed on user request!"
                print(msg)
                self._prev_pause = 0
            if self.pause==1 and self._prev_pause==1:
                pass # still not OK to loop
                out = True
                print 'not OK to loop'
            if self.pause==1 and self._prev_pause==0:
                msg = "*** Loop paused on user request..."
                print(msg)
                self._prev_pause = 1
                out = True
            return out
            
        def _handle_change(self):
            return self._on_change()                       #status = self._getStatus() #self.handleStatusChange(status) 
            #return self.pause==0
        
        def monitor(self):                          #waitWhileBusy
            if self.pause==1 or True:
                # sleep and print msgs
                while self._handle_change():        #self._getStatusAndHandleChange()
                    # not OK
                    print "sleeping"
                    sleep(self.pause_poll_interval_sec)
            #return self.pause==0
            return True
        
            
    def __init__(self,automounter=None, autocentring_translation_dct={'x':hex_samplex,'z':hex_samplez}, npucks_per_tray_max=7, nslots_per_puck_max=16):    #tray/plate
        self.npucks_per_tray_max = npucks_per_tray_max
        self.nslots_per_puck_max = nslots_per_puck_max
        self.for_scan_ordered_dct = collections.OrderedDict()
        self.for_scan_per_puck_ordered_dct = collections.OrderedDict()
        #self.rescan_lst = []
        self.allow_duplicates = True
        self.pause_main_loop = False
        self.automounter = automounter                                      #pv_prefix='BL13I-MO-ROBOT-01:'
        self.autocentring_translation_dct = autocentring_translation_dct    #'x'= tomography_translation in jythonNamespaceMapping!  assert if not!
        self.additive_displacement_for_outOfBeamPos = 7.0                  #mm (relative to inBeamPos)
        self.main_loop_status = Tomomatic.LoopStatus()
        
        self.reset()                                                        #call at end
        self.dry_run = self.TomomaticDryRun(True)                           #don't use stages, robot, autocentring, fly scan
    
    def reset(self):        #hard reset
        self.fpath = None
        self.logdir_path = None
        self.log_fpath = None
        self.verbose = False
        self.interactive = True
        self.nscans = None                      #nrows/nlines?
        self.scan_in_progress = False
        self.clear()        #soft reset
    
    def clear(self):        #soft reset
        self.per_puck_dcmp_dct = {}
        self.per_slot_priority_dcmp_dct = {}
        self.for_scan_ordered_dct.clear()
        self.for_scan_per_puck_ordered_dct.clear()
        self.loading_error = False
        self.pause_main_loop = False
        
    def is_main_loop_paused(self):
        if self.pause_main_loop:
            print("Main loop is paused!")
        return self.pause_main_loop
    
    def user_confirm_continue(self):
        _confirm_continue(msg=self.raw_input_msg['is_auto_centring_camera_acquiring?'], ex_msg=self.raw_input_msg['on_auto_centring_camera_acquiring_NOT'])
        #confirm_continue()
        _confirm_continue(msg=self.raw_input_msg['is_rotation_stage_empty?'], ex_msg=self.raw_input_msg['on_rotation_stage_being_empty_NOT'])
        curr_data_dir = wd()
        
        print("Current visit directory in GDA: %s" %(curr_data_dir))
        _confirm_continue(msg=self.raw_input_msg['is_the_visit_directory_correct?'], ex_msg=self.raw_input_msg['on_the_visit_directory_being_correct_NOT'])
        
        jns=beamline_parameters.JythonNameSpaceMapping()
        obj_of_interest = {}
        obj_of_interest['tomography_theta'] = jns.tomography_theta
        obj_of_interest['tomography_flyscan_theta'] = jns.tomography_flyscan_theta
        obj_of_interest['tomography_shutter'] = jns.tomography_shutter
        obj_of_interest['tomography_translation'] = jns.tomography_translation
        obj_of_interest['tomography_flyscan_det'] = jns.tomography_flyscan_det
        obj_of_interest['tomography_flyscan_flat_dark_det'] = jns.tomography_flyscan_flat_dark_det
        for idx, (key, val) in enumerate(obj_of_interest.iteritems()):
            name = "object undefined!"
            if val is not None:
                name = str(val.getName())
            #print("%d. %s = %s" %(idx+1, key, name))
            #print("%d. %s = %s %s" %(idx+1, key, name, '(%s)' %(get_pv_name(val) if verbose and (not get_pv_name(val) is None) else '')))
            print("%d. %s = %s" %(idx+1, key, name))
        _confirm_continue(msg=self.raw_input_msg['are_tomography_mappings_correct?'], ex_msg=self.raw_input_msg['on_tomography_mappings_being_correct_NOT'])
    
    def move_stages_to_exchange_cfg(self, timeout=60):   #timeout=15*2)
        success = True
        hex_rot.asynchronousMoveTo(0.0)
        hex_y.asynchronousMoveTo(258.0)
        hex_samplex.asynchronousMoveTo(0.0)
        hex_samplez.asynchronousMoveTo(0.0)
        hex_rx.asynchronousMoveTo(0.146)            # added for Shashi
        hex_rz.asynchronousMoveTo(0.04)             # added for Shashi
        translate_x.asynchronousMoveTo(489.395)
        t0 = time.time()
        sleep(0.1)
        while (hex_rot.isBusy() or
               hex_y.isBusy() or
               hex_samplex.isBusy() or
               hex_samplez.isBusy() or
               hex_rx.isBusy() or
               hex_rz.isBusy() or
               translate_x.isBusy()
               ):
            sleep(0.05)
            if time.time() - t0 > timeout:
                hex_rot.stop()
                hex_y.stop()
                hex_samplex.stop()
                hex_samplez.stop()
                hex_rx.stop()
                hex_rz.stop()
                translate_x.stop()
                success = False
                break
        print("move_stages_to_exchange_cfg: %s (timeout=%.3f)" %('SUCCESS' if success else 'FAIL', timeout))
        return success
    
    def move_stages_to_auto_centring_cfg(self, timeout=15*2):       # added for Shashi
        success = True
#        hex_y_curr = hex_y.getPosition()
#        hex_y.asynchronousMoveTo(hex_y_curr - 1.5)      # compensation for one extra magnet!
#        hex_rx.asynchronousMoveTo(0.1260)               # compensation for camera tilt
#        hex_rz.asynchronousMoveTo(0.068)                # compensation for camera tilt
        hex_rx.asynchronousMoveTo(0.126)
        hex_rz.asynchronousMoveTo(0.063)

        t0 = time.time()
        sleep(0.1)
        while (hex_y.isBusy() or
               hex_rx.isBusy() or
               hex_rz.isBusy()
               ):
            sleep(0.05)
            if time.time() - t0 > timeout:
                hex_y.stop()
                hex_rx.stop()
                hex_rz.stop()
                success = False
                break
        print("move_stages_to_auto_centring_cfg: %s (timeout=%.3f)" %('SUCCESS' if success else 'FAIL', timeout))
        return success
    
    def configure(self):
        self.logdir_path = gda.util.VisitPath.getVisitPath()
        timestr_fmt = "%Y-%m-%dT%H-%M-%S"
        timestr = strftime(timestr_fmt)
        if not self.fpath is None: 
            h, t = os.path.split(self.fpath)
            fname, fext = os.path.splitext(t)
            log_fname = "%s-%s.%s" %(fname,timestr,'log')
            self.log_fpath = os.path.join(self.logdir_path,log_fname)
        else:
            print('Failed on configure: input filename is None!')
        print('@log_fpath: %s' %(self.log_fpath))
    
    def load(self, fpath):
        self.clear()
        self.fpath = fpath
        with open(fpath, mode='r') as fh:
            rder = csv.DictReader(fh)
            #print type(rder), rder.__class__
            #print rder
            nrows = 0
            for row in rder:        # these are data rows (ie not including fieldname row)
                #print type(row)
                #print nrows, row
                if nrows == 0:
                    print('Column headers (fieldnames): %s' %(", ".join(row)))
                    nrows += 1
                #print('\t{row["name"]} works in the {row["department"]} department, and was born in {row["birthday month"]}.')
                print(row)
                self.sanity_check(row, nrows)
                nrows += 1
                puck_id_curr = row['puck_id']
                inpuck_slot_id_curr = row['inpuck_slot_id']
                other_items_per_puck_curr_dct = {}
                for k, v in row.items():
                    if not k in ('puck_id','inpuck_slot_id'):
                        other_items_per_puck_curr_dct.update({k: v})
                other_items_per_puck_curr_dct.update({'row_zidx': nrows-1})
                if not puck_id_curr in self.per_puck_dcmp_dct:
                    self.per_puck_dcmp_dct.update({puck_id_curr: {}})
                if not inpuck_slot_id_curr in self.per_puck_dcmp_dct[puck_id_curr]:
                    self.per_puck_dcmp_dct[puck_id_curr].update({inpuck_slot_id_curr: other_items_per_puck_curr_dct})
                else:
                    print("ERROR @puck_id %s: duplicate inpuck_slot_id_curr = %s in row %d and %d!" %(puck_id_curr,inpuck_slot_id_curr,self.per_puck_dcmp_dct[puck_id_curr][inpuck_slot_id_curr]['row_zidx'],nrows))
                #self.per_puck_dcmp_dct.update({row['puck_id']: {row['inpuck_slot_id']: }})
                
                other_items_per_slot_priority_curr_dct = {}
                slot_priority_curr = row['slot_priority']
                for k, v in row.items():
                    if k != 'slot_priority':
                        other_items_per_slot_priority_curr_dct.update({k: v})
                    other_items_per_slot_priority_curr_dct.update({'row_zidx': nrows-1})
                if not slot_priority_curr in self.per_slot_priority_dcmp_dct:
                    self.per_slot_priority_dcmp_dct.update({slot_priority_curr: [other_items_per_slot_priority_curr_dct]})
                else:
                    self.per_slot_priority_dcmp_dct[slot_priority_curr].append(other_items_per_slot_priority_curr_dct)
            #end of for
        self.nscans = nrows - 1
        assert(self.nscans >= 0)
        print self.per_puck_dcmp_dct
        print('@fpath %s: loaded %d data rows' %(self.fpath,nrows-1))
        #self.order_for_scan()
    
    def dbg_dump(self, puck_id=None):
        if not puck_id is None:
            puck_id_str = str(puck_id)
            if puck_id_str in self.per_puck_dcmp_dct:
                print('@puck_id %s:' %(puck_id_str))
                for k1,v1 in self.per_puck_dcmp_dct[puck_id_str].items():
                    #print('\t @inpuck_slot_id %s: %s' %(k1,v1))
                    print('\t @inpuck_slot_id %s:' %(k1))
                    for k2,v2 in v1.items():
                        print('\t\t @%s: %s' %(k2,v2))
                print('Summary: ')
                print('\t @puck_id %s: nslots_per_puck_populated = %d' %(puck_id_str,len(self.per_puck_dcmp_dct[puck_id_str])))
            else:
                print('@puck_id %s:' %(puck_id_str))
                print('\t No entries or invalid input puck_id!')
        else:
            nslots_populated_tot = 0
            # order by key first?
            for k0,v0 in self.per_puck_dcmp_dct.items():
                print('@puck_id %s:' %(k0))
                nslots_populated_tot += len(v0)
                for k1,v1 in self.per_puck_dcmp_dct[k0].items():
                    #print('\t @inpuck_slot_id %s: %s' %(k1,v1))
                    print('\t @inpuck_slot_id %s:' %(k1))
                    for k2,v2 in v1.items():
                        print('\t\t @%s: %s' %(k2,v2))
            #print a summary at end: npucks, nslots_per_puck_taken/occupied/populated/used
            print('SUMMARY: npucks_tot = %d, nslots_populated_tot = %d' %(len(self.per_puck_dcmp_dct),nslots_populated_tot))
            for k0,v0 in self.per_puck_dcmp_dct.items():
                print('\t @puck_id %s: nslots_per_puck_populated = %d' %(k0,len(v0)))
                
    def order_for_scan(self):
        # clear
        print self.per_slot_priority_dcmp_dct
        for k,v in self.per_slot_priority_dcmp_dct.items():
            print k, v
        for k,v in self.per_slot_priority_dcmp_dct.items():
            print 'before: ', v
            v.sort(key = lambda x: (int(x['puck_id']), int(x['inpuck_slot_id'])))
            print 'after: ', v
        self.for_scan_ordered_dct.clear()
        for k in sorted(self.per_slot_priority_dcmp_dct.keys(), key=int):
            print k, self.per_slot_priority_dcmp_dct[k]
            self.for_scan_ordered_dct[k] = sorted(self.per_slot_priority_dcmp_dct[k], key=lambda x: (int(x['puck_id']), int(x['inpuck_slot_id'])))
        print self.for_scan_ordered_dct
        for k,v in self.for_scan_ordered_dct.items():
            print k,v
        
        # pretty print
        for k0,v0 in self.for_scan_ordered_dct.items():
            print('@slot_priority %s: nitems_tot = %d' %(k0, len(v0)))
            #iter through lst of dct's 
            for dct in self.for_scan_ordered_dct[k0]:   #v0?
                #print type(dct), dct
                print('\t @puck_id = %s' %(dct['puck_id']))
                print('\t\t @inpuck_slot_id = %s' %(dct['inpuck_slot_id']))
                for k1,v1 in dct.items():
                    if not k1 in ('puck_id','inpuck_slot_id'): 
                        print('\t\t\t @%s: %s' %(k1,v1))
        
#        self.for_scan_per_puck_ordered_dct.clear()
#        for k0,v0 in self.for_scan_ordered_dct.items():
#            print k0,v0
#            other_items_for_scan_per_puck_ordered_dct = {}
#            if not k0 in self.for_scan_per_puck_ordered_dct:
#                self.for_scan_per_puck_ordered_dct[k0] = []
#            out_dct = {}
#            other_dct = {}
#            for dct in v0:
#                puck_id_curr = dct['puck_id']
#                if not puck_id_curr in out_dct:
#                    out_dct[puck_id_curr] = []
#                for k1,v1 in dct.items():
#                    if k1 != 'puck_id':
#                        other_dct.update({k1: v1})
#                out_dct[puck_id_curr].append(other_dct)
            
#            self.for_scan_per_puck_ordered_dct[k0].append({puck_id_curr: out_dct})
        self.scan_lst = []
        for k0,v0 in self.for_scan_ordered_dct.iteritems():
            for dct in v0:
                x = dct
                x['slot_priority'] = k0
                x['ctr_attempt_count'] = 0
                self.scan_lst.append(x)
        for i, el in enumerate(self.scan_lst):
            print i, el
    
    def sanity_check(self, row_dct, row_zidx):
        # or use tuple in checking cond? [ str(i) for i in range(self.npucks_per_tray_max+1)]
        puck_id_int = int(row_dct['puck_id'])
        cond_0 = 0 < puck_id_int and puck_id_int < self.npucks_per_tray_max+1
        inpuck_slot_id_int = int(row_dct['inpuck_slot_id'])
        cond_1 = 0 < inpuck_slot_id_int and inpuck_slot_id_int < self.nslots_per_puck_max+1
        #inform of ranges and meaning if applicable
        if not cond_0:
            print('Unsupported puck_id = %d in input file %s at row_zidx = %d!' %(puck_id_int,self.fpath,row_zidx))
        if not cond_1:
            print('Unsupported inpuck_slot_id = %d in input file %s at row_zidx = %d!' %(inpuck_slot_id,self.fpath,row_zidx))
        assert(cond_0 and cond_1)
        
        step_fl = float(row_dct['ang_step_deg'])
        imagesPerFlat_int = int(row_dct['nflats'])
        imagesPerDark_int = int(row_dct['ndarks'])
        exposureTime_fl = float(row_dct['exposure_time_sec'])
        
        self.apply_default_params(row_dct, row_zidx)
        
        slot_priority_int = int(row_dct['slot_priority'])
        cond_2 = 0 < slot_priority_int and slot_priority_int < 11   # make it less hard-coded, cf 10+1
        auto_centring_policy_int = int(row_dct['auto_centring_policy'])
        cond_3 = auto_centring_policy_int in (-1,0,1)
        if not cond_2:
            print('Unsupported slot_priority = %d in input file %s at row_zidx = %d!' %(slot_priority_int,self.fpath,row_zidx))
        if not cond_3:
            print('Unsupported auto_centring_policy = %d in input file %s at row_zidx = %d!' %(auto_centring_policy_int,self.fpath,row_zidx))
        assert(cond_2 and cond_3)
        ang_range_deg_fl = float(row_dct['ang_range_deg'])
    
    def apply_default_params(self, row_dct, row_zidx):
        #per each row or on complete batch? 
        #set default slot_priority (lowest?), auto_centring_policy (0?), ang_range_deg (180.0), pin_barcode ('unknown'), if not supplied (define as external const's?)
        defaults_dct = {}
        defaults_dct['auto_centring_policy'] = self.default_params['auto_centring_policy']
        defaults_dct['ang_range_deg'] = self.default_params['ang_range_deg']
        defaults_dct['pin_barcode'] = self.default_params['pin_barcode']
        defaults_dct['slot_priority'] = self.default_params['slot_priority']
        defaults_dct['description'] = 'row_zidx_%03d_puck_%02d_pin_%02d' %(row_zidx,int(row_dct['puck_id']),int(row_dct['inpuck_slot_id']))  #? (requires 'puck_id' and 'inpuck_slot_id' to exist)
        #auto_centring_policy_default = 0
        #auto_centring_policy_str = row_dct['auto_centring_policy'].strip()
        #print auto_centring_policy_str, len(auto_centring_policy_str)
        #row_dct['auto_centring_policy'] = auto_centring_policy_str if len(auto_centring_policy_str)>0 else auto_centring_policy_default
        for k, v in defaults_dct.iteritems():   #report mods in verbose mode?
            #print k
            if (k in row_dct) and (not (row_dct[k] is None)):
                row_val_str = row_dct[k].strip()
                row_dct[k] = row_val_str if len(row_val_str)>0 else v
            else:
                row_dct[k] = v                  #adds new (k,v) if k(ey) does not already exist
    
    def OLD_scan(self, start_zidx=0, nitems=None):                                  #scan_all, scan_batch?
        self.user_confirm_continue()
        dry_run_please = self.dry_run.master is True
        preamble = 'DRY RUN:' if dry_run_please else 'REAL RUN:'
        
        if self.scan_in_progress:
            print('Scan already in progress for batch file %s!' %(self.fpath))
        else:
            #nitems = (nitems is None)? self.nscans-1: nitems
            nitems = self.nscans-1
            assert(0 <= start_zidx and start_zidx < self.nscans)
            stop_zidx = start_zidx + nitems - 1                     # inc'd
            assert(0 <= stop_zidx and stop_zidx < self.nscans)
            assert(start_zidx <= stop_zidx)
            #print("start_zidx = %d, nitems = %d" %(start_zidx,nitems))
            self.scan_in_progress = True
            self.configure()        # adds timestamp
            #for reference
#            tomoFlyScan(inBeamPosition, outOfBeamPosition, exposureTime=1, start=0., stop=180., step=0.1, darkFieldInterval=0., flatFieldInterval=0.,
#                  imagesPerDark=20, imagesPerFlat=20, min_i=-1., setupForAlignment=False, autoAnalyse=True, closeShutterAfterFlats=True, extraFlatsAtEnd=False, closeShutterAtEnd=True, **kwargs):
            self.rescan_lst = []
            #for i, scn in enumerate(self.scan_lst):
            try:
                with open(self.log_fpath, mode='w') as outfh:
                    wter = csv.DictWriter(outfh, fieldnames=None)
                    for i in range(len(self.scan_lst)):
                        try:
                            interruptable()
                            scn_athand_dct = self.scan_lst[i]   # scan_athand_dct
                            ang_range_deg_athand = float(scn_athand_dct['ang_range_deg'])
                            start_athand = 0.0
                            stop_athand = start_athand + ang_range_deg_athand 
                            step_athand = float(scn_athand_dct['ang_step_deg'])
                            imagesPerFlat_athand = int(scn_athand_dct['nflats'])
                            imagesPerDark_athand = int(scn_athand_dct['ndarks'])
                            exposureTime_athand = float(scn_athand_dct['exposure_time_sec'])
                            puck_id_athand = int(scn_athand_dct['puck_id'])
                            inpuck_slot_id_athand = int(scn_athand_dct['inpuck_slot_id'])
                            auto_centring_policy_athand = int(scn_athand_dct['auto_centring_policy'])
                            ctr_attempt_count_athand = int(scn_athand_dct['ctr_attempt_count'])
                            print('\n')
                            print('scn_athand_loop_zidx = %d' %(i))
                            print('puck_id = %d, inpuck_slot_id = %d' %(puck_id_athand,inpuck_slot_id_athand))
                            print('ang_range_deg = %.3f, ang_step_deg = %.3f' %(ang_range_deg_athand,step_athand))
                            print('start = %.3f, stop = %.3f, step = %.3f' %(start_athand,stop_athand,step_athand))
                            print('nflats = %d, ndarks = %d' %(imagesPerFlat_athand,imagesPerDark_athand))
                            print('exposure_time_sec = %.3f' %(exposureTime_athand))
                            print('auto_centring_policy = %d' %(auto_centring_policy_athand))
                            print('ctr_attempt_count = %d' %(ctr_attempt_count_athand))
                            print('\n')
                            
                            out_dct = self.scan_lst[i]
                            if i==0:
                                fieldnames = list(self.scan_lst[0].keys())
                                fieldnames.append('pin_barcode_out')
                                fieldnames.append('nexus_scan_file')
                                fieldnames.append('auto_ctr_out')
                                fieldnames.append('auto_centre_x')
                                fieldnames.append('auto_centre_z')
                                #fieldnames.append('auto_centring_attempt')        # count?
                                #fieldnames.append('scan_attempt')
                                #fieldnames.append('scan_out')
                                wter.fieldnames = fieldnames
                                wter.writeheader()
                                if not dry_run_please:
                                    self.move_stages_to_exchange_cfg()
                                    #set next puck and pin
                                    caput(self.next_puck_pv, puck_id_athand)
                                    caput(self.next_pin_pv, inpuck_slot_id_athand)
                                print('%s caput(%s, %d)' %(preamble, self.next_puck_pv, puck_id_athand))
                                print('%s caput(%s, %d)' %(preamble, self.next_pin_pv, inpuck_slot_id_athand))
                                #sleep(5)
                                if not dry_run_please:
                                    #run [ 2] HTL_TO_SMP
                                    #caput(self.rbt_job_pv, 2)
                                    caput(self.rbt_job_pv, 'HTL_TO_SMP')
                                print('%s caput(%s, %s)' %(preamble, self.rbt_job_pv, 'HTL_TO_SMP'))
                                #sleep(11)
                                print("HTL_TO_SMP: waiting for %.3f sec" %(self.op_time_intervals_sec['HTL_TO_SMP']))
                                sleep(self.op_time_intervals_sec['HTL_TO_SMP'])
                            print('%s Attempting auto-centring...' %(preamble))
                            if not dry_run_please:
                                print('%s Preparing for running auto-centring...' %(preamble))
                                #hex_y_curr = hex_y.getPosition()    # added for Shashi
                                #hex_y.moveTo(hex_y_curr - 1.5)    # compensation for one extra magnet!
                                #hex_rx.moveTo(0.1260)           # compensation for camera tilt
                                #hex_rz.moveTo(0.068)            # compensation for camera tilt
                                self.move_stages_to_auto_centring_cfg()
                                print('%s Finished preparing for running auto-centring!' %(preamble))
                                print('%s Running auto-centring...' %(preamble))
                                centreOK = autoCentrePin()                  #(maxMove=8.0, moveTol=0.15)
                            else:
                                centreOK = self.dry_run.autocentring_out 
                            print('%s centreOK = %s' %(preamble, centreOK))
                            out_dct['ctr_attempt_count'] += 1
                            ctr_attempt_count_athand = out_dct['ctr_attempt_count']
                            interruptable()
                            inBeamPosition_athand = self.autocentring_translation_dct['x'].getPosition()                           # exclude under DRY RUN?
                            outOfBeamPosition_athand = inBeamPosition_athand + self.additive_displacement_for_outOfBeamPos
                            inBeamPosition_athand = 489.395                                                                         # for Shashi (translate_x)
                            outOfBeamPosition_athand = inBeamPosition_athand-15.0 # for translate_x
                            print('inBeamPosition = %.3f, outOfBeamPosition = %.3f \n' %(inBeamPosition_athand,outOfBeamPosition_athand))
                            scan_or_not = centreOK or auto_centring_policy_athand==0 or (auto_centring_policy_athand==1 and ctr_attempt_count_athand<2)
                            if scan_or_not:
                                print('%s Running scan %d (of %d)...' %(preamble,i+1,len(self.scan_lst)))
                                interruptable()
                                if not dry_run_please:
                                    tomoFlyScan(inBeamPosition=inBeamPosition_athand, outOfBeamPosition=outOfBeamPosition_athand, exposureTime=exposureTime_athand, start=start_athand, stop=stop_athand, step=step_athand, imagesPerDark=imagesPerDark_athand, imagesPerFlat=imagesPerFlat_athand)
                                else:
                                    pass
                                    #sleep(5)
                                interruptable()
                                print('%s Finished running scan %d (of %d)!\n' %(preamble, i+1,len(self.scan_lst)))
                            else:
                                if auto_centring_policy_athand !=-1:
                                    self.rescan_lst.append(scn_athand_dct)
                                else:
                                    pass
                            jns=beamline_parameters.JythonNameSpaceMapping()
                            if not dry_run_please:
                                pin_barcode_out = caget(self.pin_barcode_pv)                             #eg u'CA00CJ6595::::'
                            else:
                                pin_barcode_out = 'DEADBEEF::::'
                            out_dct['pin_barcode_out'] = pin_barcode_out.replace(':','')
                            out_dct['auto_ctr_out'] = 'CTR_SUCCESS' if centreOK else 'CTR_FAIL'
                            out_dct['auto_centre_x'] = inBeamPosition_athand
                            out_dct['auto_centre_z'] = self.autocentring_translation_dct['z'].getPosition()
                            out_dct['nexus_scan_file'] = jns.lastScanDataPoint().currentFilename if scan_or_not else ''
                            wter.writerow(out_dct)
                            interruptable()
                            if i < len(self.scan_lst)-1:
                                scn_imminent_dct = self.scan_lst[i+1]
                                puck_id_imminent = int(scn_imminent_dct['puck_id'])
                                inpuck_slot_id_imminent = int(scn_imminent_dct['inpuck_slot_id'])
                                print('puck_id_imminent = %d, inpuck_slot_id_imminent = %d' %(puck_id_imminent, inpuck_slot_id_imminent))
                                if not dry_run_please:
                                    self.move_stages_to_exchange_cfg()
                                    #set next puck and pin
                                    caput(self.next_puck_pv, puck_id_imminent)
                                    caput(self.next_pin_pv, inpuck_slot_id_imminent)
                                print('%s caput(%s, %d)' %(preamble, self.next_puck_pv, puck_id_imminent))
                                print('%s caput(%s, %d)' %(preamble, self.next_pin_pv, inpuck_slot_id_imminent))
                                sleep(5)
                                #run [ 3] SMP_EXCHANGE
                                if not dry_run_please:
                                    #run [ 3] SMP_EXCHANGE
                                    #caput(self.rbt_job_pv, 3)
                                    caput(self.rbt_job_pv, 'SMP_EXCHANGE')
                                print('%s caput(%s, %s)' %(preamble, self.rbt_job_pv, 'SMP_EXCHANGE'))
                                #sleep(18)
                                print("SMP_EXCHANGE: waiting for %.3f sec" %(self.op_time_intervals_sec['SMP_EXCHANGE']))
                                sleep(self.op_time_intervals_sec['SMP_EXCHANGE'])
                            else:
                                if not dry_run_please:
                                    self.move_stages_to_exchange_cfg()
                                    #run [ 4] SMP_TO_HTL
                                    #caput(self.rbt_job_pv, 4)
                                    caput(self.rbt_job_pv, 'SMP_TO_HTL')
                                print('%s caput(%s, %s)' %(preamble, self.rbt_job_pv, 'SMP_TO_HTL'))
                                #sleep(10)
                                print("SMP_TO_HTL: waiting for %.3f sec" %(self.op_time_intervals_sec['SMP_TO_HTL']))
                                sleep(self.op_time_intervals_sec['SMP_TO_HTL'])
                            interruptable()
                        except Exception, e:
                            # stop robot?
                            print('Error in scan %d (of %d): %s' %(i+1,len(self.scan_lst),str(e)))
                            raise(e)
                    #end of for loop
            except Exception, e:
                # stop robot?
                print('Error: %s' %(str(e)))
            finally:
                self.scan_in_progress = False
                print('@log_fpath: %s' %(self.log_fpath))
                print("All done!")
    
    
    def scan(self, start_zidx=0, nitems=None):                                  #scan_all, scan_batch?
        self.user_confirm_continue()
        dry_run_please = self.dry_run.master is True
        preamble = 'DRY RUN:' if dry_run_please else 'REAL RUN:'
        
        if self.scan_in_progress:
            print('Scan already in progress for batch file %s!' %(self.fpath))
        else:
            #nitems = (nitems is None)? self.nscans-1: nitems
            nitems = self.nscans-1
            assert(0 <= start_zidx and start_zidx < self.nscans)
            stop_zidx = start_zidx + nitems - 1                     # inc'd
            assert(0 <= stop_zidx and stop_zidx < self.nscans)
            assert(start_zidx <= stop_zidx)
            #print("start_zidx = %d, nitems = %d" %(start_zidx,nitems))
            self.scan_in_progress = True
            self.configure()        # adds timestamp
            #for reference
#            tomoFlyScan(inBeamPosition, outOfBeamPosition, exposureTime=1, start=0., stop=180., step=0.1, darkFieldInterval=0., flatFieldInterval=0.,
#                  imagesPerDark=20, imagesPerFlat=20, min_i=-1., setupForAlignment=False, autoAnalyse=True, closeShutterAfterFlats=True, extraFlatsAtEnd=False, closeShutterAtEnd=True, **kwargs):
            startTm = datetime.datetime.now()
            self.rescan_lst = []
            #for i, scn in enumerate(self.scan_lst):
            try:
                with open(self.log_fpath, mode='w') as outfh:
                    wter = csv.DictWriter(outfh, fieldnames=None)
                    len_scan_lst = len(self.scan_lst)
                    i = 0
                    first_sample = True
                    #for i in range(len(self.scan_lst)):
                    while (i < len_scan_lst) and (self.main_loop_status.monitor()):
                        out_dct = self.scan_lst[i]
                        try:
                            interruptable()
                            scn_athand_dct = self.scan_lst[i]   # scan_athand_dct
                            ang_range_deg_athand = float(scn_athand_dct['ang_range_deg'])
                            start_athand = 0.0
                            stop_athand = start_athand + ang_range_deg_athand 
                            step_athand = float(scn_athand_dct['ang_step_deg'])
                            imagesPerFlat_athand = int(scn_athand_dct['nflats'])
                            imagesPerDark_athand = int(scn_athand_dct['ndarks'])
                            exposureTime_athand = float(scn_athand_dct['exposure_time_sec'])
                            puck_id_athand = int(scn_athand_dct['puck_id'])
                            inpuck_slot_id_athand = int(scn_athand_dct['inpuck_slot_id'])
                            auto_centring_policy_athand = int(scn_athand_dct['auto_centring_policy'])
                            ctr_attempt_count_athand = int(scn_athand_dct['ctr_attempt_count'])
                            print('\n')
                            print('scn_athand_loop_zidx = %d' %(i))
                            print('puck_id = %d, inpuck_slot_id = %d' %(puck_id_athand,inpuck_slot_id_athand))
                            print('ang_range_deg = %.3f, ang_step_deg = %.3f' %(ang_range_deg_athand,step_athand))
                            print('start = %.3f, stop = %.3f, step = %.3f' %(start_athand,stop_athand,step_athand))
                            print('nflats = %d, ndarks = %d' %(imagesPerFlat_athand,imagesPerDark_athand))
                            print('exposure_time_sec = %.3f' %(exposureTime_athand))
                            print('auto_centring_policy = %d' %(auto_centring_policy_athand))
                            print('ctr_attempt_count = %d (before)' %(ctr_attempt_count_athand))
                            print('\n')
                            
                            #out_dct = self.scan_lst[i]
                            #if i==0:
                            if first_sample:
                                first_sample = False
                                fieldnames = list(self.scan_lst[0].keys())
                                extra_fieldnames = []
                                extra_fieldnames.append('pin_barcode_out')
                                extra_fieldnames.append('nexus_scan_file')
                                extra_fieldnames.append('auto_ctr_out')
                                extra_fieldnames.append('auto_centre_x')
                                extra_fieldnames.append('auto_centre_z')
                                #extra_fieldnames.append('scan_attempt_count')
                                extra_fieldnames.append('scan_out')
                                for f in extra_fieldnames:
                                    if not (f in fieldnames):
                                         fieldnames.append(f)
                                wter.fieldnames = fieldnames
                                wter.writeheader()
                                if not dry_run_please:
                                    self.move_stages_to_exchange_cfg()
                                    #set next puck and pin
                                    caput(self.next_puck_pv, puck_id_athand)
                                    caput(self.next_pin_pv, inpuck_slot_id_athand)
                                print('%s caput(%s, %d)' %(preamble, self.next_puck_pv, puck_id_athand))
                                print('%s caput(%s, %d)' %(preamble, self.next_pin_pv, inpuck_slot_id_athand))
                                #sleep(5)
                                if not dry_run_please:
                                    #run [ 2] HTL_TO_SMP
                                    #caput(self.rbt_job_pv, 2)
                                    caput(self.rbt_job_pv, 'HTL_TO_SMP')
                                print('%s caput(%s, %s)' %(preamble, self.rbt_job_pv, 'HTL_TO_SMP'))
                                #sleep(11)
                                print("HTL_TO_SMP: waiting for %.3f sec" %(self.op_time_intervals_sec['HTL_TO_SMP']))
                                sleep(self.op_time_intervals_sec['HTL_TO_SMP'])
                            print('%s Attempting auto-centring...' %(preamble))
                            if not dry_run_please:
                                print('%s Preparing for running auto-centring...' %(preamble))
                                #hex_y_curr = hex_y.getPosition()    # added for Shashi
                                #hex_y.moveTo(hex_y_curr - 1.5)    # compensation for one extra magnet!
                                #hex_rx.moveTo(0.1260)           # compensation for camera tilt
                                #hex_rz.moveTo(0.068)            # compensation for camera tilt
                                self.move_stages_to_auto_centring_cfg()
                                print('%s Finished preparing for running auto-centring!' %(preamble))
                                print('%s Running auto-centring...' %(preamble))
                                centreOK = autoCentrePin()          #(maxMove=8.0, moveTol=0.15)
                            else:
                                centreOK = self.dry_run.autocentring_out 
                            print('%s centreOK = %s' %(preamble, centreOK))
                            out_dct['ctr_attempt_count'] += 1
                            ctr_attempt_count_athand = out_dct['ctr_attempt_count']
                            print('ctr_attempt_count = %d (after)' %(ctr_attempt_count_athand))
                            interruptable()
                            jns=beamline_parameters.JythonNameSpaceMapping()
                            tomography_translation_stage = jns.tomography_translation
                            #inBeamPosition_athand = self.autocentring_translation_dct['x'].getPosition()                           # exclude under DRY RUN?
                            #outOfBeamPosition_athand = inBeamPosition_athand + self.additive_displacement_for_outOfBeamPos
                            inBeamPosition_athand = 489.395
                            outOfBeamPosition_athand = inBeamPosition_athand-10.0       #-15.0 # for translate_x
                            print('tomography_translation_stage = %s :' %(tomography_translation_stage.getName()))
                            print('\t inBeamPosition = %.3f, outOfBeamPosition = %.3f \n' %(inBeamPosition_athand,outOfBeamPosition_athand))
                            scan_or_not = centreOK or auto_centring_policy_athand==0 or (auto_centring_policy_athand==1 and ctr_attempt_count_athand==auto_centring_attempt_count_lt)
                            
                            if not dry_run_please:
                                pin_barcode_out = caget(self.pin_barcode_pv)                             #eg u'CA00CJ6595::::'
                            else:
                                pin_barcode_out = 'DEADBEEF::::'
                            out_dct['pin_barcode_out'] = pin_barcode_out.replace(':','')
                            out_dct['auto_ctr_out'] = 'CTR_SUCCESS' if centreOK else 'CTR_FAIL'
                            out_dct['auto_centre_x'] = inBeamPosition_athand
                            out_dct['auto_centre_z'] = self.autocentring_translation_dct['z'].getPosition()
                            
                            if scan_or_not:
                                print('%s Running scan %d (of %d)...' %(preamble,i+1,len(self.scan_lst)))
                                interruptable()
                                if not dry_run_please:
                                    try:
                                        tomoFlyScan(inBeamPosition=inBeamPosition_athand, outOfBeamPosition=outOfBeamPosition_athand, exposureTime=exposureTime_athand, start=start_athand, stop=stop_athand, step=step_athand, imagesPerDark=imagesPerDark_athand, imagesPerFlat=imagesPerFlat_athand)
                                        out_dct['nexus_scan_file'] = jns.lastScanDataPoint().currentFilename
                                        out_dct['scan_out'] = 'SCN_SUCCESS'
                                    except Exception, e:
                                        out_dct['scan_out'] = 'SCN_FAIL'
                                        print('Error in tomoFlyScan: %s' %(str(e)))
                                        raise(e)
                                else:
                                    #dry run
                                    out_dct['nexus_scan_file'] = ''
                                    out_dct['scan_out'] = 'SCN_SUCCESS'
                                    #sleep(5)
                                interruptable()
                                print('%s Finished running scan %d (of %d)!\n' %(preamble, i+1,len(self.scan_lst)))
                                self.scan_lst.pop(i)
                                len_scan_lst -= 1
                            else:
                                out_dct['nexus_scan_file'] = ''
                                if (not centreOK) and auto_centring_policy_athand == -1:
                                    self.scan_lst.pop(i)                                            #abandon (skip) sample
                                    len_scan_lst -= 1
                                    out_dct['scan_out'] = 'SCN_NO_GO'
                                    print('This sample will NOT be scanned due to its auto-centring policy!\n')
                                elif (not centreOK) and (auto_centring_policy_athand == 1) and (ctr_attempt_count_athand<auto_centring_attempt_count_lt):
                                    self.scan_lst.pop(i)
                                    self.scan_lst.append(out_dct)                                   #add at end for another attempt
                                    out_dct['scan_out'] = 'SCN_NO_GO'                               #SCN_IN_FUTURE/AT_END
                                    print('This sample is re-submitted at end due to its auto-centring policy!\n')
                            
#                            jns=beamline_parameters.JythonNameSpaceMapping()
#                            if not dry_run_please:
#                                pin_barcode_out = caget(self.pin_barcode_pv)                             #eg u'CA00CJ6595::::'
#                            else:
#                                pin_barcode_out = 'DEADBEEF::::'
#                            out_dct['pin_barcode_out'] = pin_barcode_out.replace(':','')
#                            out_dct['auto_ctr_out'] = 'CTR_SUCCESS' if centreOK else 'CTR_FAIL'
#                            out_dct['auto_centre_x'] = inBeamPosition_athand
#                            out_dct['auto_centre_z'] = self.autocentring_translation_dct['z'].getPosition()
#                            out_dct['nexus_scan_file'] = jns.lastScanDataPoint().currentFilename if scan_or_not else ''
                            #wter.writerow(out_dct)
                            interruptable()
                            if len(self.scan_lst) > 0:
                                scn_imminent_dct = self.scan_lst[i]
                                puck_id_imminent = int(scn_imminent_dct['puck_id'])
                                inpuck_slot_id_imminent = int(scn_imminent_dct['inpuck_slot_id'])
                                print('puck_id_imminent = %d, inpuck_slot_id_imminent = %d' %(puck_id_imminent, inpuck_slot_id_imminent))
                                if not dry_run_please:
                                    self.move_stages_to_exchange_cfg()
                                    #set next puck and pin
                                    caput(self.next_puck_pv, puck_id_imminent)
                                    caput(self.next_pin_pv, inpuck_slot_id_imminent)
                                print('%s caput(%s, %d)' %(preamble, self.next_puck_pv, puck_id_imminent))
                                print('%s caput(%s, %d)' %(preamble, self.next_pin_pv, inpuck_slot_id_imminent))
                                sleep(5)
                                #run [ 3] SMP_EXCHANGE
                                if not dry_run_please:
                                    #run [ 3] SMP_EXCHANGE
                                    #caput(self.rbt_job_pv, 3)
                                    caput(self.rbt_job_pv, 'SMP_EXCHANGE')
                                print('%s caput(%s, %s)' %(preamble, self.rbt_job_pv, 'SMP_EXCHANGE'))
                                #sleep(18)
                                print("SMP_EXCHANGE: waiting for %.3f sec" %(self.op_time_intervals_sec['SMP_EXCHANGE']))
                                sleep(self.op_time_intervals_sec['SMP_EXCHANGE'])
                            else:
                                if not dry_run_please:
                                    self.move_stages_to_exchange_cfg()
                                    #run [ 4] SMP_TO_HTL
                                    #caput(self.rbt_job_pv, 4)
                                    caput(self.rbt_job_pv, 'SMP_TO_HTL')
                                print('%s caput(%s, %s)' %(preamble, self.rbt_job_pv, 'SMP_TO_HTL'))
                                #sleep(10)
                                print("SMP_TO_HTL: waiting for %.3f sec" %(self.op_time_intervals_sec['SMP_TO_HTL']))
                                sleep(self.op_time_intervals_sec['SMP_TO_HTL'])
                            interruptable()
                        except Exception, e:
                            #execute this code where there is an exception
                            # stop robot?
                            print('Error in scan %d (of %d): %s' %(i+1,len(self.scan_lst),str(e)))
                            raise(e)
                        else:
                            #No exceptions? Run this code
                            pass
                        finally:
                            #always run this code, exception being thrown or not
                            wter.writerow(out_dct)
                    #end of while loop
            except Exception, e:
                # stop robot?
                print('Error: %s' %(str(e)))
            finally:
                self.scan_in_progress = False
                print('@log_fpath: %s' %(self.log_fpath))
                endTm = datetime.datetime.now()
                elapsedTm = endTm - startTm
                print("Elapsed time [D day[s], ][H]H:MM:SS[.UUUUUU]: %s" %(str(elapsedTm)))
                print("All done!")
    
    def move_pin_from_hotel_to_scan_pos(self, puck_id, inpuck_slot_id):
        confirm_continue()
        dry_run_please = self.dry_run.master is True
        preamble = 'DRY RUN:' if dry_run_please else 'REAL RUN:'
        if not dry_run_please:
            self.move_stages_to_exchange_cfg()                                      #needed?
            #set next puck and pin
            caput(self.next_puck_pv, puck_id)
            caput(self.next_pin_pv, inpuck_slot_id)
        print('%s caput(%s, %d)' %(preamble, self.next_puck_pv, puck_id))
        print('%s caput(%s, %d)' %(preamble, self.next_pin_pv, inpuck_slot_id))
        #sleep(5)
        if not dry_run_please:
            #run [ 2] HTL_TO_SMP
            #caput(self.rbt_job_pv, 2)
            caput(self.rbt_job_pv, 'HTL_TO_SMP')
        print('%s caput(%s, %s)' %(preamble, self.rbt_job_pv, 'HTL_TO_SMP'))
        #sleep(11)
        sleep(self.op_time_intervals_sec['HTL_TO_SMP'])
        if not dry_run_please:
            pin_barcode_out = caget(self.pin_barcode_pv)                                 #eg u'CA00CJ6595::::'
        else:
            pin_barcode_out = 'DEADBEEF::::'
        return pin_barcode_out
    
    def exchange_pins_at_scan_pos(self, new_puck_id, new_inpuck_slot_id):           #exchange_samples?
        dry_run_please = self.dry_run.master is True
        preamble = 'DRY RUN:' if dry_run_please else 'REAL RUN:'
        if not dry_run_please:
            self.move_stages_to_exchange_cfg()                                      #needed?
            #set next puck and pin
            caput(self.next_puck_pv, new_puck_id)
            caput(self.next_pin_pv, new_inpuck_slot_id)
        print('%s caput(%s, %d)' %(preamble, self.next_puck_pv, new_puck_id))
        print('%s caput(%s, %d)' %(preamble, self.next_pin_pv, new_inpuck_slot_id))
        sleep(5)
        if not dry_run_please:
            #run [ 3] SMP_EXCHANGE
            #caput(self.rbt_job_pv, 3)
            caput(self.rbt_job_pv, 'SMP_EXCHANGE')
        print('%s caput(%s, %s)' %(preamble, self.rbt_job_pv, 'SMP_EXCHANGE'))
        #sleep(18)
        sleep(self.op_time_intervals_sec['SMP_EXCHANGE'])
        if not dry_run_please:
            pin_barcode_out = caget(self.pin_barcode_pv)                                 #eg u'CA00CJ6595::::'
        else:
            pin_barcode_out = 'DEADBEEF::::'
        return pin_barcode_out
    
    def move_pin_from_scan_pos_to_hotel(self):
        dry_run_please = self.dry_run.master is True
        preamble = 'DRY RUN:' if dry_run_please else 'REAL RUN:'
        if not dry_run_please:
            self.move_stages_to_exchange_cfg()                                      #needed?
            #run [ 4] SMP_TO_HTL
            #caput(self.rbt_job_pv, 4)
            caput(self.rbt_job_pv, 'SMP_TO_HTL')
        print('%s caput(%s, %s)' %(preamble, self.rbt_job_pv, 'SMP_TO_HTL'))
        #sleep(10)
        sleep(self.op_time_intervals_sec['SMP_TO_HTL'])
    
    #test duration
    def test_move_pin_from_hotel_to_scan_pos(self, puck_id, inpuck_slot_id):
        confirm_continue()
        dry_run_please = self.dry_run.master is True
        preamble = 'DRY RUN:' if dry_run_please else 'REAL RUN:'
        if not dry_run_please:
            self.move_stages_to_exchange_cfg()                                      #needed?
            #set next puck and pin
            caput(self.next_puck_pv, puck_id)
            caput(self.next_pin_pv, inpuck_slot_id)
        print('%s caput(%s, %d)' %(preamble, self.next_puck_pv, puck_id))
        print('%s caput(%s, %d)' %(preamble, self.next_pin_pv, inpuck_slot_id))
        #sleep(5)
        sta1_bfr = caget('BL13I-MO-ROBOT-01:STA1')
        counter_bfr = caget('BL13I-MO-ROBOT-01:COUNTER')
        if not dry_run_please:
            #run [ 2] HTL_TO_SMP
            #caput(self.rbt_job_pv, 2)
            caput(self.rbt_job_pv, 'HTL_TO_SMP')
        print('%s caput(%s, %s)' %(preamble, self.rbt_job_pv, 'HTL_TO_SMP'))
        sleep(1)
        sta1_aft = caget('BL13I-MO-ROBOT-01:STA1')
        counter_aft = caget('BL13I-MO-ROBOT-01:COUNTER')
        is_running = sta1_bfr != sta1_aft
        while is_running:
            print('running: aft=%d (bfr=%d) | aft=%d (bfr=%d) | counter_aft=%.5f (counter_bfr=%.5f)' %(sta1_aft,sta1_bfr,sta1_aft & MASKS['running'],sta1_bfr & MASKS['running'],counter_aft,counter_bfr))
            sleep(0.5)
            sta1_aft = caget('BL13I-MO-ROBOT-01:STA1')
            is_running = sta1_bfr != sta1_aft
        #sleep(11)
        if not dry_run_please:
            pin_barcode_out = caget(self.pin_barcode_pv)                                 #eg u'CA00CJ6595::::'
        else:
            pin_barcode_out = 'DEADBEEF::::'
        return pin_barcode_out
    
    def test_exchange_pins_at_scan_pos(self, new_puck_id, new_inpuck_slot_id):           #exchange_samples?
        dry_run_please = self.dry_run.master is True
        preamble = 'DRY RUN:' if dry_run_please else 'REAL RUN:'
        if not dry_run_please:
            self.move_stages_to_exchange_cfg()                                      #needed?
            #set next puck and pin
            caput(self.next_puck_pv, new_puck_id)
            caput(self.next_pin_pv, new_inpuck_slot_id)
        print('%s caput(%s, %d)' %(preamble, self.next_puck_pv, new_puck_id))
        print('%s caput(%s, %d)' %(preamble, self.next_pin_pv, new_inpuck_slot_id))
        sleep(5)
        if not dry_run_please:
            #run [ 3] SMP_EXCHANGE
            #caput(self.rbt_job_pv, 3)
            caput(self.rbt_job_pv, 'SMP_EXCHANGE')
        print('%s caput(%s, %s)' %(preamble, self.rbt_job_pv, 'SMP_EXCHANGE'))
        sleep(18)
        if not dry_run_please:
            pin_barcode_out = caget(self.pin_barcode_pv)                                 #eg u'CA00CJ6595::::'
        else:
            pin_barcode_out = 'DEADBEEF::::'
        return pin_barcode_out
    
    def test_move_pin_from_scan_pos_to_hotel(self):
        dry_run_please = self.dry_run.master is True
        preamble = 'DRY RUN:' if dry_run_please else 'REAL RUN:'
        if not dry_run_please:
            self.move_stages_to_exchange_cfg()                                      #needed?
            #run [ 4] SMP_TO_HTL
            #caput(self.rbt_job_pv, 4)
            caput(self.rbt_job_pv, 'SMP_TO_HTL')
        print('%s caput(%s, %s)' %(preamble, self.rbt_job_pv, 'SMP_TO_HTL'))
        sleep(10)



    def preview(self, start_zidx, nitems=1):
        for itm in islice(self.for_scan_ordered_dct.items(), start_zidx, start_zidx+nitems):
            print itm
    
    def to_string(self):
        print(" TOMOMATIC:")
        print("\t fpath = %s" %(self.fpath))
        print("\t logdir_path = %s" %(self.logdir_path))
        print("\t log_fpath = %s" %(self.log_fpath))
        print("\t nscans = %s" %(self.nscans))
        print("\t additive_displacement_for_outOfBeamPos = %.3f" %(self.additive_displacement_for_outOfBeamPos))
        print('\t autocentring_translation_x = %s, currently positioned at %.3f' %(self.autocentring_translation_dct['x'].getName(),self.autocentring_translation_dct['x'].getPosition()))
        self.dry_run()
    
    
#    def __str__(self):
#        pass
#    def __repr__(self):
#        pass
    def __call__(self):
        self.to_string()
    
    #inner class
    class TomomaticDryRun:
        def __init__(self,autocentring_out,master=False):
            self.master = master                        #do or don't stages, robot, autocentring, fly scan
            self.autocentring_out = autocentring_out              #constant outcome from autocentring
        
        def to_string(self):
            if self.master is True:
                print('\t DRY RUN!')
                print('\t\t DRY RUN master = %s' %(self.master))
                print('\t\t DRY RUN autocentring_out = %s' %(self.autocentring_out))
            else:
                print('\t REAL RUN!')
        
#        def __str__(self):
#            pass
#        def __repr__(self):
#            pass
        
        def __call__(self):
            self.to_string()
        
#instantiation
tomomatic = Tomomatic()
tomomatic.dry_run.master = False                 #if True, DO NOT use stages, robot, auto-centring, fly scan
tomomatic.dry_run.autocentring_out = False       #centreOK = tomomatic.dry_run.autocentring_out
print("\n Created an instance called 'tomomatic'!")
#tomomatic says hello!
tomomatic()
