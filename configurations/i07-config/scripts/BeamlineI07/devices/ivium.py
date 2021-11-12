from time import sleep
from datetime import datetime

class EChem(object):
    """A potentiostat class for the Ivium n-Stat."""
    def __init__(self,pvStem,nChannels=1):
        self.pvStem = pvStem
        self.nChannels = nChannels
        
#         self.eChemMethodCh1_t = DisplayEpicsPVClass("eChemMethodCh1_t", "BL15J-EA-IVIUM-01:CHAN1:LastCollectionX_RBV", "s", "%E")
#         self.eChemMethodCh1_V = DisplayEpicsPVClass("eChemMethodCh1_V", "BL15J-EA-IVIUM-01:CHAN1:LastCollectionZ_RBV", "V", "%E")
#         self.eChemMethodCh1_I = DisplayEpicsPVClass("eChemMethodCh1_I", "BL15J-EA-IVIUM-01:CHAN1:LastCollectionY_RBV", "A", "%E")
#         self.eChemMethodCh2_t = DisplayEpicsPVClass("eChemMethodCh2_t", "BL15J-EA-IVIUM-01:CHAN2:LastCollectionX_RBV", "s", "%E")
#         self.eChemMethodCh2_V = DisplayEpicsPVClass("eChemMethodCh2_V", "BL15J-EA-IVIUM-01:CHAN2:LastCollectionZ_RBV", "V", "%E")
#         self.eChemMethodCh2_I = DisplayEpicsPVClass("eChemMethodCh2_I", "BL15J-EA-IVIUM-01:CHAN2:LastCollectionY_RBV", "A", "%E")
#         self.eChemMethodCh3_t = DisplayEpicsPVClass("eChemMethodCh3_t", "BL15J-EA-IVIUM-01:CHAN3:LastCollectionX_RBV", "s", "%E")
#         self.eChemMethodCh3_V = DisplayEpicsPVClass("eChemMethodCh3_V", "BL15J-EA-IVIUM-01:CHAN3:LastCollectionZ_RBV", "V", "%E")
#         self.eChemMethodCh3_I = DisplayEpicsPVClass("eChemMethodCh3_I", "BL15J-EA-IVIUM-01:CHAN3:LastCollectionY_RBV", "A", "%E")
#         self.eChemMethodCh4_t = DisplayEpicsPVClass("eChemMethodCh4_t", "BL15J-EA-IVIUM-01:CHAN4:LastCollectionX_RBV", "s", "%E")
#         self.eChemMethodCh4_V = DisplayEpicsPVClass("eChemMethodCh4_V", "BL15J-EA-IVIUM-01:CHAN4:LastCollectionZ_RBV", "V", "%E")
#         self.eChemMethodCh4_I = DisplayEpicsPVClass("eChemMethodCh4_I", "BL15J-EA-IVIUM-01:CHAN4:LastCollectionY_RBV", "A", "%E")
#         self.eChemMethodCh5_t = DisplayEpicsPVClass("eChemMethodCh5_t", "BL15J-EA-IVIUM-01:CHAN5:LastCollectionX_RBV", "s", "%E")
#         self.eChemMethodCh5_V = DisplayEpicsPVClass("eChemMethodCh5_V", "BL15J-EA-IVIUM-01:CHAN5:LastCollectionZ_RBV", "V", "%E")
#         self.eChemMethodCh5_I = DisplayEpicsPVClass("eChemMethodCh5_I", "BL15J-EA-IVIUM-01:CHAN5:LastCollectionY_RBV", "A", "%E")
#         self.eChemMethodCh6_t = DisplayEpicsPVClass("eChemMethodCh6_t", "BL15J-EA-IVIUM-01:CHAN6:LastCollectionX_RBV", "s", "%E")
#         self.eChemMethodCh6_V = DisplayEpicsPVClass("eChemMethodCh6_V", "BL15J-EA-IVIUM-01:CHAN6:LastCollectionZ_RBV", "V", "%E")
#         self.eChemMethodCh6_I = DisplayEpicsPVClass("eChemMethodCh6_I", "BL15J-EA-IVIUM-01:CHAN6:LastCollectionY_RBV", "A", "%E")
#         self.eChemMethodCh7_t = DisplayEpicsPVClass("eChemMethodCh7_t", "BL15J-EA-IVIUM-01:CHAN7:LastCollectionX_RBV", "s", "%E")
#         self.eChemMethodCh7_V = DisplayEpicsPVClass("eChemMethodCh7_V", "BL15J-EA-IVIUM-01:CHAN7:LastCollectionZ_RBV", "V", "%E")
#         self.eChemMethodCh7_I = DisplayEpicsPVClass("eChemMethodCh7_I", "BL15J-EA-IVIUM-01:CHAN7:LastCollectionY_RBV", "A", "%E")
#         self.eChemMethodCh8_t = DisplayEpicsPVClass("eChemMethodCh8_t", "BL15J-EA-IVIUM-01:CHAN8:LastCollectionX_RBV", "s", "%E")
#         self.eChemMethodCh8_V = DisplayEpicsPVClass("eChemMethodCh8_V", "BL15J-EA-IVIUM-01:CHAN8:LastCollectionZ_RBV", "V", "%E")
#         self.eChemMethodCh8_I = DisplayEpicsPVClass("eChemMethodCh8_I", "BL15J-EA-IVIUM-01:CHAN8:LastCollectionY_RBV", "A", "%E")
#         
#         self.monitors = [self.eChemMethodCh1_t,self.eChemMethodCh1_V,self.eChemMethodCh1_I,
#                          self.eChemMethodCh2_t,self.eChemMethodCh2_V,self.eChemMethodCh2_I,
#                          self.eChemMethodCh3_t,self.eChemMethodCh3_V,self.eChemMethodCh3_I,
#                          self.eChemMethodCh4_t,self.eChemMethodCh4_V,self.eChemMethodCh4_I,
#                          self.eChemMethodCh5_t,self.eChemMethodCh5_V,self.eChemMethodCh5_I,
#                          self.eChemMethodCh6_t,self.eChemMethodCh6_V,self.eChemMethodCh6_I,
#                          self.eChemMethodCh7_t,self.eChemMethodCh7_V,self.eChemMethodCh7_I,
#                          self.eChemMethodCh8_t,self.eChemMethodCh8_V,self.eChemMethodCh8_I]
        
    def getChannelList(self,channels):
        if channels == []:
            channels = [1]
        elif type(channels) == type(1):
            channels = [channels]
        return channels
        
    def setMethodMode(self,channels=[]):
        channels = self.getChannelList(channels)
        for i in channels:
            #caput(self.pvStem+"CHAN"+str(i)+":AssignedPort","Ports.P"+str(i))
            caput(self.pvStem+"PORT"+str(i)+":OperatingMode",1) #Method
            caput(self.pvStem+"PORT"+str(i)+":ImageMode",1) #Multiple
            #caput(self.pvStem+"HDF"+str(i)+":NDArrayPort","Ports.P"+str(i))
            caputS(self.pvStem+"HDF"+":FileTemplate","%s%s.hdf")
            sleep(0.1)
            caput(self.pvStem+"HDF"+":EnableCallbacks",1)
            caput(self.pvStem+"HDF"+":FileWriteMode",2)
            caput(self.pvStem+"HDF"+":LazyOpen",1)
            
    def setDirectMode(self,channels=[]):
        channels = self.getChannelList(channels)
        for i in channels:
            #caput(self.pvStem+"CHAN"+str(i)+":AssignedPort","Ports.P"+str(i))
            caput(self.pvStem+"PORT"+str(i)+":OperatingMode",0) #Direct
            caput(self.pvStem+"PORT"+str(i)+":ImageMode",2) #Continuous
            #caput(self.pvStem+"HDF"+str(i)+":NDArrayPort","Ports.P"+str(i))
            caputS(self.pvStem+"HDF"+":FileTemplate","%s%s.hdf")
            sleep(0.1)
            caput(self.pvStem+"HDF"+":EnableCallbacks",1)
            caput(self.pvStem+"HDF"+":FileWriteMode",2)
            caput(self.pvStem+"HDF"+":LazyOpen",1)
            
    def setMethodPath(self,path="/IviumStat/datafiles/",channels=[]):
        channels = self.getChannelList(channels)
        for i in channels:
            caputS(self.pvStem+"PORT"+str(i)+":MethodDirectory",path)
            
    def setMethodFilename(self,filename,channels=[]):
        """Takes the filename of the method to run (with or without the .imf extension)"""
        channels = self.getChannelList(channels)
        if filename[-4:] != ".imf":
            filename = filename+".imf"
        for i in channels:
            caputS(self.pvStem+"PORT"+str(i)+":MethodFileName",filename)
    
    def setHdfPath(self,path=None,channels=[]):
        """Sets the file path for the HDF file containing the eChem data.
        
        Defaults to the current visit directory /processed/eChem"""
        if path == None:
            path = InterfaceProvider.getPathConstructor().getVisitDirectory() + "/ivium/"
            if not os.path.exists(path): os.makedirs(path)
        channels = self.getChannelList(channels)
        for i in channels:
            caputS(self.pvStem+"HDF"+":FilePath",path)
            
    def setHdfFilename(self,filename,channels=[]):
        """Sets the filename for the HDF file containing the eChem data.
        
        Automatically appends the channel number to the name given"""
        channels = self.getChannelList(channels)
        for i in channels:
            caputS(self.pvStem+"HDF"+":FileName",filename+"_ch{}".format(i))
    
    def primeHdfWriter(self,channels=[]):
        channels = self.getChannelList(channels)
        for i in channels:
            caput(self.pvStem+"HDF"+":Capture",1)
            _waitFor(self.pvStem+"HDF:Capture_RBV",1,checkTime=.1,timeOut=5)
    
    def startMethod(self,channels=[]):
        channels = self.getChannelList(channels)
        for i in channels:
            caput(self.pvStem+"PORT"+str(i)+":Acquire",1)
            
    def stopMethod(self,channels=[]):
        channels = self.getChannelList(channels)
        for i in channels:
            caput(self.pvStem+"PORT"+str(i)+":Acquire",0)
            caput(self.pvStem+"HDF"+":Capture",0)
        
    def runMethod(self,methodFilePath,channel):
        self.setMethodMode(channel)
        filename = os.path.basename(methodFilePath)
        filepath = os.path.dirname(methodFilePath)+"/"
        if filename[-4:] != ".imf":
            filename = filename+".imf"
        self.setMethodPath(filepath,channel)
        self.setMethodFilename(filename,channel)
        self.setHdfPath(channels=channel)
        hdfFileName = filename[:-4]
        hdfFileName = hdfFileName+"_"+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.setHdfFilename(hdfFileName,channel)
        self.primeHdfWriter(channel)
        self.startMethod(channel)
        print "eChem method {} started on channel {} at ".format(filename,channel)
        
    def setDirectCurrent(self,channel,current):
        self.setDirectMode()
        sleep(0.1)
        # Don't need to stop anymore
        #caput(self.pvStem+"PORT"+str(channel)+":Acquire",0)
        #sleep(0.1)
        caput(self.pvStem+"PORT"+str(channel)+":CellConnection",3)
        sleep(0.1)
        caput(self.pvStem+"PORT"+str(channel)+":AppliedCurrent",current)
        caput(self.pvStem+"PORT"+str(channel)+":Acquire",1)
        caput(self.pvStem+"PORT"+str(channel)+":Apply",1)
        
    def setDirectVoltage(self,channel,voltage):
        self.setDirectMode()
        sleep(0.1)
        # Don't need to stop anymore
        #caput(self.pvStem+"PORT"+str(channel)+":Acquire",0)
        #sleep(0.1)
        caput(self.pvStem+"PORT"+str(channel)+":CellConnection",1)
        sleep(0.1)
        caput(self.pvStem+"PORT"+str(channel)+":AppliedPotential",voltage)
        caput(self.pvStem+"PORT"+str(channel)+":Acquire",1)
        caput(self.pvStem+"PORT"+str(channel)+":Apply",1)
        
eChem = EChem(pvStem="BL07I-EA-IVIUM-01:")
        

class EChemPvManager():
    def __init__(self,pvStem):
        self.pvStem = pvStem
        topPvList = ["CollectionSize_RBV","LastCollectionX_RBV","LastCollectionY_RBV","LastCollectionZ_RBV"]
        pvDict = {pv : pv for pv in topPvList}
        for i in range(1,9):
            setattr(self,"chan%s" % i,XpdfPvManager(pvDict,'%sCHAN%s:' % (pvStem,i),pvKeysToMonitor=[]))
        chanPvList = ["OperatingMode_RBV","MeasuredPotential_RBV","MeasuredCurrent_RBV","AppliedCurrent_RBV","AppliedPotential_RBV","CellConnection_RBV"]
        pvDict = {pv : pv for pv in chanPvList}
        for i in range(1,9):
            setattr(self,"chan%s" % i,XpdfPvManager(pvDict,'%sCHAN%s:' % (pvStem,i),pvKeysToMonitor=[]))
        portPvList = ["Acquire","OperatingMode","CellConnection","NumSamples","NumSamples_RBV","SamplePeriod","SamplePeriod_RBV","AppliedPotential","AppliedPotential_RBV","AppliedCurrent","AppliedCurrent_RBV","MethodDirectory","MethodFileName"]
        pvDict = {pv : pv for pv in portPvList}
        for i in range(1,9):
            setattr(self,"port%s" % i,XpdfPvManager(pvDict,'%sPORT%s:' % (pvStem,i),pvKeysToMonitor=["Acquire"]))
        hdfPvList = ["NDArrayPort","Capture","Capture_RBV","EnableCallbacks","MinCallbackTime","MinCallbackTime_RBV","BlockingCallbacks","FilePath","FileName","FileTemplate","FileTemplate_RBV","FileWriteMode","AutoSave"]
        pvDict = {pv : pv for pv in hdfPvList}
        for i in range(1,9):
            setattr(self,"hdf%s" % i,XpdfPvManager(pvDict,'%sHDF%s:' % (pvStem,i),pvKeysToMonitor=["Capture"]))
        

        
#def createScannables():
# eChemMethodCh1_t = DisplayEpicsPVClass("eChemMethodCh1_t", "BL15J-EA-IVIUM-01:CHAN1:LastCollectionX_RBV", "s", "%E")
# eChemMethodCh1_V = DisplayEpicsPVClass("eChemMethodCh1_V", "BL15J-EA-IVIUM-01:CHAN1:LastCollectionZ_RBV", "V", "%E")
# eChemMethodCh1_I = DisplayEpicsPVClass("eChemMethodCh1_I", "BL15J-EA-IVIUM-01:CHAN1:LastCollectionY_RBV", "A", "%E")
# eChemMethodCh2_t = DisplayEpicsPVClass("eChemMethodCh2_t", "BL15J-EA-IVIUM-01:CHAN2:LastCollectionX_RBV", "s", "%E")
# eChemMethodCh2_V = DisplayEpicsPVClass("eChemMethodCh2_V", "BL15J-EA-IVIUM-01:CHAN2:LastCollectionZ_RBV", "V", "%E")
# eChemMethodCh2_I = DisplayEpicsPVClass("eChemMethodCh2_I", "BL15J-EA-IVIUM-01:CHAN2:LastCollectionY_RBV", "A", "%E")
# eChemMethodCh3_t = DisplayEpicsPVClass("eChemMethodCh3_t", "BL15J-EA-IVIUM-01:CHAN3:LastCollectionX_RBV", "s", "%E")
# eChemMethodCh3_V = DisplayEpicsPVClass("eChemMethodCh3_V", "BL15J-EA-IVIUM-01:CHAN3:LastCollectionZ_RBV", "V", "%E")
# eChemMethodCh3_I = DisplayEpicsPVClass("eChemMethodCh3_I", "BL15J-EA-IVIUM-01:CHAN3:LastCollectionY_RBV", "A", "%E")
# eChemMethodCh4_t = DisplayEpicsPVClass("eChemMethodCh4_t", "BL15J-EA-IVIUM-01:CHAN4:LastCollectionX_RBV", "s", "%E")
# eChemMethodCh4_V = DisplayEpicsPVClass("eChemMethodCh4_V", "BL15J-EA-IVIUM-01:CHAN4:LastCollectionZ_RBV", "V", "%E")
# eChemMethodCh4_I = DisplayEpicsPVClass("eChemMethodCh4_I", "BL15J-EA-IVIUM-01:CHAN4:LastCollectionY_RBV", "A", "%E")
# eChemMethodCh5_t = DisplayEpicsPVClass("eChemMethodCh5_t", "BL15J-EA-IVIUM-01:CHAN5:LastCollectionX_RBV", "s", "%E")
# eChemMethodCh5_V = DisplayEpicsPVClass("eChemMethodCh5_V", "BL15J-EA-IVIUM-01:CHAN5:LastCollectionZ_RBV", "V", "%E")
# eChemMethodCh5_I = DisplayEpicsPVClass("eChemMethodCh5_I", "BL15J-EA-IVIUM-01:CHAN5:LastCollectionY_RBV", "A", "%E")
# eChemMethodCh6_t = DisplayEpicsPVClass("eChemMethodCh6_t", "BL15J-EA-IVIUM-01:CHAN6:LastCollectionX_RBV", "s", "%E")
# eChemMethodCh6_V = DisplayEpicsPVClass("eChemMethodCh6_V", "BL15J-EA-IVIUM-01:CHAN6:LastCollectionZ_RBV", "V", "%E")
# eChemMethodCh6_I = DisplayEpicsPVClass("eChemMethodCh6_I", "BL15J-EA-IVIUM-01:CHAN6:LastCollectionY_RBV", "A", "%E")
# eChemMethodCh7_t = DisplayEpicsPVClass("eChemMethodCh7_t", "BL15J-EA-IVIUM-01:CHAN7:LastCollectionX_RBV", "s", "%E")
# eChemMethodCh7_V = DisplayEpicsPVClass("eChemMethodCh7_V", "BL15J-EA-IVIUM-01:CHAN7:LastCollectionZ_RBV", "V", "%E")
# eChemMethodCh7_I = DisplayEpicsPVClass("eChemMethodCh7_I", "BL15J-EA-IVIUM-01:CHAN7:LastCollectionY_RBV", "A", "%E")
# eChemMethodCh8_t = DisplayEpicsPVClass("eChemMethodCh8_t", "BL15J-EA-IVIUM-01:CHAN8:LastCollectionX_RBV", "s", "%E")
# eChemMethodCh8_V = DisplayEpicsPVClass("eChemMethodCh8_V", "BL15J-EA-IVIUM-01:CHAN8:LastCollectionZ_RBV", "V", "%E")
# eChemMethodCh8_I = DisplayEpicsPVClass("eChemMethodCh8_I", "BL15J-EA-IVIUM-01:CHAN8:LastCollectionY_RBV", "A", "%E")
#     eChemDirectCh1_MeasuredV = DisplayEpicsPVClass("eChemDirectCh1_MeasuredV", "BL15J-EA-IVIUM-01:CHAN1:MeasuredPotential_RBV", "V", "%E")
#     eChemDirectCh1_AppliedV  = DisplayEpicsPVClass("eChemDirectCh1_AppliedV" , "BL15J-EA-IVIUM-01:CHAN1:AppliedPotential_RBV" , "V", "%E")
#     eChemDirectCh1_MeasuredI = DisplayEpicsPVClass("eChemDirectCh1_MeasuredI", "BL15J-EA-IVIUM-01:CHAN1:MeasuredCurrent_RBV"  , "A", "%E")
#     eChemDirectCh1_AppliedI  = DisplayEpicsPVClass("eChemDirectCh1_AppliedI" , "BL15J-EA-IVIUM-01:CHAN1:AppliedCurrent_RBV"   , "A", "%E")
#     eChemDirectCh2_MeasuredV = DisplayEpicsPVClass("eChemDirectCh2_MeasuredV", "BL15J-EA-IVIUM-01:CHAN2:MeasuredPotential_RBV", "V", "%E")
#     eChemDirectCh2_AppliedV  = DisplayEpicsPVClass("eChemDirectCh2_AppliedV" , "BL15J-EA-IVIUM-01:CHAN2:AppliedPotential_RBV" , "V", "%E")
#     eChemDirectCh2_MeasuredI = DisplayEpicsPVClass("eChemDirectCh2_MeasuredI", "BL15J-EA-IVIUM-01:CHAN2:MeasuredCurrent_RBV"  , "A", "%E")
#     eChemDirectCh2_AppliedI  = DisplayEpicsPVClass("eChemDirectCh2_AppliedI" , "BL15J-EA-IVIUM-01:CHAN2:AppliedCurrent_RBV"   , "A", "%E")
#     eChemDirectCh3_MeasuredV = DisplayEpicsPVClass("eChemDirectCh3_MeasuredV", "BL15J-EA-IVIUM-01:CHAN3:MeasuredPotential_RBV", "V", "%E")
#     eChemDirectCh3_AppliedV  = DisplayEpicsPVClass("eChemDirectCh3_AppliedV" , "BL15J-EA-IVIUM-01:CHAN3:AppliedPotential_RBV" , "V", "%E")
#     eChemDirectCh3_MeasuredI = DisplayEpicsPVClass("eChemDirectCh3_MeasuredI", "BL15J-EA-IVIUM-01:CHAN3:MeasuredCurrent_RBV"  , "A", "%E")
#     eChemDirectCh3_AppliedI  = DisplayEpicsPVClass("eChemDirectCh3_AppliedI" , "BL15J-EA-IVIUM-01:CHAN3:AppliedCurrent_RBV"   , "A", "%E")
#     eChemDirectCh4_MeasuredV = DisplayEpicsPVClass("eChemDirectCh4_MeasuredV", "BL15J-EA-IVIUM-01:CHAN4:MeasuredPotential_RBV", "V", "%E")
#     eChemDirectCh4_AppliedV  = DisplayEpicsPVClass("eChemDirectCh4_AppliedV" , "BL15J-EA-IVIUM-01:CHAN4:AppliedPotential_RBV" , "V", "%E")
#     eChemDirectCh4_MeasuredI = DisplayEpicsPVClass("eChemDirectCh4_MeasuredI", "BL15J-EA-IVIUM-01:CHAN4:MeasuredCurrent_RBV"  , "A", "%E")
#     eChemDirectCh4_AppliedI  = DisplayEpicsPVClass("eChemDirectCh4_AppliedI" , "BL15J-EA-IVIUM-01:CHAN4:AppliedCurrent_RBV"   , "A", "%E")
#     eChemDirectCh5_MeasuredV = DisplayEpicsPVClass("eChemDirectCh5_MeasuredV", "BL15J-EA-IVIUM-01:CHAN5:MeasuredPotential_RBV", "V", "%E")
#     eChemDirectCh5_AppliedV  = DisplayEpicsPVClass("eChemDirectCh5_AppliedV" , "BL15J-EA-IVIUM-01:CHAN5:AppliedPotential_RBV" , "V", "%E")
#     eChemDirectCh5_MeasuredI = DisplayEpicsPVClass("eChemDirectCh5_MeasuredI", "BL15J-EA-IVIUM-01:CHAN5:MeasuredCurrent_RBV"  , "A", "%E")
#     eChemDirectCh5_AppliedI  = DisplayEpicsPVClass("eChemDirectCh5_AppliedI" , "BL15J-EA-IVIUM-01:CHAN5:AppliedCurrent_RBV"   , "A", "%E")
#     eChemDirectCh6_MeasuredV = DisplayEpicsPVClass("eChemDirectCh6_MeasuredV", "BL15J-EA-IVIUM-01:CHAN6:MeasuredPotential_RBV", "V", "%E")
#     eChemDirectCh6_AppliedV  = DisplayEpicsPVClass("eChemDirectCh6_AppliedV" , "BL15J-EA-IVIUM-01:CHAN6:AppliedPotential_RBV" , "V", "%E")
#     eChemDirectCh6_MeasuredI = DisplayEpicsPVClass("eChemDirectCh6_MeasuredI", "BL15J-EA-IVIUM-01:CHAN6:MeasuredCurrent_RBV"  , "A", "%E")
#     eChemDirectCh6_AppliedI  = DisplayEpicsPVClass("eChemDirectCh6_AppliedI" , "BL15J-EA-IVIUM-01:CHAN6:AppliedCurrent_RBV"   , "A", "%E")
#     eChemDirectCh7_MeasuredV = DisplayEpicsPVClass("eChemDirectCh7_MeasuredV", "BL15J-EA-IVIUM-01:CHAN7:MeasuredPotential_RBV", "V", "%E")
#     eChemDirectCh7_AppliedV  = DisplayEpicsPVClass("eChemDirectCh7_AppliedV" , "BL15J-EA-IVIUM-01:CHAN7:AppliedPotential_RBV" , "V", "%E")
#     eChemDirectCh7_MeasuredI = DisplayEpicsPVClass("eChemDirectCh7_MeasuredI", "BL15J-EA-IVIUM-01:CHAN7:MeasuredCurrent_RBV"  , "A", "%E")
#     eChemDirectCh7_AppliedI  = DisplayEpicsPVClass("eChemDirectCh7_AppliedI" , "BL15J-EA-IVIUM-01:CHAN7:AppliedCurrent_RBV"   , "A", "%E")
#     eChemDirectCh8_MeasuredV = DisplayEpicsPVClass("eChemDirectCh8_MeasuredV", "BL15J-EA-IVIUM-01:CHAN8:MeasuredPotential_RBV", "V", "%E")
#     eChemDirectCh8_AppliedV  = DisplayEpicsPVClass("eChemDirectCh8_AppliedV" , "BL15J-EA-IVIUM-01:CHAN8:AppliedPotential_RBV" , "V", "%E")
#     eChemDirectCh8_MeasuredI = DisplayEpicsPVClass("eChemDirectCh8_MeasuredI", "BL15J-EA-IVIUM-01:CHAN8:MeasuredCurrent_RBV"  , "A", "%E")
#     eChemDirectCh8_AppliedI  = DisplayEpicsPVClass("eChemDirectCh8_AppliedI" , "BL15J-EA-IVIUM-01:CHAN8:AppliedCurrent_RBV"   , "A", "%E")
# print "eChem scannables created"

    
def caputS(pv,string):
    ustring = map(ord,string+u"\u0000")
    caput(pv,ustring)
    
def _waitFor(pv,value,checkTime=0.5,timeOut=30,logger=None):
     i = 0
     timeOut = int(float(timeOut) / float(checkTime))
     sleep(float(checkTime))
     while str(caget(pv)) != str(value):
         sleep(float(checkTime))
         i += 1
         if i > timeOut:
             raise Exception("waitFor timed out while waiting for "+ str(pv) + " to change to " + str(value))
    
    
    #eChemMethodCh1_V,eChemMethodCh1_I, eChemMethodCh2_V, eChemMethodCh2_I, eChemMethodCh3_V, eChemMethodCh3_I, eChemMethodCh4_V, eChemMethodCh4_I, eChemMethodCh5_V, eChemMethodCh5_I, eChemMethodCh6_V, eChemMethodCh6_I, eChemMethodCh7_V, eChemMethodCh7_I, eChemMethodCh8_V, eChemMethodCh8_I    
    
    
"""
NOTES ON OPERATION IN DIRECT MODE
1. Changes to applied current/voltage are only taken into account when the PORT is Stopped and Started again
2. When Cell Mode is set to Potential or Current,  is the live Voltage reading and LastCollectionY_RBV is the live Current reading
"""
print "eChem scripts loaded"