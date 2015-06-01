# detector_control_pds copied from i11 config scripts, last modified r20930 13/11/09 fy65
# Reduced down to only the first sensor & updated to i15 PVs.
from localStationScripts.detector_control_class import DetectorControlClass
pds=[]
#llim11=DetectorControlClass('llim11', 'BL11I-EA-MAC-01:E1:LLIM',    'BL11I-EA-MAC-01:E1:LLIM:RBV',    'mv', '%4.0f'); pds.append(llim11)
#ulim11=DetectorControlClass('ulim11', 'BL11I-EA-MAC-01:E1:ULIM',    'BL11I-EA-MAC-01:E1:ULIM:RBV',    'mv', '%4.0f'); pds.append(ulim11)
#pmt11=DetectorControlClass( 'pmt11',  'BL11I-EA-MAC-01:E1:CTRL',    'BL11I-EA-MAC-01:E1:CTRL:RBV',    'mv', '%4.0f'); pds.append(pmt11)
etl_lowlim= DetectorControlClass('etl_lowlim', 'BL15I-EA-DET-01:M1:D0:LLIM', 'BL15I-EA-DET-01:M1:D0:LLIM:RBV', 'mV', '%4.0f'); pds.append(etl_lowlim)
etl_uplim = DetectorControlClass('etl_uplim',  'BL15I-EA-DET-01:M1:D0:ULIM', 'BL15I-EA-DET-01:M1:D0:ULIM:RBV', 'mV', '%4.0f'); pds.append(etl_uplim)
etl_gain  = DetectorControlClass('etl_gain',   'BL15I-EA-DET-01:M1:D0:CTRL', 'BL15I-EA-DET-01:M1:D0:CTRL:RBV', 'V',  '%4.0f'); pds.append(etl_gain)

print "Created ETL detector objects:",
print [pd.getName() for pd in pds]