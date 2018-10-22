'''
Example 1: scan scanTimer 0 20 5 pointTime lineTime stopwatch clock
Example 2: scan testMotor1 0 10 1 dummyCounter 5 stopwatch clock
'''
from Diamond.PseudoDevices.Timers import ShowTimeClass, ShowClockClass,\
    LineTimeClass, PointTimeClass, WaitTimerClass, ScanTimerClass,\
    SoftCounterClass
from gda.device.scannable.scannablegroup import ScannableGroup

#from Diamond.PseudoDevices.Timers import *;

print "-"*100;
print 'Creating "Timers" scannable group: ';
print 'For time reporting, using "stopwatch", "timekeeper", and "clock" objects';
stopwatch=ShowTimeClass('stopwatch');
timekeeper=ShowTimeClass('timekeeper');
timekeeper.autoReset=False;
clock=ShowClockClass('clock');

print 'For time measuring, using "lineTime" and "pointTime" for the time spent on one line of a scan and each scan point, respectively';
lineTime=LineTimeClass('lineTime');
pointTime=PointTimeClass('pointTime');

print "To control the speed of a scan, using 'waitTimer' for wait delay or 'scanTimer' or 'timer' as scannable" 
waitTimer=WaitTimerClass('waitTimer');

#To scan against time. 
timer=ScanTimerClass('timer');
scanTimer=ScanTimerClass('scanTimer');

Timers=ScannableGroup()
Timers.setName('Timers')
Timers.addGroupMember(clock);
Timers.addGroupMember(stopwatch);
Timers.addGroupMember(timekeeper);
Timers.addGroupMember(lineTime);
Timers.addGroupMember(pointTime);
Timers.addGroupMember(waitTimer);
Timers.addGroupMember(timer);
Timers.addGroupMember(scanTimer);


dummyCounter=SoftCounterClass('dummyCounter');
dummyCounter1=SoftCounterClass('dummyCounter1');
dummyCounter2=SoftCounterClass('dummyCounter2');

from Diamond.PseudoDevices.DummyShutter import DummyShutterClass
dummyShutter = DummyShutterClass('dummyShutter', delayAfterOpening=0.5, delayAfterClosing=0);
#dummyCounter.addShutter(dummyShutter);

Dummies=ScannableGroup()
Dummies.setName("Dummies")
Dummies.addGroupMember(dummyCounter);
Dummies.addGroupMember(dummyCounter1);
Dummies.addGroupMember(dummyCounter2);


