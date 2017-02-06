peSetPath(path="x:\\2017\\ee15677-1\\")

#temps = [30,189.5,387.3,604.0,839.5] #Empty capillary
#temps = [30] #Empty XPDF
#temps = [30,53.4,97.6,142.9,189.5,237.2,286.0,336.1,387.3,439.7,493.3,548.1,604.0,661.1,719.4,778.9,839.5,901.3] #Sample
temps = [20] #Si standard

def collectEE15677(sampleFileName,exposure=300):
    spinOn
    blowerIn
    for i,t in enumerate(temps):
        setBlowerTemp(t,rate=5)
        waitForTol("BL15J-EA-BLOW-01:PV:RBV",t,tol=1,checkTime=5,timeOut=6000)
        print "Tolerance met. Waiting for 120 seconds"
        if i != 0:
            sleep(120)
        tempname = "dark_"+sampleFileName+str(i+1)+"_"+str(exposure)+"s"+"_t_"+str(blowerT.getPosition())+"C"
        detCollectDark(tempname,120)
        tempname = sampleFileName+"_"+str(i+1)+"_"+str(exposure)+"s"+"_t_"+str(blowerT.getPosition())+"C"
        detCollectSample(tempname,300)
    print "data collections complete..."
    setBlowerTemp(20,rate=5)
    blowerOut
    print "cooling down the blower... DON'T TOUCH IT UNTIL IT IS COOL!"
    waitForTol("BL15J-EA-BLOW-01:PV:RBV",50.,tol=40.,checkTime=5,timeOut=6000)
    spinOff
    print "collectEE15677 complete! You may now change your sample"

print "ee15677-1 script loaded"

#DATA COLLECTIONS PERFORMED
#collectEE15677(sampleFileName="quartz_cap_1mmOD",exposure=300)
#collectEE15677('Empty_XPDF')
#collectEE15677('MSC018_La10Ge6O27')