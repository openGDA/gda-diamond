from detector_control_class import DetectorControlClass
pds=[]
#Ie2 
llimIe2=DetectorControlClass('llimIe2', 'BL11J-DI-IMON-01:E1:LLIM', 'BL11I-DI-IMON-01:E1:LLIM:RBV', 'mv', '%4.0f'); pds.append(llimIe2)
ulimIe2=DetectorControlClass('ulimIe2', 'BL11J-DI-IMON-01:E1:ULIM', 'BL11I-DI-IMON-01:E1:ULIM:RBV', 'mv', '%4.0f'); pds.append(ulimIe2)
pmtIe2=DetectorControlClass('pmtIe2', 'BL11J-DI-IMON-01:E1:CTRL', 'BL11I-DI-IMON-01:E1:CTRL:RBV', 'mv', '%4.0f'); pds.append(pmtIe2)

print "finished ETL Detector object creation"
    