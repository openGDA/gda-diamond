class pol2Comp(ScannableMotionBase):
    '''PA compensation device'''
    def __init__(self,name,_dettans, _tthp, _thp,devices,help=None):
        self.setName(name)
        if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
        self.setInputNames([name])
        self.setExtraNames(['dettrans, thpcor','tthp'])
        self.devices=devices
        self.setOutputFormat(["%4.4f","%4.4f","%4.4f",'%4.4f'])
        self.Units=['deg']
        self.setLevel(5)    
    

    def sin_func(self,x,coefs):
        return (coefs[0]/2)*sin((x+coefs[1])*pi/180.)+coefs[2]

    def calibrate(self,devices):
        self.dettrans_sin_coefs = self.devices[dettrans]
        self.tthp_sin_coefs = self.devices[tthp]
        self.thp_sin_coefs = self.devices[thp]
        self.dettransoffset = self.sin_func(stoke(),self.dettrans_sin_coefs)-dettrans()
        self.tthpoffset = self.sin_func(stoke(),self.tthp_sin_coefs)-tthp()
        self.thpoffset = self.sin_func(stoke(),self.thp_sin_coefs)-thp()
        print('PA offsets = '+str(self.dettransoffset)+' '+str(self.tthpoffset)+' '+str(self.thpoffset))

    def asynchronousMoveTo(self,value):
        self.dettranscomp = self.sin_func(value,self.dettrans_sin_coefs)+self.dettransoffset
        self.tthpcomp = self.sin_func(value,self.tthp_sin_coefs)+self.tthpoffset
        self.thpcomp = self.sin_func(value,self.thp_sin_coefs)+self.thpoffset
        dettrans.asynchronousMoveTo(self.dettranscomp)
        tthp.asynchronousMoveTo(self.tthpcomp)
        thp.asynchronousMoveTo(self.thpcomp)

    def getPosition(self):
        try:
            detranscomp = self.sin_func(stoke(),self.dettrans_sin_coefs)-self.dettransoffset
            tthpcomp = self.sin_func(stoke(),self.tthp_sin_coefs)-self.tthpoffset
            thpcomp = self.sin_func(stoke(),self.thp_sin_coefs)-self.thpoffset
            return stoke(), self.detranscomp, self.tthpcomp, self.thpcomp
        except:
            print("Must be calibrated first.\nYou must use pol2.calibrate() at stokes 0")
    def isBusy(self):
            return stoke.isBusy(), dettrans.isBusy(), tthp.isBusy(), thp.isBusy() 



#devices={'dettrans':[1.7736,-185.32,-25.368],'tthp':[1.662, 94.796, 90.404], 'thp':[0.4714,101.48,47.811]}
#pol2=pol2Comp("pol2", dettrans, tthp, thp, devices, help="Dettrans, tthp, thp compensation for pol device.")