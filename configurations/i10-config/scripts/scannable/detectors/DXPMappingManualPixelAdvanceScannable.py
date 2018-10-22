from gda.device.scannable import DummyScannable
from gda.epics import CAClient 

class ManualPixelAdvance(DummyScannable):
    
    def __init__(self, name, pv='ME13C-EA-DET-01:',formatstring='%6f'):
        self.setName(name)
#         self.setInputNames([])
#         self.setOutputFormat([])
        self.nextCh=CAClient(pv+'NextPixel')
        self.rt=CAClient(pv+'PresetReal')
        self.checkbusy=CAClient(pv+'ElapsedReal')
       
    def atScanStart(self):
        if not self.nextCh.isConfigured():
            self.nextCh.configure()
        if not self.rt.isConfigured():
            self.rt.configure()
        if not self.checkbusy.isConfigured():
            self.checkbusy.configure()
            
    def atScanEnd(self):
        if self.nextCh.isConfigured():
            self.nextCh.clearup()
        if self.rt.isConfigured():
            self.rt.clearup()
        if self.checkbusy.isConfigured():
            self.checkbusy.clearup()
           
    def isBusy(self):
        while self.checkbusy.caget()<self.rt.caget():
        try:
            if not self.nextCh.isConfigured():
                self.nextCh.configure()
                self.nextCh.caput(1)
                self.nextCh.clearup()
            else:
                self.nextCh.caput(1)
        except:
            print "error occurred when advance to next point"
    
    def atPointEnd(self):
        pass
#         try:
#             if not self.nextCh.isConfigured():
#                 self.nextCh.configure()
#                 self.nextCh.caput(1)
#                 self.nextCh.clearup()
#             else:
#                 self.nextCh.caput(1)
#         except:
#             print "error occurred when advance to next point"
    
#     def getPosition(self):
#         pass
#     
#     def asynchronousMoveTo(self, new_pos):
#         pass
#     
#     def isBusy(self):
#         return False
#     
#     def toFormattedString(self):
#         return ""
    
next=ManualPixelAdvance("next", "ME13C-EA-DET-01:NextPixel") 
