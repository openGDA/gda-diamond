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

sample_diode = DisplayEpicsPVClass("sample_diode","BL22I-EA-TTRM-02:Cur3:MeanValue_RBV","A","%.6e")
user_tetrAMM_ch1 = DisplayEpicsPVClass("user_tetrAMM_ch1","BL22I-EA-TTRM-01:Cur1:MeanValue_RBV","A","%.6e")
user_tetrAMM_ch2 = DisplayEpicsPVClass("user_tetrAMM_ch2","BL22I-EA-TTRM-01:Cur2:MeanValue_RBV","A","%.6e")
user_tetrAMM_ch3 = DisplayEpicsPVClass("user_tetrAMM_ch3","BL22I-EA-TTRM-01:Cur3:MeanValue_RBV","A","%.6e")
user_tetrAMM_ch4 = DisplayEpicsPVClass("user_tetrAMM_ch4","BL22I-EA-TTRM-01:Cur4:MeanValue_RBV","A","%.6e")
