# This script gives a selection of examples of how to create a GDA variable from a non moveable EPICS PV.
# To use those here remove the # or to create new ones copy to end, remove # and edit as approporiate
# The scan line at the bottom shows useage of the variables set up

#bufferpressure=DisplayEpicsPVClass("bufferpressure","BL22I-CG-CRYO-01:NBUFF","psi","%.3e")
#poweroutput=DisplayEpicsPVClass("poweroutput","BL22I-CG-CRYO-01:HPOW","psi","%.3e")
#returntemp=DisplayEpicsPVClass("returntemp","BL22I-CG-CRYO-01:RETUT","psi","%.3e")
#flowrate=DisplayEpicsPVClass("flowrate","BL22I-CG-CRYO-01:NFLOW","psi","%.3e")
#feedpressure=DisplayEpicsPVClass("feedpressure","BL22I-CG-CRYO-01:PFEED","psi","%.3e")
#mainnitrogenlevel=DisplayEpicsPVClass("mainnitrogenlevel","BL22I-CG-CRYO-01:MNLEV","Hz","%.3e")
#nitrogenlevel=DisplayEpicsPVClass("nitrogenlevel","BL22I-CG-CRYO-01:NLEV","Hz","%.3e")
#pumpoutput=DisplayEpicsPVClass("pumpoutput","BL22I-CG-CRYO-01:PUMPN","Hz","%.3e")
# diode=DisplayEpicsPVClass("","BL22I-DI-IAMP-11:PHD1:I","V","%.3f")
#nitrogen=DisplayEpicsPVClass("","BL22I-CG-CRYO-01:MNLEV","Hz","%.3f")
# caldiode=DisplayEpicsPVClass("","BL22I-RS-ABSB-02:DIODE:I","V","%.3f")

#scan pxyx 0 96 0.02 normorange s4xplusi ringcurrent pumpoutput1 nitrogenlevel1 mainnitrogenlevel1 feedpressure1 bufferpressure1 flowrate1 returntemp1 poweroutput1
#d13d1=DisplayEpicsPVClass("","BL22I-DI-PHDGN-13:DIODE:I","V","%.3f")
#readback=DisplayEpicsPVClass("readback","BL22I-OP-DCM-01:FPMTR:FFB.CVAL","V","%d")
#adcYminus=DisplayEpicsPVClass("adcYminus","BL22I-AL-SLITS-02:Y:MINUS:I:FFB.RVAL","V","%d")

#nl= nitrogenlevel1=DisplayEpicsPVClass("nl","BL22I-CG-CRYO-01:MNLEV","Hz","%.3e")
#s2ypi = DisplayEpicsPVClass("s2ypi","BL22I-AL-SLITS-02:Y:PLUS:I:FFB.RVAL","V","%.5e")
#s2ymi = DisplayEpicsPVClass("s2ymi","BL22I-AL-SLITS-02:Y:MINUS:I:FFB.RVAL","V","%.5e")
#s2diff = DisplayEpicsPVClass("s2diff","BL22I-OP-DCM-01:FPMTR:FFB.ERR","V","%.5e")
#s2cx = DisplayEpicsPVClass("s2cx","BL22I-DI-PHDGN-03:STAT:CentroidX_RBV","mm","%.5e")
#s2cy = DisplayEpicsPVClass("s2cy","BL22I-DI-PHDGN-03:STAT:CentroidY_RBV","mm","%.5e")
#s2cxs = DisplayEpicsPVClass("s2cxs","BL22I-DI-PHDGN-03:STAT:SigmaX_RBV","mm","%.5e")
#s2cys = DisplayEpicsPVClass("s2cys","BL22I-DI-PHDGN-03:STAT:SigmaY_RBV","mm","%.5e")
#d12xcent = DisplayEpicsPVClass("d12xcent","BL22I-DI-PHDGN-12:STAT:CentroidX_RBV","pixel","%.1f")
#d12ycent = DisplayEpicsPVClass("d12ycent","BL22I-DI-PHDGN-12:STAT:CentroidY_RBV","pixel","%.1f")

#valvepos = DisplayEpicsPVClass("valvepos", "BL22I-CG-CRYO-01:FILL:VALVEPOS", "%","%.2f")
#qbpmypos = DisplayEpicsPVClass("qbpmypos","BL22I-DI-PHDGN-07:BPM:YPOS","mm","%.4f")
#qbpmxpos = DisplayEpicsPVClass("qbpmxpos","BL22I-DI-PHDGN-07:BPM:XPOS","mm","%.4f")
#qbpmi = DisplayEpicsPVClass("qbpmi","BL22I-DI-PHDGN-07:BPM:INTEN","V","%.5e")
#qbpmyplus = DisplayEpicsPVClass("qbpmyplus","BL22I-DI-PHDGN-07:Y:PLUS:I","V","%.6f")
#qbpmyminus = DisplayEpicsPVClass("qbpmyminus","BL22I-DI-PHDGN-07:Y:MINUS:I","V","%.6f")
#qbpmxplus = DisplayEpicsPVClass("qbpmxplus","BL22I-DI-PHDGN-07:X:PLUS:I","V","%.6f")
#qbpmxminus = DisplayEpicsPVClass("qbpmxminus","BL22I-DI-PHDGN-07:X:MINUS:I","V","%.6f")

#sbpmypos = DisplayEpicsPVClass("sbpmypos","BL22I-AL-SLITS-04:BPM:YPOS","mm","%.4f")
#sbpmxpos = DisplayEpicsPVClass("sbpmxpos","BL22I-AL-SLITS-04:BPM:XPOS","mm","%.4f")
#sbpmi = DisplayEpicsPVClass("sbpmi","BL22I-AL-SLITS-04:BPM:INTEN","V","%.5e")
#sbpmyplus = DisplayEpicsPVClass("sbpmyplus","BL22I-AL-SLITS-04:BPM:BPMI1","V","%.6f")
#sbpmyminus = DisplayEpicsPVClass("sbpmyminus","BL22I-AL-SLITS-04:BPM:BPMI3","V","%.6f")
#sbpmxplus = DisplayEpicsPVClass("sbpmxplus","BL22I-AL-SLITS-04:BPM:BPMI4","V","%.6f")
#sbpmxminus = DisplayEpicsPVClass("sbpmxminus","BL22I-AL-SLITS-04:BPM:BPMI2","V","%.6f")
#ic = DisplayEpicsPVClass("ic","BL22I-DI-PHDGN-10:DIODE1:I","uA","%.5e")

xrayeye_centroid_x = DisplayEpicsPVClass("xrayeye_centroid_x","BL22I-DI-PHDGN-12:STAT:CentroidX_RBV","px","%.6f")
xrayeye_centroid_y = DisplayEpicsPVClass("xrayeye_centroid_y","BL22I-DI-PHDGN-12:STAT:CentroidY_RBV","px","%.6f")

EPICS_energy = DisplayEpicsPVClass("EPICS_energy", "BL22I-OP-DCM-01:ENERGY.RBV", "keV", "%.4f")

#s1ypos = DisplayEpicsPVClass("qbpmypos","BL22I-DI-IAMP-06:YPOS","mm","%.5qe")
#s1xpos = DisplayEpicsPVClass("qbpmypos","BL22I-DI-IAMP-06:YPOS","mm","%.5qe")

#roomtemp1=DisplayEpicsPVClass("roomtemp1","BL22I-EA-ROOM-01:TEMP1","deg","%5.4f")
#roomtemp2=DisplayEpicsPVClass("roomtemp2","BL22I-EA-ROOM-01:TEMP2","deg","%5.4f")
#roomtemp3=DisplayEpicsPVClass("roomtemp3","BL22I-EA-ROOM-01:TEMP3","deg","%5.4f")
#roomtemp4=DisplayEpicsPVClass("roomtemp4","BL22I-EA-ROOM-01:TEMP4","deg","%5.4f")
#roomtemp5=DisplayEpicsPVClass("roomtemp5","BL22I-EA-ROOM-01:TEMP5","deg","%5.4f")
#roomtemp6=DisplayEpicsPVClass("roomtemp6","BL22I-EA-ROOM-01:TEMP6","deg","%5.4f")

#Eurotherm=DisplayEpicsPVClass("Eurotherm","BL22I-EA-TEMPC-02:PV:RBV","deg","%5.2f")

#alioy1=DisplayEpicsPVClass("alioy1","BL22I-MO-TABLE-06:Y1.RBV","mm","%.5qe")
#mfstagey1=DisplayEpicsPVClass("mfstagey1","BL22I-MO-TABLE-07:Y.RBV","mm","%6.6f")

#crystal1_temp=DisplayEpicsPVClass("crystal1_temp","BL22I-OP-DCM-01:XTAL1:TEMP","deg","%6.3f")
#crystal2_temp=DisplayEpicsPVClass("crystal2_temp","BL22I-OP-DCM-01:XTAL2:TEMP","deg","%6.3f")
#ps=DisplayEpicsPVClass("ps","FE22I-PS-SHTR-01:STA","mm","%6.3f")

#d4sc=DisplayEpicsPVClass("d4sc","BL22I-AL-SLITS-02:X:PLUS:I:FFB","V","%6.3f")
#d6sc=DisplayEpicsPVClass("d6sc","BL22I-AL-SLITS-02:X:MINUS:I:FFB","V","%6.3f")
#s2ypi = DisplayEpicsPVClass("s2ypi","BL22I-AL-SLITS-02:Y:PLUS:I:FFB","V","%.5e")
#s2ymi = DisplayEpicsPVClass("s2ymi","BL22I-AL-SLITS-02:Y:MINUS:I:FFB","V","%.5e")

#d13diode1=DisplayEpicsPVClass("d13diode1","BL22I-DI-PHDGN-13:DIODE:I","V","%6.3f")
#i0qbpm=DisplayEpicsPVClass("i0qbpm","BL22I-DI-IAMP-06:INTEN","mm","%6.4f")
#i0s4=DisplayEpicsPVClass("i0s4","BL22I-DI-IAMP-05:INTEN","mm","%6.4f")

#ffberr=DisplayEpicsPVClass("ffberr","BL22I-OP-DCM-01:FPMTR:FFB.ERR","mm","%6.4f")
#cathode = DisplayEpicsPVClass("cathode","BL22I-EA-HV-01:VMON0:RBV","V","%.0f")
#side = DisplayEpicsPVClass("side","BL22I-EA-HV-01:VMON1:RBV","V","%.0f")
#window = DisplayEpicsPVClass("window","BL22I-EA-HV-01:VMON2:RBV","V","%.0f")
#drift = DisplayEpicsPVClass("drift","BL22I-EA-HV-01:VMON3:RBV","V","%.0f")
#cathode_i = DisplayEpicsPVClass("cathode_i","BL22I-EA-HV-01:IMON0:RBV","V","%.2f")
#side_i = DisplayEpicsPVClass("side_i","BL22I-EA-HV-01:IMON1:RBV","V","%.2f")
#window_i = DisplayEpicsPVClass("window_i","BL22I-EA-HV-01:IMON2:RBV","V","%.2f")
#drift_i = DisplayEpicsPVClass("drift_i","BL22I-EA-HV-01:IMON3:RBV","V","%.2f")

#ffboutput=DisplayEpicsPVClass("ffboutput","BL22I-OP-DCM-01:FPMTR:FBS2.CVAL","mm","%6.4f")

#qbpmyplus = DisplayEpicsPVClass("qbpmyplus","BL22I-DI-PHDGN-07:Y:PLUS:I","V","%.4e")
#qbpmyminus = DisplayEpicsPVClass("qbpmyminus","BL22I-DI-PHDGN-07:Y:MINUS:I","V","%.4e")
#qbpmxplus = DisplayEpicsPVClass("qbpmxplus","BL22I-DI-PHDGN-07:X:PLUS:I","V","%.4e")
#qbpmxminus = DisplayEpicsPVClass("qbpmxminus","BL22I-DI-PHDGN-07:X:MINUS:I","V","%.4e")

