'''
Created on 21 Feb 2019

@author: fy65
'''
from gov.aps.jca.event import MonitorListener
from scannabledevices.pausableScannableWithListenerSupport import PauseableScannable
from gda.observable import IObserver
from org.slf4j import LoggerFactory
from gdaserver import armtth
from time import sleep

#I21 Laser Scanner listener
LASER_STATUS={0:'None', 1:'Blue', 2:'Yellow', 3:'Red'}
class LaserScannerMonitorListener(MonitorListener):
    
    def __init__(self, scannable=None):
        self.scannable=scannable
        self.newLaserStatus=0
        self.logger=LoggerFactory.getLogger("LaserScannerMonitorListener")
        self.lastLaserStatusUpdated=0
        
    def setScannable(self, s):
        self.scannable=s
        return self

    def monitorChanged(self, mevent):
        '''monitoring laser scanner status value, pause motor when receiving 'Yellow' signal,
        resume motion when receiving 'None' or Blue' signal, print a message to console when
        receiving 'Red' signal.
        '''
        self.newLaserStatus = int(mevent.getDBR().getEnumValue()[0])
        self.logger.debug("Laser Scanner Status is updated to {}", LASER_STATUS[self.newLaserStatus])
        if self.scannable is None:
            raise ValueError("scannable is not set!")
        if self.newLaserStatus != self.lastLaserStatusUpdated:
            if self.newLaserStatus == 2 or self.newLaserStatus == 3: #Yellow zone and Red zone
                print "Pause %s motion: Laser Scanner status is %s zone !" % (self.scannable.getName(), LASER_STATUS[self.newLaserStatus])
                self.scannable.pause()
            elif self.newLaserStatus == 1 or self.newLaserStatus == 0: #Blue zone or None zone
                print "Resume %s motion: Laser Scanner status is %s zone" % (self.scannable.getName(), LASER_STATUS[self.newLaserStatus])
                self.scannable.resume()
        self.lastLaserStatusUpdated=self.newLaserStatus

#I21 cinel-seal nitrogen flow listener          
FLOW_STATUS={0:'Off', 1:'On'}
class FlowStatusMonitorListener(MonitorListener):
    
    def __init__(self, scannable=None):
        self.scannable=scannable
        self.newFlowStatus=0
        self.logger=LoggerFactory.getLogger("FlowStatusMonitorListener")
        self.lastFlowStatusUpdated=0
    
    def setScannable(self, s):
        self.scannable=s
        return self
        
    def monitorChanged(self, mevent):
        '''monitoring laser scanner status value, pause motor when receiving 'Yellow' signal,
        resume motion when receiving 'None' or Blue' signal, print a message to console when
        receiving 'Red' signal.
        '''
        self.newFlowStatus = int(mevent.getDBR().getEnumValue()[0])
        self.logger.debug("Sliding Seal Nitrogen flow status is updated to {}", FLOW_STATUS[self.newFlowStatus])
        if self.scannable is None:
            raise ValueError("scannable is not set!")
        if self.newFlowStatus != self.lastFlowStatusUpdated:
            if self.newFlowStatus == 0: # flow too low
                print "Pause %s motion: Nitrogen flow status is %s !" % (self.scannable.getName(), FLOW_STATUS[self.newFlowStatus])
                self.scannable.pause()
            else: 
                print "Resume %s motion: Nitrogen flow status is %s " % (self.scannable.getName(), FLOW_STATUS[self.newFlowStatus])
                self.scannable.resume()
        self.lastFlowStatusUpdated=self.newFlowStatus

PV_MonitorListener_Dictionary={'laser' : ("BL21I-MO-ARM-01:TTH:LASER:STATUS",LaserScannerMonitorListener()),
                               'flow'  : ("BL21I-MO-ARM-01:TTH:SSEAL:NTRGN:STATUS",FlowStatusMonitorListener())}

armtthWithScanner = PauseableScannable("armtthWithScanner", armtth, 0.01, PV_MonitorListener_Dictionary)

# CONTROL_STATUS={0:'pause', 1:'resume'}
# class MyObserver(IObserver):
#     
#     def __init__(self, scannable=None):
#         self.scannable=scannable
#         self.newFlowStatus=0
#     
#     def setScannable(self, s):
#         self.scannable=s
#         return self
#     
#     def update(self, source, change):
#         if source==self:
#             if change == 0:
#                 self.scannable.pause()
#             elif change == 1:
#                 self.scannable.resume()
#             else:
#                 print "Status : %d is not supported." % change