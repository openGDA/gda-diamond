from __future__ import with_statement
import csv
import os
import collections
from itertools import islice
from time import sleep, strftime

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

def check_continue():
    """
    Check if the user wants to continue.
    Returns:
        True - if user wishes to continue
        False - if user wishes not to continue (abort)
    Raises:
        Exception - if user wishes to abort
    """
    cont = None
    while cont not in {'y', 'n'}:
        cont = raw_input('Confirm there is no sample on the rotation stage - continue?: Y(es)/N(o)')
        try:
            cont = cont.lower()[0]
        except:
            print('Type in either Y(es) or N(o)!')
            cont = None
    if cont.startswith('n'):
        raise Exception('Sample on the rotation stage - aborting!')
    else:
        return cont.startswith('y')

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
    'slot_priority':        1,
    'auto_centring_policy': 0,
    'ang_range_deg':        180.0,
    'barcode':              'unknown'
}

class Tomomatic:
    def __init__(self,automounter=None, autocentring_translation_x=hex_samplex, npucks_per_tray_max=7, nslots_per_puck_max=16):    #tray/plate
        self.npucks_per_tray_max = npucks_per_tray_max
        self.nslots_per_puck_max = nslots_per_puck_max
        self.for_scan_ordered_dct = collections.OrderedDict()
        self.for_scan_per_puck_ordered_dct = collections.OrderedDict()
        self.allow_duplicates = True
        self.automounter = automounter                                      #pv_prefix='BL13I-MO-ROBOT-01:'
        self.autocentring_translation_x = autocentring_translation_x        # =tomography_translation in jythonNamespaceMapping!
        self.additive_displacement_for_outOfBeamPos = -7.0                  #mm (relative to inBeamPos)
        self.reset()                                                        # call it at end
    
    
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
    
    def move_stages_to_exchange_cfg(self, timeout=15):
        hex_rot.asynchronousMoveTo(0.0)
        hex_y.asynchronousMoveTo(260.0)
        hex_samplex.asynchronousMoveTo(0.0)
        hex_samplez.asynchronousMoveTo(0.0)
        t0 = time.time()
        sleep(0.1)
        while (hex_rot.isBusy() or
               hex_y.isBusy() or
               hex_samplex.isBusy() or
               hex_samplez.isBusy()):
            sleep(0.05)
            if time.time() - t0 > timeout:
                hex_rot.stop()
                hex_y.stop()
                hex_samplex.stop()
                hex_samplez.stop()
                break
    
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
            print('Summary: npucks_tot = %d, nslots_populated_tot = %d' %(len(self.per_puck_dcmp_dct),nslots_populated_tot))
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
                self.scan_lst.append(x)
        for i, el in enumerate(self.scan_lst):
            print i, el
    
    def sanity_check(self, row_dct, row_zidx):
        #self.apply_defaults(row_dct)
        # or use tuple in checking cond? [ str(i) for i in range(self.npucks_per_tray_max+1)]
        puck_id_int = int(row_dct['puck_id'])
        inpuck_slot_id_int = int(row_dct['inpuck_slot_id'])
        slot_priority_int = int(row_dct['slot_priority'])
        auto_centring_policy_int = int(row_dct['auto_centring_policy'])
        cond_0 = 0 < puck_id_int and puck_id_int < self.npucks_per_tray_max+1
        cond_1 = 0 < inpuck_slot_id_int and inpuck_slot_id_int < self.nslots_per_puck_max+1
        cond_2 = 0 < slot_priority_int and slot_priority_int < 11   # make it less hard-coded, cf 11
        cond_3 = auto_centring_policy_int in (-1,0,1)
        #inform of ranges and meaning if applicable
        if not cond_0:
            print('Unsupported puck_id = %d in input file %s at row_zidx = %d!' %(puck_id_int,self.fpath,row_zidx))
        if not cond_1:
            print('Unsupported inpuck_slot_id = %d in input file %s at row_zidx = %d!' %(inpuck_slot_id,self.fpath,row_zidx))
        if not cond_2:
            print('Unsupported slot_priority = %d in input file %s at row_zidx = %d!' %(slot_priority_int,self.fpath,row_zidx))
        if not cond_3:
            print('Unsupported auto_centring_policy = %d in input file %s at row_zidx = %d!' %(auto_centring_policy_int,self.fpath,row_zidx))
        assert(cond_0 and cond_1 and cond_2 and cond_3)
        
        ang_range_deg_fl = float(row_dct['ang_range_deg'])
        step_fl = float(row_dct['ang_step_deg'])
        imagesPerFlat_int = int(row_dct['nflats'])
        imagesPerDark_int = int(row_dct['ndarks'])
        exposureTime_fl = float(row_dct['exposure_time_sec'])
        
    
    def apply_defaults(self, row_dct):
        #per each row or on complete batch? 
        #set default slot_priority (lowest?), auto_centring_policy (0?), ang_range_deg (180.0), barcode ('unknown'), if not supplied (define as const's)
        pass
    
    def scan(self, start_zidx=0, nitems=None):
        next_puck_pv = 'BL13I-MO-ROBOT-01:D083'
        next_pin_pv = 'BL13I-MO-ROBOT-01:D084'
        rbt_job_pv = 'BL13I-MO-ROBOT-01:JOBTGT'
        rbt_stop_pv = 'BL13I-MO-ROBOT-01:HOLDON'
        pin_barcode_pv = 'BL13I-MO-ROBOT-01:BARCODE'
        
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
            #for i, scn in enumerate(self.scan_lst):
            try:
                with open(self.log_fpath, mode='w') as outfh:
                    wter = csv.DictWriter(outfh, fieldnames=None)
                    for i in range(len(self.scan_lst)):
                        try:
                            interruptable()
                            scn_athand = self.scan_lst[i]   # scan_athand_dct
                            ang_range_deg_athand = float(scn_athand['ang_range_deg'])
                            start_athand = 0.0
                            stop_athand = start_athand + ang_range_deg_athand 
                            step_athand = float(scn_athand['ang_step_deg'])
                            imagesPerFlat_athand = int(scn_athand['nflats'])
                            imagesPerDark_athand = int(scn_athand['ndarks'])
                            exposureTime_athand = float(scn_athand['exposure_time_sec'])
                            puck_id_athand = int(scn_athand['puck_id'])
                            inpuck_slot_id_athand = int(scn_athand['inpuck_slot_id'])
                            print("\n scn_athand = %d" %(i))
                            print('puck_id = %d, inpuck_slot_id = %d' %(puck_id_athand,inpuck_slot_id_athand))
                            print('ang_range_deg = %.3f, ang_step_deg = %.3f' %(ang_range_deg_athand,step_athand))
                            print('start = %.3f, stop = %.3f, step = %.3f' %(start_athand,stop_athand,step_athand))
                            print('nflats = %d, ndarks = %d' %(imagesPerFlat_athand,imagesPerDark_athand))
                            print('exposure_time_sec = %.3f\n' %(exposureTime_athand))
                            
                            #set next puck and pin
                            if i==0:
                                fieldnames = list(self.scan_lst[0].keys())
                                fieldnames.append('barcode_out')
                                fieldnames.append('nexus_scan_file')
                                wter.fieldnames = fieldnames
                                wter.writeheader()
                                self.move_stages_to_exchange_cfg()
                                caput(next_puck_pv, puck_id_athand)
                                caput(next_pin_pv, inpuck_slot_id_athand)
                                print('caput(%s, %d)' %(next_puck_pv, puck_id_athand))
                                print('caput(%s, %d)' %(next_pin_pv, inpuck_slot_id_athand))
                                #sleep(5)
                                #run [ 2] HTL_TO_SMP
                                #caput(rbt_job_pv, 2)
                                caput(rbt_job_pv, 'HTL_TO_SMP')
                                print('caput(%s, %s)' %(rbt_job_pv, 'HTL_TO_SMP'))
                                sleep(11)
                            print('Running auto-centring...')
                            centreOK = autoCentrePin()
                            print('centreOK = %s' %(centreOK))
                            inBeamPosition_athand = self.autocentring_translation_x.getPosition()
                            outOfBeamPosition_athand = inBeamPosition_athand + self.additive_displacement_for_outOfBeamPos
                            print('inBeamPosition = %.3f, outOfBeamPosition = %.3f' %(inBeamPosition_athand,outOfBeamPosition_athand))
                            print('\nRunning scan %d (of %d)...' %(i+1,len(self.scan_lst)))
                            interruptable()
                            tomoFlyScan(inBeamPosition=inBeamPosition_athand, outOfBeamPosition=outOfBeamPosition_athand, exposureTime=exposureTime_athand, start=start_athand, stop=stop_athand, step=step_athand, imagesPerDark=imagesPerDark_athand, imagesPerFlat=imagesPerFlat_athand)
                            interruptable()
                            #sleep(5)
                            print('Finished running scan %d (of %d)!\n' %(i+1,len(self.scan_lst)))
                            jns=beamline_parameters.JythonNameSpaceMapping()
                            out_dct = self.scan_lst[i]
                            barcode_out = caget(pin_barcode_pv)                             #eg u'CA00CJ6595::::'
                            out_dct['barcode_out'] = barcode_out.replace(':','')
                            out_dct['nexus_scan_file'] = jns.lastScanDataPoint().currentFilename
                            wter.writerow(out_dct)
                            if i < len(self.scan_lst)-1:
                                scn_imminent = self.scan_lst[i+1]
                                puck_id_imminent = int(scn_imminent['puck_id'])
                                inpuck_slot_id_imminent = int(scn_imminent['inpuck_slot_id'])
                                print('puck_id_imminent = %d, inpuck_slot_id_imminent = %d' %(puck_id_imminent, inpuck_slot_id_imminent))
                                self.move_stages_to_exchange_cfg()
                                #set next puck and pin
                                caput(next_puck_pv, puck_id_imminent)
                                caput(next_pin_pv, inpuck_slot_id_imminent)
                                print('caput(%s, %d)' %(next_puck_pv, puck_id_imminent))
                                print('caput(%s, %d)' %(next_pin_pv, inpuck_slot_id_imminent))
                                sleep(5)
                                #run [ 3] SMP_EXCHANGE
                                #caput(rbt_job_pv, 3)
                                caput(rbt_job_pv, 'SMP_EXCHANGE')
                                print('caput(%s, %s)' %(rbt_job_pv, 'SMP_EXCHANGE'))
                                sleep(18)
                            else:
                                self.move_stages_to_exchange_cfg()
                                #run [ 4] SMP_TO_HTL
                                #caput(rbt_job_pv, 4)
                                caput(rbt_job_pv, 'SMP_TO_HTL')
                                print('caput(%s, %s)' %(rbt_job_pv, 'SMP_TO_HTL'))
                                sleep(10)
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
                print("All done!")
    
    def preview(self, start_zidx, nitems=1):
        for itm in islice(self.for_scan_ordered_dct.items(), start_zidx, start_zidx+nitems):
            print itm
    
    def to_string(self):
        print("fpath = %s" %(self.fpath))
        print("logdir_path = %s" %(self.logdir_path))
        print("log_fpath = %s" %(self.log_fpath))
        print("nscans = %s" %(self.nscans))
        print("additive_displacement_for_outOfBeamPos = %.3f" %(self.additive_displacement_for_outOfBeamPos))
        print('autocentring_translation_x = %s, currently positioned at %.3f' %(self.autocentring_translation_x.getName(),self.autocentring_translation_x.getPosition()))
    
    
#    def __str__(self):
#        pass
#    def __repr__(self):
#        pass
    def __call__(self):
        self.to_string()

tomomatic = Tomomatic()
print('\n Created an instance called tomomatic!')
