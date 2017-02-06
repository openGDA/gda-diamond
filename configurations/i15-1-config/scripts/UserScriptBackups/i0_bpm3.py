#i0 = DisplayEpicsPVClass("i0", "BL15J-EA-CALC-03.I", "arb", "%f")

def i0Reset():
    caput("BL15J-EA-CALC-03.DESC","i0 BPM3 XBPM")
    caput("BL15J-EA-CALC-03.SCAN","9")
    
    caput("BL15J-EA-CALC-03.INPA","BL15J-DI-QBPM-03:A")
    caput("BL15J-EA-CALC-03.CMTA","XBPM ChA")
    caput("BL15J-EA-CALC-03.INPB","BL15J-DI-QBPM-03:B")
    caput("BL15J-EA-CALC-03.CMTB","XBPM ChB")
    caput("BL15J-EA-CALC-03.INPC","BL15J-DI-QBPM-03:C")
    caput("BL15J-EA-CALC-03.CMTC","XBPM ChC")
    caput("BL15J-EA-CALC-03.INPD","BL15J-DI-QBPM-03:D")
    caput("BL15J-EA-CALC-03.CMTD","XBPM ChD")
    
    caput("BL15J-EA-CALC-03.CLCE","0.338")
    caput("BL15J-EA-CALC-03.CMTE","X calibration constant")
    caput("BL15J-EA-CALC-03.CLCF","0.338")
    caput("BL15J-EA-CALC-03.CMTF","Y calibration constant")
    
    caput("BL15J-EA-CALC-03.CLCG","P*E*((A+B)-(C+D))/I")
    caput("BL15J-EA-CALC-03.CMTG","X position")
    caput("BL15J-EA-CALC-03.CLCH","P*F*((B+C)-(A+D))/I")
    caput("BL15J-EA-CALC-03.CMTH","Y position")
    caput("BL15J-EA-CALC-03.CLCI","A+B+C+D")
    
    caput("BL15J-EA-CALC-03.CLCO","1.0")
    caput("BL15J-EA-CALC-03.CMTO","Feedback threshold")
    caput("BL15J-EA-CALC-03.CLCP","I>O")
    caput("BL15J-EA-CALC-03.CMTP","Feedback on")
    
alias i0Reset



def bpm3CollectCalibration(sleepTime):
    voltages = dnp.arange(-1,9.5,0.5)
    print str(sleepTime)+" s settling time..."
    for v in voltages:
        caput("BL15J-OP-LAUE-01:PIEZO:CONTROL",v)
        sleep(sleepTime)
        monV = caget("BL15J-OP-LAUE-01:PIEZO:MONITOR")
        actV = caget("BL15J-OP-LAUE-01:PITCH:FINE:VOL:RD")
        pizPos = caget("BL15J-OP-LAUE-01:PITCH:FINE:POS:RD")
        bpm2posX = caget("BL15J-DI-BPM-02:PY:Double1_RBV")
        bpm3posX = caget("BL15J-EA-CALC-03.G")
        print "v "+str(v)+" monV "+monV+" actV "+actV+" pizPos "+pizPos+" bpm2posX "+bpm2posX+" bpm3posX "+bpm3posX
    print "...done!"
        


print "i0 (bpm3) scripts loaded"