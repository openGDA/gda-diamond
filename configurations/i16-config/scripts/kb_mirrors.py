
kb_string='BL16I-MO-KBM-01:'

kb1t1=SingleEpicsPositionerClass('kb1_T1',kb_string+'T1.VAL',kb_string+'T1.RBV',kb_string+'T1.DMOV',kb_string+'T1.STOP' ,'mm','%f',command=None)
kb1t2=SingleEpicsPositionerClass('kb1_T2',kb_string+'T2.VAL',kb_string+'T2.RBV',kb_string+'T2.DMOV',kb_string+'T2.STOP' ,'mm','%f',command=None)
kb1trans=SingleEpicsPositionerClass('kb1_trans',kb_string+'T3.VAL',kb_string+'T3.RBV',kb_string+'T3.DMOV',kb_string+'T3.STOP' ,'mm','%f',command=None)
kb2trans=SingleEpicsPositionerClass('kb2_trans',kb_string+'T4.VAL',kb_string+'T4.RBV',kb_string+'T4.DMOV',kb_string+'T4.STOP' ,'mm','%f',command=None)
kb2t5=SingleEpicsPositionerClass('kb2_T5',kb_string+'T5.VAL',kb_string+'T5.RBV',kb_string+'T5.DMOV',kb_string+'T5.STOP' ,'mm','%f',command=None)
kb2t6=SingleEpicsPositionerClass('kb2_T6',kb_string+'T6.VAL',kb_string+'T6.RBV',kb_string+'T6.DMOV',kb_string+'T6.STOP' ,'mm','%f',command=None)
kb1roll=SingleEpicsPositionerClass('kb1_roll',kb_string+'ROLL1.VAL',kb_string+'ROLL1.RBV',kb_string+'ROLL1.DMOV',kb_string+'ROLL1.STOP' ,'mm','%f',command=None)
kb2roll=SingleEpicsPositionerClass('kb2_roll',kb_string+'ROLL2.VAL',kb_string+'ROLL2.RBV',kb_string+'ROLL2.DMOV',kb_string+'ROLL2.STOP' ,'mm','%f',command=None)
