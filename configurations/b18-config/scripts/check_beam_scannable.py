from gda.device.scannable import ScannableBase
from gda.device import DeviceException
from gda.epics import CAClient
from gda.jython import InterfaceProvider

def warn(message):
    InterfaceProvider.getTerminalPrinter().print(message)
    
class CheckBeamScannable(ScannableBase) :
    
    def __init__(self, name) :
        self.name = name
        self.inputNames = [name]
        self.setOutputFormat({});
        self.setInputNames({});
        self.ca1 = CAClient();

    def atScanStart(self):
        beam_on=True
        d1=0
        d2=0
        d3=0
        a3=0
        d7=0
        d9=0
        Shtr0=0
        Shtr1=0
        warn_msg=''
        if self.ca1.caget('BL18B-DI-PHDGN-01:STA')!='1':
            d1=1
            warn_msg=warn_msg+'\nD1 closed - diagnostic in'
        if self.ca1.caget('BL18B-DI-PHDGN-02:STA')!='1':
            d2=1
            warn_msg=warn_msg+'\nD2 closed - diagnostic in'
        if self.ca1.caget('BL18B-DI-PHDGN-03:STA')!='1':
            d3=1
            warn_msg=warn_msg+'\nD3 closed - diagnostic in'
        if self.ca1.caget('BL18B-OP-ATTN-03:P1:UPD.D')!='0.0':
            a3=1
            warn_msg=warn_msg+'\nA3 closed - fluorescence screen in'
        if self.ca1.caget('BL18B-DI-PHDGN-07:STA')!='3':
            d7=1
            warn_msg=warn_msg+'\nD7 closed - front laser in'
        if self.ca1.caget('BL18B-DI-PHDGN-09:STA')!='3':
            d9=1
            warn_msg=warn_msg+'\nD9 closed - camera in'
        if self.ca1.caget('BL18B-PS-SHTR-01:STA')=='3':
            Shtr0=1
            warn_msg=warn_msg+'\nExperimental Shutter closed'
        if self.ca1.caget('FE18B-PS-SHTR-02:STA')=='3':
            Shtr1=1
            warn_msg=warn_msg+'\nOptic Shutter closed'
        on=[d1,d2,d3,a3,d7,d9,Shtr0,Shtr1]
        if sum(on) is not 0:
            beam_on=False
            warn('X-ray beam not on:'+warn_msg)
        
        if beam_on == False :
            raise DeviceException(warn_msg)
        