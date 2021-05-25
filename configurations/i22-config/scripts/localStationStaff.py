# ===================================================================================
# Configuration of servers after restart/reset
# ===================================================================================

# Uncomment (and edit) if non-standard motors are required for use with ncdgridscan
gridscan_stage = [base_x, base_y]

# Uncomment to change which channels and gain settings are used for It and I0 values in nexus files
# NB Commenting this out again after a reset will not return the settings to default until the servers
#    are restarted
#scaler_channels = {'It': NcdChannel(channel=3, scaling=bs2diodegain),
#                   'I0': NcdChannel(channel=1, scaling=d4d2gain)}

# ===================================================================================
# Add any commands that needs to be run after each restart/reset below this line
# ===================================================================================
#diode_y = SingleEpicsPositionerClass('diode_y', 'BL22I-MO-TABLE-05:Y', 'BL22I-MO-TABLE-05:Y.RBV' , 'BL22I-MO-TABLE-05:Y.DMOV' , 'BL22I-MO-TABLE-05:Y.STOP','mm', '%.4f')
#diode_x = SingleEpicsPositionerClass('diode_x', 'BL22I-MO-TABLE-05:X', 'BL22I-MO-TABLE-05:X.RBV' , 'BL22I-MO-TABLE-05:X.DMOV' , 'BL22I-MO-TABLE-05:X.STOP','mm', '%.4f')
from gdascripts.pd.epics_pds import DisplayEpicsPVClass

qbpm1_xpos = DisplayEpicsPVClass("qbpm1_xpos","BL22I-EA-XBPM-01:PosX:MeanValue_RBV","um","%.6f")
qbpm1_ypos = DisplayEpicsPVClass("qbpm1_ypos","BL22I-EA-XBPM-01:PosY:MeanValue_RBV","um","%.6f")
qbpm1_quad1 = DisplayEpicsPVClass("qbpm1_quad1","BL22I-EA-XBPM-01:Cur1:MeanValue_RBV","A","%.6e")
qbpm1_quad2 = DisplayEpicsPVClass("qbpm1_quad2","BL22I-EA-XBPM-01:Cur2:MeanValue_RBV","A","%.6e")
qbpm1_quad3 = DisplayEpicsPVClass("qbpm1_quad3","BL22I-EA-XBPM-01:Cur3:MeanValue_RBV","A","%.6e")
qbpm1_quad4 = DisplayEpicsPVClass("qbpm1_quad4","BL22I-EA-XBPM-01:Cur4:MeanValue_RBV","A","%.6e")
qbpm1_total = DisplayEpicsPVClass("qbpm1_total","BL22I-EA-XBPM-01:SumAll:MeanValue_RBV","A","%.6e")
qbpm2_xpos = DisplayEpicsPVClass("qbpm2_xpos","BL22I-EA-XBPM-02:PosX:MeanValue_RBV","um","%.6f")
qbpm2_ypos = DisplayEpicsPVClass("qbpm2_ypos","BL22I-EA-XBPM-02:PosY:MeanValue_RBV","um","%.6f")
qbpm2_quad1 = DisplayEpicsPVClass("qbpm2_quad1","BL22I-EA-XBPM-02:Cur1:MeanValue_RBV","A","%.6e")
qbpm2_quad2 = DisplayEpicsPVClass("qbpm2_quad2","BL22I-EA-XBPM-02:Cur2:MeanValue_RBV","A","%.6e")
qbpm2_quad3 = DisplayEpicsPVClass("qbpm2_quad3","BL22I-EA-XBPM-02:Cur3:MeanValue_RBV","A","%.6e")
qbpm2_quad4 = DisplayEpicsPVClass("qbpm2_quad4","BL22I-EA-XBPM-02:Cur4:MeanValue_RBV","A","%.6e")
qbpm2_total = DisplayEpicsPVClass("qbpm2_total","BL22I-EA-XBPM-02:SumAll:MeanValue_RBV","A","%.6e")

sample_diode = DisplayEpicsPVClass("sample_diode","BL22I-EA-TTRM-01:Cur1:MeanValue_RBV","A","%.6e")
user_tetrAMM_ch1 = DisplayEpicsPVClass("user_tetrAMM_ch1","BL22I-EA-TTRM-01:Cur1:MeanValue_RBV","A","%.6e")
user_tetrAMM_ch2 = DisplayEpicsPVClass("user_tetrAMM_ch2","BL22I-EA-TTRM-01:Cur2:MeanValue_RBV","A","%.6e")
user_tetrAMM_ch3 = DisplayEpicsPVClass("user_tetrAMM_ch3","BL22I-EA-TTRM-01:Cur3:MeanValue_RBV","A","%.6e")
user_tetrAMM_ch4 = DisplayEpicsPVClass("user_tetrAMM_ch4","BL22I-EA-TTRM-01:Cur4:MeanValue_RBV","A","%.6e")

def feedback_SS():
    caput("BL22I-OP-KBM-01:HFM:FBS4.INP","BL22I-EA-XBPM-01:PosX:MeanValue_RBV")
    caput("BL22I-OP-KBM-01:VFM:FBS4.INP","BL22I-EA-XBPM-01:PosY:MeanValue_RBV")
    caput("BL22I-OP-KBM-01:HFM:FBS4.KP", 0.001)
    caput("BL22I-OP-KBM-01:VFM:FBS4.KP", -0.001)
    caput("BL22I-OP-KBM-01:HFM:FBS4.KI", 0.41667)
    caput("BL22I-OP-KBM-01:VFM:FBS4.KI", 0.5208)
    caput("BL22I-EA-XBPM-01:DRV:Geometry", "Square")
    print "Feedback running from XBPM1 at secondary source"
    return
    
def feedback_EH():
    caput("BL22I-OP-KBM-01:HFM:FBS4.INP","BL22I-EA-XBPM-02:PosX:MeanValue_RBV")
    caput("BL22I-OP-KBM-01:VFM:FBS4.INP","BL22I-EA-XBPM-02:PosY:MeanValue_RBV")
    caput("BL22I-OP-KBM-01:HFM:FBS4.KP", 0.001)
    caput("BL22I-OP-KBM-01:VFM:FBS4.KP", -0.001)
    caput("BL22I-OP-KBM-01:HFM:FBS4.KI", 0.41667)
    caput("BL22I-OP-KBM-01:VFM:FBS4.KI", 0.5208)
    caput("BL22I-EA-TTRM-01:DRV:Geometry", "Square")
    print "Feedback running from XBPM2 in experimental hutch"
    return
    
def feedback_auto():
    caput("BL22I-OP-KBM-01:HFM:FBS4:AUTO","Auto")
    caput("BL22I-OP-KBM-01:VFM:FBS4:AUTO","Auto")
    print "Feedback running in auto mode"
    return

def feedback_off():
    caput("BL22I-OP-KBM-01:HFM:FBS4:AUTO","Manual")
    caput("BL22I-OP-KBM-01:HFM:FBS4.FBON","Off")
    caput("BL22I-OP-KBM-01:VFM:FBS4:AUTO","Manual")
    caput("BL22I-OP-KBM-01:VFM:FBS4.FBON","Off")
    print "Feedback is OFF!"
    
def feedback_on():
    caput("BL22I-OP-KBM-01:HFM:FBS4:AUTO","Manual")
    caput("BL22I-OP-KBM-01:HFM:FBS4.FBON","On")
    caput("BL22I-OP-KBM-01:VFM:FBS4:AUTO","Manual")
    caput("BL22I-OP-KBM-01:VFM:FBS4.FBON","On")
    print "Feedback is ON in manual mode"
    
def optimise_pitch():
    if eh_shutter.getPosition() == "Closed":
        print "Shutter is closed, using D4D1 to optimise"
        feedback_off()
        pos d4filter 'IL Diode VFM'
        d4d1gain.setFixed(0)
        if d4d1.getPosition() > 1e6:
            rscan dcm_finepitch -100 100 1 d4d1
            inc dcm_finepitch -100
            go peak
        else:
            print "Not enough beam to optimise - Aborting here"
        pos d4filter 'Clear deflected'
        feedback_auto()
        return
    else:
        print "Shutter is open, using QBPM1 to optimise"
        feedback_off()
        if qbpm1_total.getPosition() > 1e-8:
            rscan dcm_finepitch -100 100 1 qbpm1_total
            inc dcm_finepitch -100
            go peak
        else:
            print "Not enough beam to optimise - Aborting here"
        feedback_auto()
        return
