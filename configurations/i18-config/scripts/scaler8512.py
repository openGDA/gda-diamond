# File for reading the 8512 scalars

#from gda.script.pd.scalar8512_pds import ScalarChannelEpicsPVClass
#execfile("/home/nv23/workspace/gda_trunk/scripts/gdascripts/pd/scaler8512_pds.py")

pvScalerTP='BL18I-DI-8512-01:PRESET'

pvScalerCNT='BL18I-DI-8512-01:STARTCOUNT'

print "Setting up PVs for CA1"

pvCA11C = 'BL18I-DI-PHDGN-01:DIODE:IF'
pvCA12C = 'BL18I-DI-PHDGN-02:DIODE:IF'
pvCA13C = 'BL18I-DI-PHDGN-03:DIODE:IF'
pvCA14C = 'BL18I-DI-PHDGN-05:B:DIODE:IF'

print "Setting up PVs for CA2"

pvCA21C = 'BL18I-DI-IAMP-02:I1F'
pvCA22C = 'BL18I-DI-IAMP-02:I2F'
pvCA23C = 'BL18I-DI-IAMP-02:I3F'
pvCA24C = 'BL18I-DI-IAMP-02:I4F'

print "Setting up PVs for CA3"

pvCA31C = 'BL18I-DI-PHDGN-06:B:DIODE:IF'
pvCA32C = 'BL18I-DI-PHDGN-07:B:DIODE:IF'
pvCA33C = 'BL18I-DI-IAMP-03:I3F'
pvCA34C = 'BL18I-DI-IAMP-03:I4F'

print "Creating objects..."

ca11s = ScalerChannelEpicsPVClass('ca11s',pvScalerTP, pvScalerCNT, pvCA11C)
ca12s = ScalerChannelEpicsPVClass('ca12s',pvScalerTP, pvScalerCNT, pvCA12C)
ca13s = ScalerChannelEpicsPVClass('ca13s',pvScalerTP, pvScalerCNT, pvCA13C)
ca14s = ScalerChannelEpicsPVClass('ca14s',pvScalerTP, pvScalerCNT, pvCA14C)

ca21s = ScalerChannelEpicsPVClass('ca21s',pvScalerTP, pvScalerCNT, pvCA21C)
ca22s = ScalerChannelEpicsPVClass('ca22s',pvScalerTP, pvScalerCNT, pvCA22C)
ca23s = ScalerChannelEpicsPVClass('ca23s',pvScalerTP, pvScalerCNT, pvCA23C)
ca24s = ScalerChannelEpicsPVClass('ca24s',pvScalerTP, pvScalerCNT, pvCA24C)

ca31s = ScalerChannelEpicsPVClass('ca31s',pvScalerTP, pvScalerCNT, pvCA31C)
ca32s = ScalerChannelEpicsPVClass('ca32s',pvScalerTP, pvScalerCNT, pvCA32C)
ca33s = ScalerChannelEpicsPVClass('ca33s',pvScalerTP, pvScalerCNT, pvCA33C)
ca34s = ScalerChannelEpicsPVClass('ca34s',pvScalerTP, pvScalerCNT, pvCA34C)
