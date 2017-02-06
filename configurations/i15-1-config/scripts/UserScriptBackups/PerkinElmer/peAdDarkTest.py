class PeAdDarkTest (PeAdTest):

    def preConfigure(self, info):
        PeAdTest.preConfigure(self, info);
        self.hdfPlugin = "HDF5B:"

    def run(self, position):
        ##caput(detPVs[det]+"PROC2:EnableBackground","0") #For file writing
        self.adBase.setIntBySuffix("PROC2:EnableBackground",0)

        PeAdTest.run(self, position)

        ##caput("BL15J-EA-DET-01:PROC2:SaveBackground","1")
        ##caput("BL15J-EA-DET-01:PROC2:EnableBackground","1")
        self.adBase.setIntBySuffix("PROC2:SaveBackground",1)
        self.adBase.setIntBySuffix("PROC2:EnableBackground",1)