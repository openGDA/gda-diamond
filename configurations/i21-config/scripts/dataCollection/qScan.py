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

def qscan(beam_energy,beam_polarisation,s5v1gap_val,saazimuth_val,satilt_val,say_val,\
                start,step,n_points,energy_sample,sapolaroffset,thts_val,vec,a_val,\
                sax_sample, saz_sample,n_frames_sample,sample_exposure,\
                sax_elastic,saz_elastic,n_frames_elastic,elastic_exposure):
    id_gap=idgap_fn(beam_energy,beam_polarisation) #for this energy and polarisation
    if beam_polarisation=='LV':
        row_phase=28
    elif beam_polarisation=='LH':
        row_phase = 0
        
    # Switch to LV
    idscannable.moveTo([id_gap, beam_polarisation, row_phase]) 
    # set beam energy
    energy.moveTo(beam_energy)  # @UndefinedVariable
    # set slit s5 gap
    s5v1gap.moveTo(s5v1gap_val)
    # set sample positions
    saazimuth.moveTo(saazimuth_val)
    satilt.moveTo(satilt_val)
    say.moveTo(say_val)
    
    #add metadata for this collection
    meta_add("scan_origin_id", nfn())
    meta_add("scan_levels", 1)
    meta_add("scan0_name", "qval")
    meta_add("scan0_length", n_points)
    
    for i in range(n_points):
        
        energy.moveTo(beam_energy)  # @UndefinedVariable
        qval = start + i*step
        sapolarval = qtransferrlu2sapolar(energy_sample,qval,sapolaroffset,thts_val,vec,a_val) 
        sapolar.moveTo(sapolarval)
        
        # collect point number and qval value
        meta_add("scan0_index", i)
        meta_add("Outer", qval)
    
        # Move to sample position
        sax.moveTo(sax_sample)
        saz.moveTo(saz_sample)
        
        # collect sample type and elastic reference scan number
        meta_add("sample_type", "sample")
        meta_add("elastic_scan", nfn()+1)
        
        print('Total number of points is %d. Point number %d is at qtransferrlupara=%.3f, and th=%.3f for sample'%(n_points,i+1.0,qval,sapolarval))
        scan(dummies.x, 1, n_frames_sample, 1, andor, sample_exposure)  # @UndefinedVariable
    
        # Move to the carbon tape position
        sax.moveTo(0.5)
        sax.moveTo(sax_elastic)
        saz.moveTo(saz_elastic)
        
        # collect sample type and relevant sample scan number
        meta_add("sample_type", "elastic_reference")
        meta_add("sample_scan", nfn()-1)
        
        print('Total number of points is %d. Point number %d is at qtransferrlupara=%.3f, and th=%.3f for ctape'%(n_points,i+1.0,qval,sapolarval))
        scan(dummies.x, 1, n_frames_elastic, 1, andor, elastic_exposure)  # @UndefinedVariable
        
        sleep(0.5)
        print('*******************************************************************')
        print('\n')    