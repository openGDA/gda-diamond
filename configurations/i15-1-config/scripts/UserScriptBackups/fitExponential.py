import scisoftpy as dnp

def negExp(p1,p2,xdata,*args):
    return p1*dnp.exp(-p2*xdata[0])

def runExponential():
    xdata = dnp.linspace(0,5,40)
    ydata = dnp.array([3.5733e+00, 2.1821e+00, 1.8313e+00, 1.9893+00, 8.3145e-01, 9.8761e-01])
    fr = dnp.fit.fit([negExp, dnp.fit.function.offset], xdata, ydata, [ 2.5, 1.2, 0.1], [(0,4), 0, (-0.2,0.7)])
    print fr
    fr.plot()
    
def monitorDet(setStable=0.01,countedStable=5):
    #pe1statMean = DisplayEpicsPVClass("pe1statMean", "BL15J-EA-DET-01:STAT:MeanValue_RBV", "counts", "%1.4f")
    zebraTime = float(caget("BL15J-EA-ZEBRA-01:DIV1_DIV"))
    acquireTime = zebraTime/1000. ##acquireTime in seconds
    detReady = False
    xdata = []
    ydata = []
    i = 0
    countStable = 0
    dnp.plot.setdefname('Detector stability')
    dnp.plot.clear()
    print "Waiting for stability"
    while detReady == False:
        sleep(acquireTime)
        xdata.append(float(i) * acquireTime)
        currentY = float(caget("BL15J-EA-DET-01:STAT:MeanValue_RBV"))
        ydata.append(currentY)
        #print "adding data "+str(pe1statMean)
        i = i+1
        if i > 5:
            fr = dnp.fit.fit([negExp, dnp.fit.function.offset], dnp.array(xdata), dnp.array(ydata), [ 3.0, 0.2, currentY], [(-4,4), 0, (currentY-currentY*10,currentY+currentY*10)])
            #fr.plot()
            #print(fr)
            plotdata = fr.makeplotdata()
            xdatas = dnp.array(xdata)
            dnp.plot.line(xdatas,plotdata[0])
            dnp.plot.addline(xdatas,plotdata[1])
            dnp.plot.addline(xdatas,plotdata[2])
            dnp.plot.addline(xdatas,plotdata[3])
            dnp.plot.addline(xdatas,plotdata[5])
            timeStable = dnp.log(setStable)/-fr[1]
            dnp.plot.addline(dnp.array([timeStable,timeStable]),dnp.array([plotdata[0].min(),plotdata[0].max()]))
            #print "Time stable "+str(timeStable)
            if xdatas.max() > timeStable:
                countStable = countStable + 1
                print "Stable for "+str(countStable)+" frames"
            else:
                countStable = 0
                print "Unstable; waiting for stability"
        if countStable > countedStable-1:
            detReady = True
            print "Detector is stable"
        if i > 30:
            detReady = True
            print "Timed out without reaching stability"
    print(str(xdata))
    print(str(ydata))

#def setBean(beanname):
#    db = dnp.plot.getd

print "fitExponential scripts loaded"