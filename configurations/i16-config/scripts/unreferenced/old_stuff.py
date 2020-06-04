class DisplayEpicsPVLakeshoreTemperatureInCelsius(ScannableMotionBase):
    def __init__(self, name, pvstring, unitstring, formatstring,channel,level):
        self.setName(name);
        self.setInputNames([])
#        self.setExtraNames([name+'S']);
        self.Units=[unitstring]
        self.setOutputFormat([formatstring])
#        self.setOutputFormat([formatstring,formatstring])
        self.setLevel(level)
        self.pvstring=pvstring
        self.channel=channel

    def getPosition(self):
        return float(caget(self.pvstring+'CRDG'+self.channel))
        
    def isBusy(self):
        sleep(0.1)
        return 0