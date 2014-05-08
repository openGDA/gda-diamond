from gdascripts.metadata.metadata_commands import meta_add
from gda.factory import Finder

# remove after 8.36
def setMetadata():
    addList= ["bda_x","bda_y","m1_x","m1_pitch","m1_y","m1_roll","m1_yaw","s1_xsize",
                   "s1_xcentre","s1_xminus","s1_xplus","s1_ysize","s1_ycentre","s1_yminus",
                   "s1_yplus","pgm_cff","grating_pitch","grating_x","m2_x","m2_pitch","m3_x",
                   "m3_pitch","m3_yaw","m3_roll","m3_y","m4_x","m4_pitch","m4_yaw","m4_roll",
                   "m4_ellipticity","m4_curvature","pgm_energy","idgap"]

    finder = Finder.getInstance()
    for s in addList:
        scannable = finder.find(s)
        if scannable is not None:
            meta_add(scannable)
        else:
            print 'This scannable does not exist:',s
        

    
    
    
    
    