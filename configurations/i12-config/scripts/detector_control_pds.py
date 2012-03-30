from detector_control_class import DetectorControlClass
pds=[]
# Optic Hutch 2 ETL Detector 
#llimI0oh2=DetectorControlClass('llimI0oh2', 'BL12I-AL-ATTN-02:ETL:LLIM', 'BL12I-AL-ATTN-02:ETL:LLIM:RBV', 'mv', '%4.0f'); pds.append(llimI0oh2)
#ulimI0oh2=DetectorControlClass('ulimI0oh2', 'BL12I-AL-ATTN-02:ETL:ULIM', 'BL12I-AL-ATTN-02:ETL:ULIM:RBV', 'mv', '%4.0f'); pds.append(ulimI0oh2)
#pmtI0oh2=DetectorControlClass('pmtI0oh2',   'BL12I-AL-ATTN-02:ETL:CTRL', 'BL12I-AL-ATTN-02:ETL:CTRL:RBV', 'mv', '%4.0f'); pds.append(pmtI0oh2)
# Experiment Hutch 1 ETL Detector
#llimI0eh1=DetectorControlClass('llimI0eh1', 'BL12I-DI-PHDGN-02:ETL:LLIM', 'BL12I-DI-PHDGN-02:ETL:LLIM:RBV', 'mv', '%4.0f'); pds.append(llimI0eh1)
#ulimI0eh1=DetectorControlClass('ulimI0eh1', 'BL12I-DI-PHDGN-02:ETL:ULIM', 'BL12I-DI-PHDGN-02:ETL:ULIM:RBV', 'mv', '%4.0f'); pds.append(ulimI0eh1)
#pmtI0eh1=DetectorControlClass('pmtI0eh1',   'BL12I-DI-PHDGN-02:ETL:CTRL', 'BL12I-DI-PHDGN-02:ETL:CTRL:RBV', 'mv', '%4.0f'); pds.append(pmtI0eh1)
# External Hutch ETL detector
#llim31=DetectorControlClass('llim31', 'BL11I-EA-MAC-03:E1:LLIM', 'BL11I-EA-MAC-03:E1:LLIM:RBV', 'mv', '%4.0f'); pds.append(llim31)
#ulim31=DetectorControlClass('ulim31', 'BL11I-EA-MAC-03:E1:ULIM', 'BL11I-EA-MAC-03:E1:ULIM:RBV', 'mv', '%4.0f'); pds.append(ulim31)
#pmt31=DetectorControlClass('pmt31', 'BL11I-EA-MAC-03:E1:CTRL', 'BL11I-EA-MAC-03:E1:CTRL:RBV', 'mv', '%4.0f'); pds.append(pmt31)

print "finished ETL Detector object creation"
    