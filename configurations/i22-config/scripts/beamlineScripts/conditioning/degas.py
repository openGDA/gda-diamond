import time

class Degas:
    def __init__(self, slit, slitmax, gauge, gaugemax, P=2.0, I=0.1, D=0.3, Derivator=0.0, Integrator=0.0, Integrator_max=500, Integrator_min=-500):
        self.slit = slit
        self.slitmax = slitmax
        self.gauge = gauge
        self.Kp=P
        self.Ki=I
        self.Kd=D
        self.Derivator=Derivator
        self.Integrator=Integrator
        self.Integrator_max=Integrator_max
        self.Integrator_min=Integrator_min

        self.set_point=gaugemax
        self.error=0.0
        self.originalposition = self.slit.getPosition()
        self.runpos = self.slitmax > self.originalposition
        self.abort = False

    def update(self):
        """
        Calculate PID output value for given reference input and feedback
        """
        current_value = self.gauge.getPosition()
        self.error = self.set_point - current_value
        self.P_value = self.Kp * self.error
        self.D_value = self.Kd * ( self.error - self.Derivator)
        self.Derivator = self.error
        self.Integrator = self.Integrator + self.error
        if self.Integrator > self.Integrator_max:
            self.Integrator = self.Integrator_max
        elif self.Integrator < self.Integrator_min:
            self.Integrator = self.Integrator_min
        self.I_value = self.Integrator * self.Ki
        PID = self.P_value + self.I_value + self.D_value
        return PID

    def setPoint(self,set_point):
        self.set_point = set_point
        self.Integrator=0
        self.Derivator=0

    def atslitEnd(self):
        position = self.slit.getPosition()
        if self.runpos:
            if position >= self.slitmax:
                return True
        else:
            if position <= self.slitmax:
                return True
        return False
    
    def run(self):
        while not self.atslitEnd() and not self.abort:
            if self.runpos:
                inc self.slit self.update()
            else:
                inc self.slit -1*self.update()
            time.sleep(1)
            print "vacuum at %s %5.5g -- %s position %5.5g" % (self.gauge.getName(), self.gauge.getPosition(), self.slit.getName(), self.slit.getPosition())
        print "finished or aborted"
        self.slit.moveTo(self.originalposition)
        print "%s moved back to %5.5g" % (self.slit.getName(), self.originalposition)

#deg=Degas(s1_xgap, 6.000, gauge02, 4e-07, P=1e6, I=10000)
#set up Gauge to monitor pressure
#gauge02=DisplayEpicsPVClass("gauge02","BL22I-VA-GAUGE-02:P","mbar","%.2e")
#Before running try deg.update() to give initial PID step. CHeck that this is sensible.
#deg.update()
