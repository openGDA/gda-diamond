'''
Created on 10 Jan 2018

@author: fy65
'''
from calibration.Energy2Gap4ID import idgap_fn
from gdaserver import s5v1gap, idscannable, saazimuth, satilt, say, sapolar, sax,\
    saz, andor
from gdascripts.metadata.metadata_commands import meta_add
from i21commands.dirFileCommands import nfn
from gdascripts.scan.installStandardScansWithProcessing import scan
from dataCollection.MomentumTransfer import qtransferrlu2sapolar
from time import sleep

def qscan(**kwargs):
    id_gap=idgap_fn(kwargs['beam_energy'],kwargs['beam_polarisation']) #for this energy and polarisation
    if kwargs['beam_polarisation']=='LV':
        row_phase=28
    elif kwargs['beam_polarisation']=='LH':
        row_phase = 0
        
    # Switch to LV
    idscannable.moveTo([id_gap, kwargs['beam_polarisation'], row_phase]) 
    # set beam energy
    energy.moveTo(kwargs['beam_energy'])  # @UndefinedVariable
    # set slit s5 gap
    s5v1gap.moveTo(kwargs['s5v1gap_val'])
    # set sample positions
    saazimuth.moveTo(kwargs['saazimuth_val'])
    satilt.moveTo(kwargs['satilt_val'])
    
    
    #add metadata for this collection
    meta_add("scan_origin_id", nfn())
    meta_add("scan_levels", 1)
    meta_add("scan0_name", "qval")
    meta_add("scan0_length", kwargs['n_points'])
    
    for i in range(kwargs['n_points']):
        
        energy.moveTo(beam_energy)  # @UndefinedVariable
        qval = kwargs['qStart'] + kwargs['i*qStep']
        sapolarval = qtransferrlu2sapolar(kwargs['energy_sample'],qval,kwargs['sapolar_offset'],kwargs['thts_val'],kwargs['vec'],kwargs['a']) 
        sapolar.moveTo(sapolarval)
        
        # collect point number and qval value
        meta_add("scan0_index", i)
        meta_add("qval", qval)
    
        # Move to sample position
        sax.moveTo(kwargs['sax_sample'])
        say.moveTo(kwargs['say_sample'])
        saz.moveTo(kwargs['saz_sample'])
        
        # collect sample type and elastic reference scan number
        meta_add("sample_type", "sample")
        meta_add("elastic_scan", nfn()+1)
        
        print('Total number of points is %d. Point number %d is at qtransferrlupara=%.3f, and th=%.3f for sample'%(kwargs['n_points'],i+1.0,qval,sapolarval))
        scan(dummies.x, 1, kwargs['n_frames_per_point_sample'], 1, andor, kwargs['sample_exposure_time'])  # @UndefinedVariable
    
        # Move to the carbon tape position
        sax.moveTo(0.5)
        sax.moveTo(kwargs['sax_ctape'])
        sax.moveTo(kwargs['say_ctape'])
        saz.moveTo(kwargs['saz_ctape'])
        
        # collect sample type and relevant sample scan number
        meta_add("sample_type", "elastic_reference")
        meta_add("sample_scan", nfn()-1)
        
        print('Total number of points is %d. Point number %d is at qtransferrlupara=%.3f, and th=%.3f for ctape'%(kwargs['n_points'],i+1.0,qval,sapolarval))
        scan(dummies.x, 1, kwargs['n_frames_per_point_elastic'], 1, andor, kwargs['elastic_exposure_time'])  # @UndefinedVariable
        
        sleep(0.5)
        print('*******************************************************************')
        print('\n')    