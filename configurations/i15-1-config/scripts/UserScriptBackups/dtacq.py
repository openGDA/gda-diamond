def dtacqReset():
    pvstem = "BL15J-EA-ADC-01:"
    
    #adc tab
    caput(pvstem+"ADC:DataType","0") #Int16
    caput(pvstem+"ADC:RANGE","0") #+-10V
    caput(pvstem+"ADC:ImageMode","2") #Continuous
    caput(pvstem+"ADC:TriggerMode","0") #Internal
    
    #trig
    caput(pvstem+"TRIG:EnableCallbacks","0")

    #roi
    for i in range(16):
        caput(pvstem+"ROI"+str(i)+":NDArrayPort","dtacq.adc")
        caput(pvstem+"ROI"+str(i)+":EnableCallbacks","1")
        caput(pvstem+"ROI"+str(i)+":MinCallbackTime","0")
        caput(pvstem+"ROI"+str(i)+":BlockingCallbacks","0")
        caput(pvstem+"ROI"+str(i)+":DataTypeOut","8") #Automatic
        caput(pvstem+"ROI"+str(i)+":EnableScale","0")
        caput(pvstem+"ROI"+str(i)+":EnableX","1")
        caput(pvstem+"ROI"+str(i)+":EnableY","0")
        caput(pvstem+"ROI"+str(i)+":EnableZ","0")
        caput(pvstem+"ROI"+str(i)+":BinX","1")
        caput(pvstem+"ROI"+str(i)+":MinX",i)
        caput(pvstem+"ROI"+str(i)+":SizeX",1)
        caput(pvstem+"ROI"+str(i)+":ReverseX","0")

    #stat
    for i in range(16):
        if i == 0:
            caput(pvstem+"STAT"+str(i)+":NDArrayPort","dtacq.roi0")
        else:
            caput(pvstem+"STAT"+str(i)+":NDArrayPort","dtacq.roi."+str(i))
        caput(pvstem+"STAT"+str(i)+":EnableCallbacks","1")
        caput(pvstem+"STAT"+str(i)+":MinCallbackTime","0")
        caput(pvstem+"STAT"+str(i)+":BlockingCallbacks","0")
        caput(pvstem+"STAT"+str(i)+":ComputeStatistics","1") #Turn on stats
        caput(pvstem+"STAT"+str(i)+":ComputeCentroid","0")
        caput(pvstem+"STAT"+str(i)+":ComputeHistogram","0")
        caput(pvstem+"STAT"+str(i)+":ComputeProfiles","0")
    
    #hdf
    #path is on the linux system, i.e. /dls/i15-1/data/2016/......
    caput(pvstem+"HDF:EnableCallbacks","0") #Make sure we don't accidentally fill the file system

    caput("BL15J-EA-ADC-01:ADC:Acquire","1") #Turn on acquisition
    print "dtacq reset complete"
alias dtacqReset

def dtacqSetTime(time="0.1"): #Frame time in seconds
    setSamples = 1000000*float(time)
    if setSamples > 1000000:
        print "Maximum frame time is 1 s; setting to 1 s"
    if setSamples < 10000:
        print "You probably won't get sensible data beyond 0.01 s; setting to 0.01 s"
        setSamples = 10000
    caput("BL15J-EA-ADC-01:ADC:SizeY",setSamples)
    caput("BL15J-EA-ADC-01:ADC:Acquire","1") #Turn on acquisition

def dtacqSetFreq(freq="10"): #Frame rate in Hz
    setSamples = 1000000/float(freq)
    if setSamples > 1000000:
        print "Minimum read-out frequency is 1 Hz; setting to 1 Hz"
    if setSamples < 10000:
        print "You probably won't get sensible data beyond 100 Hz; setting to 100 Hz"
        setSamples = 10000
    caput("BL15J-EA-ADC-01:ADC:SizeY",setSamples)
    caput("BL15J-EA-ADC-01:ADC:Acquire","1") #Turn on acquisition

print "dtacq scripts loaded"