'''
Created on 10 Jan 2018

@author: fy65
'''
from calibration.Energy2Gap4ID import idgap_calc
from gdaserver import s5v1gap, idscannable, phi, y, th, x,z, andor
from gdascripts.metadata.metadata_commands import meta_add, meta_rm
from i21commands.dirFileCommands import nfn
from gdascripts.scan.installStandardScansWithProcessing import scan
from dataCollection.MomentumTransfer import qtransferrlu2sapolar
from time import sleep
from __main__ import energy, interruptable, acquireRIXS  # @UnresolvedImport

def qscan(**kwargs):
    '''perform q scan over the specified q range using the M5lq mirror.
    At each q value, both sample and ctape scattering data are collected 
    with different exposure time and number of images per point specified.
    
    Note: id_gap is calculated using function idgap_fn() in module calibration.Energy2Gap4ID
    which has to be kept in sync with method idgap_fn() in module calibration.Energy_class.
    
    @param kwargs: a dictionary containing 25 parameters required for q scan
    keys in the dictionary argument are 
    
    ['a', 'beam_energy', 'beam_polarisation', 'c', 'elastic_exposure_time', 'energy_sample', 
     'n_frames_per_point_elastic', 'n_frames_per_point_sample', 'n_points', 'qEnd', 'qStart', 
     'qStep', 's5v1gap_val', 'saazimuth_val', 'sample_exposure_time', 'sapolar_offset', 
     'satilt_val', 'sax_ctape', 'sax_sample', 'say_ctape', 'say_sample', 'saz_ctape', 
     'saz_sample', 'thts_val', 'vec']
     
     These keys are used to retrieve its corresponding value in this code.

    In addition the following q scan metadata are also recorded in data file:
    
     ["scan_origin_id", "scan_levels", "scan0_name", "scan0_length",
      "scan0_index","qval", "sample_type","elastic_scan", "sample_scan"]
      
    These are required by data reduction software. 
    These metadata are dynamically add before scan, updated during scan, and removed after scan
    so it will not appears in files not related to q scan!
    '''
    id_gap=idgap_calc(kwargs['beam_energy'],kwargs['beam_polarisation']) #for this energy and polarisation
    if kwargs['beam_polarisation']=='LV':
        row_phase=28
    elif kwargs['beam_polarisation']=='LH':
        row_phase = 0
        
    if not kwargs['dry_run']:
        # Switch to LV
        idscannable.moveTo([id_gap, kwargs['beam_polarisation'], row_phase]) 
        # set beam energy
        energy.moveTo(kwargs['beam_energy'])
        # set slit s5 gap
        s5v1gap.moveTo(kwargs['s5v1gap_val'])
        # set sample positions
        phi.moveTo(kwargs['saazimuth_val'])
        sa.chi.moveTo(kwargs['satilt_val'])  # @UndefinedVariable
    
    
        #add qscan metadata for this collection
        meta_add("scan_origin_id", nfn())
        meta_add("scan_levels", 1)
        meta_add("scan0_name", "qval")
        meta_add("scan0_length", kwargs['n_points'])
    
    for i in range(kwargs['n_points']):
        
        if not kwargs['dry_run']:
            energy.moveTo(kwargs['beam_energy'])  
        qval = kwargs['qStart'] + i*kwargs['qStep']
        sapolarval = qtransferrlu2sapolar(kwargs['energy_sample'],qval,kwargs['sapolar_offset'],kwargs['thts_val'],kwargs['vec'],kwargs['a']) 
        if not kwargs['dry_run']:
            th.moveTo(sapolarval)
            interruptable()  # @UndefinedVariable
        
        if not kwargs['dry_run']:
            # collect point number and qval value
            meta_add("scan0_index", i)
            meta_add("qval", qval)
    
            # Move to sample position
            x.moveTo(kwargs['sax_sample'])
            interruptable()  # @UndefinedVariable
            y.moveTo(kwargs['say_sample'])
            interruptable()  # @UndefinedVariable
            z.moveTo(kwargs['saz_sample'])
            interruptable()  # @UndefinedVariable
            
            # collect sample type and elastic reference scan number
            meta_add("sample_type", "sample")
            meta_add("elastic_scan", nfn()+1)
        
        print('Total number of points is %d. Point number %d is at qtransferrlupara=%.3f, and th=%.3f for sample'%(kwargs['n_points'],i+1.0,qval,sapolarval))
        if not kwargs['dry_run']:
            acquireRIXS(kwargs['n_frames_per_point_sample'], andor, kwargs['sample_exposure_time'])
            #scan(dummies.x, 1, kwargs['n_frames_per_point_sample'], 1, andor, kwargs['sample_exposure_time'])
            interruptable()  # @UndefinedVariable
    
            # Move to the carbon tape position
            #sax.moveTo(0.5)
            x.moveTo(kwargs['sax_ctape'])
            interruptable()  # @UndefinedVariable
            y.moveTo(kwargs['say_ctape'])
            interruptable()  # @UndefinedVariable
            z.moveTo(kwargs['saz_ctape'])
            interruptable()  # @UndefinedVariable
            
            # collect sample type and relevant sample scan number
            meta_rm("elastic_scan")
            meta_add("sample_type", "elastic_reference")
            meta_add("sample_scan", nfn()-1)
        
        print('Total number of points is %d. Point number %d is at qtransferrlupara=%.3f, and th=%.3f for ctape'%(kwargs['n_points'],i+1.0,qval,sapolarval))
        if not kwargs['dry_run']:
            acquireRIXS(kwargs['n_frames_per_point_elastic'], andor, kwargs['elastic_exposure_time'])
            #scan(dummies.x, 1, kwargs['n_frames_per_point_elastic'], 1, andor, kwargs['elastic_exposure_time'])
            interruptable()  # @UndefinedVariable
            sleep(0.5)
            meta_rm("sample_scan")
        print('*******************************************************************')
        print('\n')    

        if not kwargs['dry_run']:
            #remove qscan metadata for this collection
            meta_rm("scan_origin_id", "scan_levels", "scan0_name", "scan0_length",\
                    "scan0_index","qval", "sample_type")

def qscanclean():
    meta_rm("scan_origin_id", "scan_levels", "scan0_name", "scan0_length",\
            "scan0_index","qval", "sample_type")    
    