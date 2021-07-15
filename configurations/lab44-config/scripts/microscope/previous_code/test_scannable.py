class test_Class(PseudoDevice):
    def __init__(self,name,motor1, motor2, motorz):
        self.setName(name)
        self.setInputNames(['xx'])
        self.setOutputFormat(['%3.2f'])
        self.setExtraNames(['sub'])
        self.setLevel(6)
        self.motor1 = motor1
        self.motor2 = motor2
        self.motorz = motorz
        self.xPosition = 0.0 
        
        self.iambusy = False
         
    def atScanStart(self):
        return

    def atScanEnd(self):
        return

    def getPosition(self): 
        print self.motor1.getPosition()
        newPosition = self.motor1.getPosition()
        return newPosition

    def asynchronousMoveTo(self, new_xx):
        xx = self.motor1.getPosition()
        yy = self.motor2.getPosition()
        print xx, yy
        newZ = (xx-yy)/10.0
        print('new z = ', newZ)
        #motorz.asynchronousMoveTo(newZ)
        self.motor1.asynchronousMoveTo(new_xx)
        return 

    def isBusy(self):
        return self.iambusy