from gda.device.scannable import ScannableMotionBase

class szCryoCompensation(ScannableMotionBase):
    '''sz device with temperature compensation.\nUsage: pos szc 0 to maintain calibrated sz for current temperature. The device uses a 5th order polynomial  '''
    def __init__(self,name,_sz,devices,help=None):
            self.setName(name)
            if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
            self.setInputNames([name])
            self.devices=devices
            self.setOutputFormat(['%4.4f'])
            self.Units=['mm']
            self.setLevel(5)
            self.sz=_sz

    def poly(self,x,coefs):
        return coefs[0]*x**5+coefs[1]*x**4+coefs[2]*x**3+coefs[3]*x**2+coefs[4]*x+coefs[5]

    def calibrate(self,device,channel):
        self.channel = channel
        self.device = device
        self.cryopoly = self.devices[self.device]

        Temp=self.channel()
        self.szoffset = self.poly(Temp,self.cryopoly)-self.sz()
        print('Sample offset = '+str(self.szoffset))

    def asynchronousMoveTo(self,value):
        szcomp = self.poly(self.channel(), self.cryopoly)-self.szoffset - self.sz() + value
        self.sz.asynchronousMoveTo(szcomp + self.sz())

    def getPosition(self):
        try:
            szcom = self.poly(self.channel(), self.cryopoly)-self.szoffset -self.sz()
            return szcom 
        except:
            print("Must be calibrated first.\nEnter, for example szc.calibrate('4K',Ta)")
    def isBusy(self):
            return self.sz.isBusy()

#devices={'800K':[4.47796541e-14, -7.01502180e-11, 4.23265147e-08, -1.24509237e-05, 8.48412284e-04, 1.00618264e+01],'4K':[-1.43421764e-13, 1.05344999e-10, -1.68819096e-08, -5.63109884e-06, 3.38834427e-04, 9.90716891]}
#szc=szCryoCompensation("szc", sz, devices, help="Sample height with temperature compensation.\nEnter, for example szc.calibrate('4K',Ta) \nto calibrate using the 4K cryo and channel Ta or\nszc.calibrate('800K',Tc) for the cryofurnace.")
