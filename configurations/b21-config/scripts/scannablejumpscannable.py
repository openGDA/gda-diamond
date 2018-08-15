from gdascripts.pd.time_pds import tictoc
from gda.device.scannable import ScannableMotionBase

"""
   scan scannablejumpscannable.ScJuSc("step",4,5,x,-.9) 0 10 1 x bsdiode

   This will move scannable x to -.9 on or after the ScJuSc is moved past 5
   ScJuSc will pause for 4 seconds on each step

Writing data to file (NeXus): <ahappyplace>
step	time	      x	bsdiode
   0	4.01	1.9000	 91.321
1.00	8.05	1.9000	 98.516
2.00	12.07	1.9000	 98.516
3.00	16.09	1.9000	 18.704
4.00	20.13	1.9000	 19.151
5.00	24.15	-0.9000	 40.334
6.00	28.17	-0.9000	 25.024
7.00	32.19	-0.9000	 25.024
8.00	36.24	-0.9000	 16.380
9.00	40.26	-0.9000	 64.800
10.00	44.28	-0.9000	 25.087
Scan complete.
"""

class ScJuSc(ScannableMotionBase):
    def __init__(self, name, waitstep, jumppoint, jumpscannable, jumpto, ):
        self.setName(name);
        self.jumpscannable = jumpscannable
        self.jumppoint = jumppoint
        self.jumpto = jumpto
        self.waitstep = waitstep
        self.setInputNames([name])
        self.setExtraNames(["time"])
        self.Units=['sec']
        self.setOutputFormat(['%6.2f', "%6.2f"])
        self.setLevel(7)
        self.timer=tictoc()
        self.waitUntilTime = 0
        self.mypos = 0.0

    def atScanStart(self):
        self.timer.reset()
        self.waitUntilTime = 0

    def rawGetPosition(self):
        return [self.mypos, self.timer()]

    def rawAsynchronousMoveTo(self,newpos):
        self.mypos = newpos
        self.waitUntilTime=self.timer()+self.waitstep
        if newpos >= self.jumppoint:
            self.jumpscannable.asynchronousMoveTo(self.jumpto)

    def stop(self):
        self.waitUntilTime = 0

    def rawIsBusy(self):
        return (self.timer()<self.waitUntilTime) or (self.jumpscannable.isBusy())

