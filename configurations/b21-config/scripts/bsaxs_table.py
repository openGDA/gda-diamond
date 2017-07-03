#script to add biosaxs table

biotable_y=SingleEpicsPositionerClass('biotable_y', 'BL21B-MO-TABLE-04:Y.VAL' , 'BL21B-MO-TABLE-04:Y.RBV' , 'BL21B-MO-TABLE-04:Y.DMOV' , 'BL21B-MO-TABLE-04:Y.STOP' , 'mm', '%.5f')
biotable_x=SingleEpicsPositionerClass('biotable_x', 'BL21B-MO-TABLE-04:X.VAL' , 'BL21B-MO-TABLE-04:X.RBV' , 'BL21B-MO-TABLE-04:X.DMOV' , 'BL21B-MO-TABLE-04:X.STOP' , 'mm', '%.5f')

bs_x=SingleEpicsPositionerClass('bs_x', 'BL21B-RS-ABSB-03:X.VAL' , 'BL21B-RS-ABSB-03:X.RBV' , 'BL21B-RS-ABSB-03:X.DMOV' , 'BL21B-RS-ABSB-03:X.STOP' , 'mm', '%.5f')
bs_y=SingleEpicsPositionerClass('bs_y', 'BL21B-RS-ABSB-03:Y.VAL' , 'BL21B-RS-ABSB-03:Y.RBV' , 'BL21B-RS-ABSB-03:Y.DMOV' , 'BL21B-RS-ABSB-03:Y.STOP' , 'mm', '%.5f')


t3_y=SingleEpicsPositionerClass('t3_y', 'BL21B-MO-TABLE-03:Y.VAL' , 'BL21B-MO-TABLE-03:Y.RBV' , 'BL21B-MO-TABLE-03:Y.DMOV' , 'BL21B-MO-TABLE-03:Y.STOP' , 'mm', '%.5f')
t3_x=SingleEpicsPositionerClass('t3_x', 'BL21B-MO-TABLE-03:X.VAL' , 'BL21B-MO-TABLE-03:X.RBV' , 'BL21B-MO-TABLE-03:X.DMOV' , 'BL21B-MO-TABLE-03:X.STOP' , 'mm', '%.5f')


#scan dcm_pitch -4.0 -3.65 0.001 d3d2