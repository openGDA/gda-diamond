
from Diamond.PseudoDevices.Timers import *;

print "-------------------------------------------------------------------";
print 'Creating timers: ';
print 'For time reporting, using stopwatch and stopclock';
stopwatch=ShowTimeClass('stopwatch');
timekeeper=ShowTimeClass('timekeeper');
timekeeper.autoReset=False;

clock=ShowClockClass('clock');

print 'For time measureing, using lineTime and pointTime for the time spent on one line of a scan and each scan point';
lineTime=LineTimeClass('lineTime');
pointTime=PointTimeClass('pointTime');

print "To control the speed of a scan, using waitTimer as a counterTimer or scanTimer as scannable" 
waitTimer=WaitTimerClass('waitTimer');

#To scan against time. 
timer=ScanTimerClass('timer');
scanTimer=ScanTimerClass('scanTimer');

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
#Example 1: scan scanTimer 0 20 5 pointTime lineTime stopwatch clock
#Example2 scan testMotor1 0 10 1 dummyCounter 5 stopwatch clock

Dummies.addGroupMember(dummyCounter);
Dummies.addGroupMember(dummyCounter1);
Dummies.addGroupMember(dummyCounter2);


