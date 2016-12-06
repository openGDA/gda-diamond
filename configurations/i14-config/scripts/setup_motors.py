run('/dls_sw/i14/scripts/Beamline/dcm_enrg.py')
run('/dls_sw/i14/scripts/Beamline/EpicsScannable.py')

# DCM (now in GDA config)
#createPVScannable('dcm_pitch','BL14I-OP-DCM-01:PITCH.VAL')
#createPVScannable('dcm_roll','BL14I-OP-DCM-01:ROLL.VAL')
#createPVScannable('dcm_perp','BL14I-OP-DCM-01:GAP.VAL')
#createPVScannable('dcm_bragg','BL14I-OP-DCM-01:BRAGG.VAL')

# Slits (now in GDA config)
#createPVScannable('s1x_centre','BL14I-AL-SLITS-01:X:CENTER.VAL')
#createPVScannable('s1y_centre','BL14I-AL-SLITS-01:Y:CENTER.VAL')

# Diagnostics (now in GDA config)
#createPVScannable('d3','BL14I-DI-PHDGN-03:X.VAL')
#createPVScannable('d4_y','BL14I-DI-PHDGN-04:Y.VAL')
#createPVScannable('d4_x','BL14I-DI-PHDGN-04:X.VAL')

# Mirror 1 (now in GDA config)
#createPVScannable('m1_x','BL14I-OP-MIRR-01:X.VAL')
#createPVScannable('m1_y','BL14I-OP-MIRR-01:Y.VAL')
#createPVScannable('m1_pitch', 'BL14I-OP-MIRR-01:PITCH.VAL')

# Mirror 2 (now in GDA config)
#createPVScannable('m2_x','BL14I-OP-MIRR-02:X.VAL')
#createPVScannable('m2_y','BL14I-OP-MIRR-02:Y.VAL')
#createPVScannable('m2_pitch', 'BL14I-OP- MIRR-02:PITCH.VAL')
#createPVScannable('m2_roll', 'BL14I-OP-MIRR-02:ROLL.VAL')

# ID _gap (now in GDA config)
#createPVScannable('id_gap','SR14I-MO-SERVC-01:BLGAPMTR.VAL')

# Detectors (now in GDA config)
#d4_diode1=EPICSMonitor('d4_diode1','BL14I-DI-PHDGN-04:FEMTO1:I','uA','%5.5g')
#d4_diode2=EPICSMonitor('d4_diode2','BL14I-DI-PHDGN-04:FEMTO2:I','uA','%5.5g')
#d3_diode1=EPICSMonitor('d3_diode1','BL14I-DI-PHDGN-03:FEMTO1:I','uA','%5.5g')

# A dummy detectors for pausing after steps
#mypause=DummyDetector("mypause","s","%4.4f")

# Combo scannable to move bragg and perp
dcm_enrg = DCMpdq("dcm_enrg")

# EXAFS scannable to record log(i0/it) from d4_diode2 and d3_diode1
exafs_d4_scatter  =ExafsDetector("exafs_inline",d3_diode1,d4_diode1)
# EXAFS scannable to record log(i0/it) from d4_diode1 and d3_diode1
exafs_d4_inline  =ExafsDetector("exafs_scatter",d3_diode1,d4_diode2)

#exafs_d4_adc_inline  =ExafsDetector("exafs_scatter",d3_adc_scatter,d4_adc_inline)

createPVMonitor("d1_diode", 'BL14I-DI-PHDGN-01:FEMTO1:I')
createPVMonitor("d2_diode", 'BL14I-DI-PHDGN-02:FEMTO1:I')
createPVMonitor("d5_diode1", 'BL14I-DI-PHDGN-05:FEMTO1:I')
createPVMonitor("d5_diode2", 'BL14I-DI-PHDGN-05:FEMTO2:I')
createPVMonitor("d5_adc",'BL14I-DI-PHDGN-05:FEMTO2:ADC2_VALUE')
createPVMonitor("d4_adc_inline",'BL14I-DI-PHDGN-04:FEMTO2:ADC2_VALUE')
createPVMonitor("d3_adc_scatter",'BL14I-DI-PHDGN-03:FEMTO1:ADC1_VALUE')

createPVMotor("s3_x",'BL14I-AL-SLITS-03:X:CENTER')
createPVMotor("s3_xgap",'BL14I-AL-SLITS-03:X:SIZE')
createPVMotor("s3_y",'BL14I-AL-SLITS-03:Y:CENTER')
createPVMotor("s3_ygap",'BL14I-AL-SLITS-03:Y:SIZE')
createPVMotor("s2_x",'BL14I-AL-SLITS-02:CENTER')
createPVMotor("s2_xgap",'BL14I-AL-SLITS-02:SIZE')