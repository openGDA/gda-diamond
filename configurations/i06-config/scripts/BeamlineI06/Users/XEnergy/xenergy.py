import time
from gda.device.scannable import PseudoDevice
from gda.epics import CAClient
#use iddrpenergy!!!!!!!!!!!!!

class UndulatorControlClass:
    def __init__(self):
        self.energy = 700.0
        self.xpol = 'pc'
        self.offhar = 0.0
        self.detune = 3.0
        self.xmode = '2idxmcd' # other possible values: '2idxas', 'idd' , 'idu'
        self.ugap = 50.0
        self.dgap = 50.0
        self.dtrp = 22.0
        self.dbrp = 22.0
        self.utrp = -22.0
        self.ubrp = -22.0
        #this is for storing the results of calculated Id parameters for comparison with the actual position
        self.calcParams = None
        self.calcParams = {'dgap' : 0.0, 'ugap' : 0.0, 'dtrp' : 0.0, 'dbrp' : 0.0, 'utrp' : 0.0, 'ubrp': 0.0}
        
        temp = {'Horizontal': 'lh', 'lh': 'lh', 'Vertical': 'lv', 'lv': 'lv'}
        self.aliases = {'PosCirc': 'pc', 'pc' : 'pc', 'nc' : 'nc', 'NegCirc': 'nc'}
        self.aliases.update(temp) 
        self.dpcListGap = self.makePolyListGap('d','pc')
        self.dncListGap = self.makePolyListGap('d','nc')
        self.upcListGap = self.makePolyListGap('u','pc')
        self.uncListGap = self.makePolyListGap('u','nc')

        self.dlhListGap = self.makePolyListGap('d','lh')
        self.dlvListGap = self.makePolyListGap('d','lv')
        self.ulhListGap = self.makePolyListGap('u','lh')
        self.ulvListGap = self.makePolyListGap('u','lv')

        self.dpcListPhase = self.makePolyListPhase('d')
        self.dncListPhase = [-x for x in self.dpcListPhase]
        self.upcListPhase = self.makePolyListPhase('u')
        self.uncListPhase = [-x for x in self.upcListPhase]
        
        self.dlhListPhase = [0]
        self.dlvListPhase = [32]

        self.dListGapDict = {'pc' : self.dpcListGap, 'nc' : self.dncListGap, 'lh' : self.dlhListGap, 'lv' : self.dlvListGap}
        self.uListGapDict = {'pc' : self.upcListGap, 'nc' : self.uncListGap, 'lh' : self.ulhListGap, 'lv' : self.ulvListGap}

        self.dListPhaseDict = {'pc' : self.dpcListPhase, 'nc' : self.dncListPhase, 'lh' : [0], 'lv' : [32]}
        self.uListPhaseDict = {'pc' : self.upcListPhase, 'nc' : self.uncListPhase, 'lh' : [0], 'lv' : [32]}

    def makePolyListGap(self,id,xpol):
        plist = []
        for i in range(12):
            plist.append(self.geteVTommCoeffGap(id,xpol,i+1))
        return plist

    def makePolyListPhase(self,id):
        plist = []
        for i in range(4):
            plist.append(self.geteVTommCoeffPhase(id,i+1))
        return plist

    def geteVTommCoeffGap(self,id,xpol,index):
        pvstr = "BL06I-OP-ID"
        if id[0] not in ['u', 'd']:
            print "->id string is wrong: legal values [u,d]. Operation cancelled."
            return 0
        if xpol not in ['pc', 'nc', 'lh','lv']:
                print "polarization string is wrong: legal values [pc,nc]. Operation cancelled."
                return 0
        if ((index<1)|(index>12))  :
            print "index is wrong: legal values [1 .. 12]. Operation cancelled."
            return 0
        ca = CAClient()
        pvstr+=id + '-01:'
        if xpol==self.aliases['lh']:
            pvstr += 'HZ:C' + str(index)
        if xpol==self.aliases['lv']:
            pvstr += 'VT:C' + str(index)
        if xpol==self.aliases['pc']:
            pvstr += 'PC:C' + str(index)
        if xpol==self.aliases['nc']:
            pvstr += 'NC:C' + str(index)    
        pvstr = pvstr.upper()        
        return float(ca.caget(pvstr))

    def geteVTommCoeffPhase(self,id,index):
        pvstr = "BL06I-OP-ID"
        if id not in ['u','d']:
            print "id string is wrong: legal values ['u','d']. Operation cancelled."
            return 0
        if ((index<1)|(index>12))  :
            print "index is wrong: legal values [1 .. 12]. Operation cancelled."
            return 0
        ca = CAClient()
        pvstr+=id + '-01:RP:C'+str(index)
        pvstr = pvstr.upper()
        return float(ca.caget(pvstr))

    def idmm(self,energy,plist):
        mm = 0.0
        for i in range(len(plist)): mm += plist[i]*pow(energy,i)
        return mm
  
    def calcIdPos(self,energy):
        #this method calculates the ID position. The allowed mode are:
        #'2idxmcd' to make xmcd with 2 undulators with opposite polarization
        #'2idxas' to use 2 undulator at the same energy and polarization, for maximum intensity
        #'idd', 'idu' to use only one undulator
        #the field 'offhar' is used to keep the undulator slightly detuned and reduce the flux
        #the field 'detune' is the amount of mm the gap of the undulator with unwnated polarization is closed
        #when using '2idxmcd' e
        if self.xmode not in ['2idxmcd', '2idxas', 'idd', 'idu']:
            print "mode string is wrong: legal values ['2idxmcd', '2idxas', 'idd', 'idu']. Operation cancelled."
            return 0
        if (self.xpol not in(['pc', 'nc', 'lh', 'lv'])):
            print "polarization string is wrong: legal values ['pc', 'nc', 'lh', 'lv']"
            return 0  
     
        if ((self.xmode.upper() == '2IDXMCD')&(self.xpol in ['pc', 'nc'])):
            #print "calculatin Id parameters for 2 undulator xmcd, circular"        
            dgap = self.idmm(energy, self.dpcListGap)    
            ugap = self.idmm(energy, self.uncListGap)
            if (self.xpol == 'pc'):
                ugap -= abs(self.detune)
            elif (self.xpol == 'nc'):
                dgap -= abs(self.detune)
            ugap -= abs(self.offhar)
            dgap -= abs(self.offhar)
            dtrp = dbrp = self.idmm(dgap,self.dpcListPhase)
            utrp = ubrp = self.idmm(ugap,self.uncListPhase)

        if ((self.xmode.upper() == '2IDXMCD')&(self.xpol in ['lh', 'lv'])):
            #print "2 undulator xmcd, linear"        
            dgap = self.idmm(energy, self.dlhListGap)    
            ugap = self.idmm(energy, self.ulvListGap)
            if (self.xpol == 'lh'):
                ugap -= abs(self.detune)
            elif (self.xpol == 'lv'):
                dgap -= abs(self.detune)
            ugap -= abs(self.offhar)
            dgap -= abs(self.offhar)
            dtrp = dbrp = self.idmm(energy, self.dlhListPhase)
            utrp = self.idmm(energy, self.dlvListPhase)
            ubrp = -self.idmm(energy, self.dlvListPhase)

        if (self.xmode.upper() == '2IDXAS'):
            #print "2 undulator xas"        
            dgap = self.idmm(self.energy, self.dListGapDict[self.xpol])    
            ugap = self.idmm(self.energy, self.uListGapDict[self.xpol])
            ugap -= abs(self.offhar)
            dgap -= abs(self.offhar)
            if (self.xpol in ['pc', 'nc', 'lh']):
                dtrp = dbrp = self.idmm(dgap,self.dListPhaseDict[self.xpol])
                utrp = ubrp = self.idmm(ugap,self.uListPhaseDict[self.xpol])
            else:
                dtrp = self.idmm(dgap,self.dListPhaseDict[self.xpol])
                dbrp = -self.idmm(dgap,self.dListPhaseDict[self.xpol])
                utrp = self.idmm(ugap,self.uListPhaseDict[self.xpol])
                ubrp = -self.idmm(ugap,self.uListPhaseDict[self.xpol])

        if (self.xmode.upper() == 'IDD'):
            #print "downstream ondulator mode"        
            dgap = self.idmm(energy, self.dListGapDict[self.xpol])    
            ugap = 150.0
            utrp = ubrp = 0.0
            dgap -= abs(self.offhar)
            if (self.xpol in ['pc', 'nc', 'lh']):
                dtrp = dbrp = self.idmm(dgap,self.dListPhaseDict[self.xpol])
                
            else:
                dtrp = self.idmm(dgap,self.dListPhaseDict[self.xpol])
                dbrp = -self.idmm(dgap,self.dListPhaseDict[self.xpol])

        if (self.xmode.upper() == 'IDU'):
            #print "downstream ondulator mode"        
            dgap = 150    
            ugap = self.idmm(energy, self.uListGapDict[self.xpol])
            ugap -= abs(self.offhar)
            dtrp = dbrp = 0
            if (self.xpol in ['pc', 'nc', 'lh']):
                utrp = ubrp = self.idmm(ugap,self.uListPhaseDict[self.xpol])
            else:
                utrp = self.idmm(ugap,self.uListPhaseDict[self.xpol])
                ubrp = -self.idmm(ugap,self.uListPhaseDict[self.xpol])       

        #print "requested energy, polarization, detune:", energy, self.xpol, self.detune
        #print "IDD parameters:",dtrp,dbrp, dgap
        #print "IDU parameters:",utrp,ubrp, ugap
        self.calcParams['dgap'] = dgap
        self.calcParams['ugap'] = ugap
        self.calcParams['dtrp'] = dtrp
        self.calcParams['dbrp'] = dbrp
        self.calcParams['utrp'] = utrp
        self.calcParams['ubrp'] = ubrp
        return 1  

    def storeIdPos(self):
        self.dgap = self.calcParams['dgap']
        self.ugap = self.calcParams['ugap']
        self.dtrp = self.calcParams['dtrp']
        self.dbrp = self.calcParams['dbrp']
        self.utrp = self.calcParams['utrp']
        self.ubrp = self.calcParams['ubrp']

    def setParameters(self, energy, xpol, xmode, offhar, detune):
        self.energy = energy
        self.xpol = xpol
        self.xmode = xmode
        self.offhar = offhar
        self.detune = detune
        
    def xenergyIsBusy(self):
        flag = pgmenergy.isBusy()
        flag |= (idugap.isBusy() | iddgap.isBusy())
        flag |= (iddtrp.isBusy() | iddbrp.isBusy() | idutrp.isBusy() | idubrp.isBusy())
        return flag

    def xenergyMove(self):
        pgmenergy.asynchronousMoveTo(self.energy)
        iddgap.asynchronousMoveTo(self.dgap)
        idugap.asynchronousMoveTo(self.ugap)
        iddtrp.asynchronousMoveTo(self.dtrp)
        iddbrp.asynchronousMoveTo(self.dbrp)
        idutrp.asynchronousMoveTo(self.utrp)
        idubrp.asynchronousMoveTo(self.ubrp)
        t0 = time.time()
        while (self.xenergyIsBusy()):
            self.isBusy = True
            time.sleep(0.1)
            if ((time.time()-t0)>180):#time limit increased!!!!!!!!
                print "time out error: the ID is still busy." 
                break
        #return True if all the motors are not busy
        return not (self.xenergyIsBusy())


class XenergyClass(PseudoDevice):
    def __init__(self,name,id):
        self.setName(name);
        self.setInputNames([name])
        self.setOutputFormat(['%3.2f'])
        self.setExtraNames([])
        self.setLevel(6)
        
        self.id = id
        self.energy = self.id.energy 
        self.xmode = self.id.xmode
        self.offhar = self.id.offhar
        self.detune = self.id.detune
        self.xpol = self.id.xpol
        
        self.iambusy = False

    def getPosition(self): 
        #print "IDD parameters:",self.id.dtrp, self.id.dbrp, self.id.dgap
        #print "IDU parameters:",self.id.utrp, self.id.ubrp, self.id.ugap
        return self.energy

    def asynchronousMoveTo(self, new_energy):
        self.iambusy = True
        self.id.setParameters(new_energy, self.id.xpol, self.id.xmode, self.id.offhar, self.id.detune)
        self.id.calcIdPos(new_energy)
        self.id.storeIdPos()
        self.id.xenergyMove()
        #print new_energy,xpol2.getPosition(),self.offhar
        self.energy = new_energy
        self.iambusy = False
        return 

    def isBusy(self):
        self.iambusy = self.id.xenergyIsBusy()
        return self.iambusy

class XpolClass(PseudoDevice):
    def __init__(self,name,id):
        self.setName(name);
        self.id = id
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(['%s'])
        self.setLevel(5)
        self.xpol = self.id.xpol
        self.iambusy = False
        self.aliases = {'PosCirc': 'pc', 'pc' : 'pc', 'nc' : 'nc', 'NegCirc': 'nc'} 
        self.aliases.update({'Horizontal': 'lh', 'Vertical': 'lv', 'lh': 'lh', 'lv': 'lv'})

    def getPosition(self): 
        return self.xpol

    def asynchronousMoveTo(self, newPol):
    	#add a control line to check that the "newpol" is an allowed string!!!!!!!!!!!!
        self.iambusy = True
        self.id.setParameters(self.id.energy, self.aliases[newPol], self.id.xmode, self.id.offhar, self.id.detune)
        self.id.calcIdPos(self.id.energy)
        self.id.storeIdPos()
        self.id.xenergyMove()        
        #print xenergy2.getPosition(),newPol,xenergy2.detune
        self.xpol = self.aliases[newPol]
        self.iambusy = False
        return 

    def isBusy(self):
        self.iambusy = self.id.xenergyIsBusy()
        return self.iambusy

class XmodeClass(PseudoDevice):
    def __init__(self,name,id):
        self.setName(name);
        self.id = id
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(['%s'])
        self.setLevel(4)
        self.xmode = '2idxmcd'
        self.iambusy = False
        #self.aliases = {'xmcd': 'xmcd2und', 'xmcd2und' : 'xmcd2und', 'xas' : 'xas2und', 'xas2und': 'xas2und'} 
        #self.aliases.update({'xdd': 'xdd', 'xud': 'xud'})

    def getPosition(self): 
        print "allowed xmode values: iduxmcd, iduxas, idd, idu"
        self.xmode = self.id.xmode
        return self.xmode

    def asynchronousMoveTo(self, newMode):
        self.iambusy = True
        self.id.setParameters(self.id.energy, self.id.xpol, newMode, self.id.offhar, self.id.detune)
        self.id.calcIdPos(self.id.energy)
        self.id.storeIdPos()
        self.id.xenergyMove()        
        #print self.id.energy,newMode,xenergy2.detune
        self.xmode = newMode
        self.iambusy = False
        return 

    def isBusy(self):
        self.iambusy = self.id.xenergyIsBusy()
        return self.iambusy
       
class OffHarClass(PseudoDevice):
    def __init__(self,name,id):
        self.setName(name);
        self.id = id
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(['%3.2f'])
        self.setLevel(3)
        self.offhar = 0
        self.iambusy = False

    def getPosition(self): 
        return self.offhar

    def asynchronousMoveTo(self, newOffHar):
        self.iambusy = True
        self.id.setParameters(self.id.energy, self.id.xpol, self.id.xmode, newOffHar, self.id.detune)
        self.id.calcIdPos(self.id.energy)
        self.id.storeIdPos()
        self.id.xenergyMove()        
        #print self.id.energy,newOffHar,xenergy2.detune
        self.offhar = newOffHar
        self.iambusy = False
        return 

    def isBusy(self):
        self.iambusy = self.id.xenergyIsBusy()
        return self.iambusy
       
class DetuneClass(PseudoDevice):
    def __init__(self,name,id):
        self.setName(name);
        self.id = id
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(['%3.2f'])
        self.setLevel(2)
        self.detune = self.id.detune
        self.iambusy = False

    def getPosition(self): 
        return self.detune

    def asynchronousMoveTo(self, newDetune):
        self.iambusy = True
        self.id.setParameters(self.id.energy, self.id.xpol, self.id.xmode, self.id.offhar, newDetune)
        self.id.calcIdPos(self.id.energy)
        self.id.storeIdPos()
        self.id.xenergyMove()        
        #print self.id.energy, newDetune, self.id.detune
        self.detune = newDetune
        self.iambusy = False
        return 

    def isBusy(self):
        self.iambusy = self.id.xenergyIsBusy()
        return self.iambusy

exec('[ins_device, xenergy, xpol, xmode, offhar, detune] = [None, None, None, None, None, None]')

iduxmcd = '2idxmcd'
iduxas = '2idxas'
idd =  'idd'
idu = 'idu'

ins_device = UndulatorControlClass()

xenergy = XenergyClass("xenergy",ins_device)

xpol = XpolClass("xpol",ins_device)

xmode = XmodeClass("xmode",ins_device)

offhar = OffHarClass("offhar",ins_device)

detune = DetuneClass("detune",ins_device)

