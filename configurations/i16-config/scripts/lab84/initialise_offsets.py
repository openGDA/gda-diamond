'''
All of these positions are based on persistent values which are required
for localStation.py to run to complete without errors in dummy mode.
 
In dummy mode these positions need only to be set once on server start in any 
new GDA deployment. They will persist over the lifetime of this deployment.

This is converted from /i16-config/scripts/dummy/essential_positions.py to use importing objects

@author: Fajin Yuan
@since: 6 April 2023
'''

def setup_scannables_offsets():
    '''initialise offset value of a number of scannables in dummy mode.
    This should be run once after all scannables used are defined in the jython name space.
    '''
    # these offsets are required by localStation.py at GDA server startup
    from localStationScripts.startup_offsets import delta_axis_offset, cry_offset,\
        dcmharmonic, ref_offset, bragg_offset, idgap_offset, uharmonic, delta_offset,\
        eta_offset
    delta_axis_offset.asynchronousMoveTo(0)
    cry_offset.asynchronousMoveTo(5)
    dcmharmonic.asynchronousMoveTo(1)
    ref_offset.asynchronousMoveTo(2)
    bragg_offset.asynchronousMoveTo(0.271790060076)
    idgap_offset.asynchronousMoveTo(0.533034663313)
    uharmonic.asynchronousMoveTo(3)
    delta_offset.asynchronousMoveTo(0)
    eta_offset.asynchronousMoveTo(-0.7)
    
    # These positions are not essential to completing localStation, but are
    # essential for avoiding missing metadata. They are based on scan 971324
    from localStationScripts.startup_offsets import base_z_offset, m1y_offset, \
        m2_coating_offset, m2y_offset, ztable_offset
    base_z_offset.asynchronousMoveTo(-13.537191459600757)
    m1y_offset.asynchronousMoveTo(-15.366825459600758)
    m2_coating_offset.asynchronousMoveTo(11)
    m2y_offset.asynchronousMoveTo(-22.340825459600758)
    ztable_offset.asynchronousMoveTo(-19.99470545960076)

PIL3_CENTRE_I_DEFAULT=239
PIL3_CENTRE_J_DEFAULT=106

def setup_pil3_centre():
    '''initialise detector centre position
    '''
    from dummy.localStationStaff import pil3_centre_i, pil3_centre_j
    pil3_centre_i.asynchronousMoveTo(PIL3_CENTRE_I_DEFAULT)
    pil3_centre_j.asynchronousMoveTo(PIL3_CENTRE_J_DEFAULT)
    