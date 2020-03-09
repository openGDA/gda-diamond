from gda.jython.commands import GeneralCommands
from gda.epics import CAClient
from gda.factory import Finder

finder = Finder.getInstance()

zebra=finder.find("zebra")      # zebra1 BL12I-EA-ZEBRA-01:
zebra2=finder.find("zebra2")    # zebra2 BL12I-EA-ZEBRA-02:
zebra3=finder.find("zebra3")    # zebra3 BL12I-EA-ZEBRA-03:

zebra2Root ="BL12I-EA-ZEBRA-02"

def callCaput(name, index, val):
    name = name %(index)
    pvName = zebra2Root + name
    if CAClient.get(pvName) != val:
        CAClient.put(pvName, val)


def setZebra2ModeOLD(mode):
    print "Started checking Zebra1 set-up"
    pvNameZebra1 = "BL12I-EA-ZEBRA-01:OUT1_LVDS"
    if CAClient.get(pvNameZebra1) != 31:
        CAClient.put(pvNameZebra1, 31)
    print "Finished checking Zebra1 set-up"
    
    print "Started setting Zebra2 to mode = %s" %mode
    if mode != 1 and mode != 2:
        raise Exception("Bad input Zebra2 mode: "+`mode`)
    
    if mode == 1:   #step-scan
        #soft_in     = 1;
        CAClient.put(zebra2Root+":SOFT_IN", 1)
        
        pvName = ":AND%s_ENA"
        #ena_and[0]  = 3;
        callCaput(pvName, 0+1, 3)
        #ena_and[1]  = 3;
        callCaput(pvName, 1+1, 3)
        #ena_and[2]  = 3;
        callCaput(pvName, 2+1, 3)
        #ena_and[3]  = 0;
        callCaput(pvName, 3+1, 0)
        
        pvName = ":AND1_INP%s"
        #and1_inp[0] = 1;
        callCaput(pvName, 0+1, 1)
        #and1_inp[1] = 60;
        callCaput(pvName, 1+1, 60)
        #and1_inp[2] = 0;
        callCaput(pvName, 2+1, 0)
        #and1_inp[3] = 0;
        callCaput(pvName, 3+1, 0)
        
        pvName = ":AND2_INP%s"
        #and2_inp[0] = 4;
        callCaput(pvName, 0+1, 4)
        #and2_inp[1] = 60;
        callCaput(pvName, 1+1, 60)
        #and2_inp[2] = 0;
        callCaput(pvName, 2+1, 0)
        #and2_inp[3] = 0;
        callCaput(pvName, 3+1, 0)
        
        pvName = ":AND3_INP%s"
        #and3_inp[0] = 7;
        callCaput(pvName, 0+1, 7)
        #and3_inp[1] = 60;
        callCaput(pvName, 1+1, 60)
        #and3_inp[2] = 0;
        callCaput(pvName, 2+1, 0)
        #and3_inp[3] = 0;
        callCaput(pvName, 3+1, 0)
        
        pvName = ":AND4_INP%s"
        #and4_inp[0] = 0;
        callCaput(pvName, 0+1, 0)
        #and4_inp[1] = 0;
        callCaput(pvName, 1+1, 0)
        #and4_inp[2] = 0;
        callCaput(pvName, 2+1, 0)
        #and4_inp[3] = 0;
        callCaput(pvName, 3+1, 0)
        
        #out1_ttl    = 34;
        CAClient.put(zebra2Root+":OUT1_TTL", 34)
        #out1_nim    = 0;
        CAClient.put(zebra2Root+":OUT1_NIM", 0)
        #out1_lvds   = 0;
        CAClient.put(zebra2Root+":OUT1_LVDS", 0)
        
        #out2_ttl    = 32;
        CAClient.put(zebra2Root+":OUT2_TTL", 32)
        #out2_nim    = 0;
        CAClient.put(zebra2Root+":OUT2_NIM", 0)
        #out2_lvds   = 0;
        CAClient.put(zebra2Root+":OUT2_LVDS", 0)
        
        #out3_ttl    = 33;
        CAClient.put(zebra2Root+":OUT3_TTL", 33)
        #out3_oc     = 0;
        CAClient.put(zebra2Root+":OUT3_OC", 0)
        #out3_lvds   = 0;
        CAClient.put(zebra2Root+":OUT3_LVDS", 0)
        
        #out4_ttl    = 34;
        CAClient.put(zebra2Root+":OUT4_TTL", 34)
        #out4_nim    = 0;
        CAClient.put(zebra2Root+":OUT4_NIM", 0)
        #out4_pecl   = 0;
        CAClient.put(zebra2Root+":OUT4_PECL", 0)
    
    if mode == 2:   #continuous scan
        #soft_in     = 1;
        CAClient.put(zebra2Root+":SOFT_IN", 1)
        
        pvName = ":AND%s_ENA"
        #ena_and[0]  = 3;
        callCaput(pvName, 0+1, 3)
        #ena_and[1]  = 3;
        callCaput(pvName, 1+1, 3)
        #ena_and[2]  = 3;
        callCaput(pvName, 2+1, 3)
        #ena_and[3]  = 0;
        callCaput(pvName, 3+1, 0)
        
        pvName = ":AND1_INP%s"
        #and1_inp[0] = 1;
        callCaput(pvName, 0+1, 1)
        #and1_inp[1] = 60;
        callCaput(pvName, 1+1, 60)
        #and1_inp[2] = 0;
        callCaput(pvName, 2+1, 0)
        #and1_inp[3] = 0;
        callCaput(pvName, 3+1, 0)
        
        pvName = ":AND2_INP%s"
        #and2_inp[0] = 4;
        callCaput(pvName, 0+1, 4)
        #and2_inp[1] = 60;
        callCaput(pvName, 1+1, 60)
        #and2_inp[2] = 0;
        callCaput(pvName, 2+1, 0)
        #and2_inp[3] = 0;
        callCaput(pvName, 3+1, 0)
        
        pvName = ":AND3_INP%s"
        #and3_inp[0] = 3;
        callCaput(pvName, 0+1, 3)
        #and3_inp[1] = 60;
        callCaput(pvName, 1+1, 60)
        #and3_inp[2] = 0;
        callCaput(pvName, 2+1, 0)
        #and3_inp[3] = 0;
        callCaput(pvName, 3+1, 0)
        
        pvName = ":AND4_INP%s"
        #and4_inp[0] = 0;
        callCaput(pvName, 0+1, 0)
        #and4_inp[1] = 0;
        callCaput(pvName, 1+1, 0)
        #and4_inp[2] = 0;
        callCaput(pvName, 2+1, 0)
        #and4_inp[3] = 0;
        callCaput(pvName, 3+1, 0)
        
        #out1_ttl    = 34;
        CAClient.put(zebra2Root+":OUT1_TTL", 34)
        #out1_nim    = 0;
        CAClient.put(zebra2Root+":OUT1_NIM", 0)
        #out1_lvds   = 32;
        CAClient.put(zebra2Root+":OUT1_LVDS", 32)
        
        #out2_ttl    = 0;
        CAClient.put(zebra2Root+":OUT2_TTL", 0)
        #out2_nim    = 0;
        CAClient.put(zebra2Root+":OUT2_NIM", 0)
        #out2_lvds   = 33;
        CAClient.put(zebra2Root+":OUT2_LVDS", 33)
        
        #out3_ttl    = 0;
        CAClient.put(zebra2Root+":OUT3_TTL", 0)
        #out3_oc     = 0;
        CAClient.put(zebra2Root+":OUT3_OC", 0)
        #out3_lvds   = 0;
        CAClient.put(zebra2Root+":OUT3_LVDS", 0)
        
        #out4_ttl    = 34;
        CAClient.put(zebra2Root+":OUT4_TTL", 34)
        #out4_nim    = 0;
        CAClient.put(zebra2Root+":OUT4_NIM", 0)
        #out4_pecl   = 0;
        CAClient.put(zebra2Root+":OUT4_PECL", 0)
    
    #Set the scan type
    CAClient.put(zebra2Root+":SCAN_TYPE", mode)
    print "Finished setting Zebra2 to mode = %s" %mode
    
    
# public void setValue(String beforeUnderscore, int beforeUnderscoreId, String afterUnderscore, int afterUnderscoreId,int val) throws Exception {
def setZebra2Mode_(mode):
    print "Started checking Zebra1 set-up." #caputStringAsWaveform("BL23I-EA-ZEBRA-01:ZEBRA:CONFIG_FILE", "/dls_sw/i23/epics/zebra/2019-1-14-tomo.zeb")
    #pvNameZebra1 = "BL12I-EA-ZEBRA-01:OUT1_LVDS"
    #if CAClient.get(pvNameZebra1) != 31:
    #    CAClient.put(pvNameZebra1, 31)
    zebra.setValue("OUT",1,"LVDS",-1, 31)
    print "Finished checking Zebra1 set-up."
    
    print "Started setting Zebra2 to mode = %s" %mode
    if mode != 1 and mode != 2:
        raise Exception("Bad input Zebra2 mode: "+`mode`)
    
    if mode == 1:   #step-scan
        #soft_in     = 1;
        #CAClient.put(zebra2Root+":SOFT_IN", 1)
        zebra2.setValue("SOFT",-1,"IN",-1, 1)
        
        #pvName = ":AND%s_ENA"
        #ena_and[0]  = 3;
        #callCaput(pvName, 0+1, 3)
        zebra2.setValue("AND",1,"ENA",-1, 3)
        #ena_and[1]  = 3;
        #callCaput(pvName, 1+1, 3)
        zebra2.setValue("AND",2,"ENA",-1, 3)
        #ena_and[2]  = 3;
        #callCaput(pvName, 2+1, 3)
        zebra2.setValue("AND",3,"ENA",-1, 3)
        #ena_and[3]  = 0;
        #callCaput(pvName, 3+1, 0)
        zebra2.setValue("AND",4,"ENA",-1, 0)
        
        #pvName = ":AND1_INP%s"
        #and1_inp[0] = 1;
        #callCaput(pvName, 0+1, 1)
        zebra2.setValue("AND",1,"INP",1, 1)
        #and1_inp[1] = 60;
        #callCaput(pvName, 1+1, 60)
        zebra2.setValue("AND",1,"INP",2, 60)
        #and1_inp[2] = 0;
        #callCaput(pvName, 2+1, 0)
        zebra2.setValue("AND",1,"INP",3, 0)
        #and1_inp[3] = 0;
        #callCaput(pvName, 3+1, 0)
        zebra2.setValue("AND",1,"INP",4, 0)
        
        #pvName = ":AND2_INP%s"
        #and2_inp[0] = 4;
        #callCaput(pvName, 0+1, 4)
        zebra2.setValue("AND",2,"INP",1, 4)
        #and2_inp[1] = 60;
        #callCaput(pvName, 1+1, 60)
        zebra2.setValue("AND",2,"INP",2, 60)
        #and2_inp[2] = 0;
        #callCaput(pvName, 2+1, 0)
        zebra2.setValue("AND",2,"INP",3, 0)
        #and2_inp[3] = 0;
        #callCaput(pvName, 3+1, 0)
        zebra2.setValue("AND",2,"INP",4, 0)
        
        #pvName = ":AND3_INP%s"
        #and3_inp[0] = 7;
        #callCaput(pvName, 0+1, 7)
        zebra2.setValue("AND",3,"INP",1, 7)
        #and3_inp[1] = 60;
        #callCaput(pvName, 1+1, 60)
        zebra2.setValue("AND",3,"INP",2, 60)
        #and3_inp[2] = 0;
        #callCaput(pvName, 2+1, 0)
        zebra2.setValue("AND",3,"INP",3, 0)
        #and3_inp[3] = 0;
        #callCaput(pvName, 3+1, 0)
        zebra2.setValue("AND",3,"INP",4, 0)
        
        #pvName = ":AND4_INP%s"
        #and4_inp[0] = 0;
        #callCaput(pvName, 0+1, 0)
        zebra2.setValue("AND",4,"INP",1, 0)
        #and4_inp[1] = 0;
        #callCaput(pvName, 1+1, 0)
        zebra2.setValue("AND",4,"INP",2, 0)
        #and4_inp[2] = 0;
        #callCaput(pvName, 2+1, 0)
        zebra2.setValue("AND",4,"INP",3, 0)
        #and4_inp[3] = 0;
        #callCaput(pvName, 3+1, 0)
        zebra2.setValue("AND",4,"INP",4, 0)
        
        #out1_ttl    = 34;
        #CAClient.put(zebra2Root+":OUT1_TTL", 34)
        zebra2.setValue("OUT",1,"TTL",-1, 34)
        #out1_nim    = 0;
        #CAClient.put(zebra2Root+":OUT1_NIM", 0)
        zebra2.setValue("OUT",1,"NIM",-1, 0)
        #out1_lvds   = 0;
        #CAClient.put(zebra2Root+":OUT1_LVDS", 0)
        zebra2.setValue("OUT",1,"LVDS",-1, 0)
        
        #out2_ttl    = 32;
        #CAClient.put(zebra2Root+":OUT2_TTL", 32)
        zebra2.setValue("OUT",2,"TTL",-1, 32)
        #out2_nim    = 0;
        #CAClient.put(zebra2Root+":OUT2_NIM", 0)
        zebra2.setValue("OUT",2,"NIM",-1, 0)
        #out2_lvds   = 0;
        #CAClient.put(zebra2Root+":OUT2_LVDS", 0)
        zebra2.setValue("OUT",2,"LVDS",-1, 0)
        
        #out3_ttl    = 33;
        #CAClient.put(zebra2Root+":OUT3_TTL", 33)
        zebra2.setValue("OUT",3,"TTL",-1, 33)
        #out3_oc     = 0;
        #CAClient.put(zebra2Root+":OUT3_OC", 0)
        zebra2.setValue("OUT",3,"OC",-1, 0)
        #out3_lvds   = 0;
        #CAClient.put(zebra2Root+":OUT3_LVDS", 0)
        zebra2.setValue("OUT",3,"LVDS",-1, 0)
        
        #out4_ttl    = 34;
        #CAClient.put(zebra2Root+":OUT4_TTL", 34)
        zebra2.setValue("OUT",4,"TTL",-1, 34)
        #out4_nim    = 0;
        #CAClient.put(zebra2Root+":OUT4_NIM", 0)
        zebra2.setValue("OUT",4,"NIM",-1, 0)
        #out4_pecl   = 0;
        #CAClient.put(zebra2Root+":OUT4_PECL", 0)
        zebra2.setValue("OUT",4,"PECL",-1, 0)
    
    if mode == 2:   #continuous scan
        #soft_in     = 1;
        #CAClient.put(zebra2Root+":SOFT_IN", 1)
        zebra2.setValue("SOFT",-1,"IN",-1, 1)
        
        #pvName = ":AND%s_ENA"
        #ena_and[0]  = 3;
        #callCaput(pvName, 0+1, 3)
        zebra2.setValue("AND",1,"ENA",-1, 3)
        #ena_and[1]  = 3;
        #callCaput(pvName, 1+1, 3)
        zebra2.setValue("AND",2,"ENA",-1, 3)
        #ena_and[2]  = 3;
        #callCaput(pvName, 2+1, 3)
        zebra2.setValue("AND",3,"ENA",-1, 3)
        #ena_and[3]  = 0;
        #callCaput(pvName, 3+1, 0)
        zebra2.setValue("AND",4,"ENA",-1, 0)
        
        #pvName = ":AND1_INP%s"
        #and1_inp[0] = 1;
        #callCaput(pvName, 0+1, 1)
        zebra2.setValue("AND",1,"INP",1, 1)
        #and1_inp[1] = 60;
        #callCaput(pvName, 1+1, 60)
        zebra2.setValue("AND",1,"INP",2, 60)
        #and1_inp[2] = 0;
        #callCaput(pvName, 2+1, 0)
        zebra2.setValue("AND",1,"INP",3, 0)
        #and1_inp[3] = 0;
        #callCaput(pvName, 3+1, 0)
        zebra2.setValue("AND",1,"INP",4, 0)
        
        #pvName = ":AND2_INP%s"
        #and2_inp[0] = 4;
        #callCaput(pvName, 0+1, 4)
        zebra2.setValue("AND",2,"INP",1, 4)
        #and2_inp[1] = 60;
        #callCaput(pvName, 1+1, 60)
        zebra2.setValue("AND",2,"INP",2, 60)
        #and2_inp[2] = 0;
        #callCaput(pvName, 2+1, 0)
        zebra2.setValue("AND",2,"INP",3, 0)
        #and2_inp[3] = 0;
        #callCaput(pvName, 3+1, 0)
        zebra2.setValue("AND",2,"INP",4, 0)
        
        #pvName = ":AND3_INP%s"
        #and3_inp[0] = 3;
        #callCaput(pvName, 0+1, 3)
        zebra2.setValue("AND",3,"INP",1, 3)
        #and3_inp[1] = 60;
        #callCaput(pvName, 1+1, 60)
        zebra2.setValue("AND",3,"INP",2, 60)
        #and3_inp[2] = 0;
        #callCaput(pvName, 2+1, 0)
        zebra2.setValue("AND",3,"INP",3, 0)
        #and3_inp[3] = 0;
        #callCaput(pvName, 3+1, 0)
        zebra2.setValue("AND",3,"INP",4, 0)
        
        #pvName = ":AND4_INP%s"
        #and4_inp[0] = 0;
        #callCaput(pvName, 0+1, 0)
        zebra2.setValue("AND",4,"INP",1, 0)
        #and4_inp[1] = 0;
        #callCaput(pvName, 1+1, 0)
        zebra2.setValue("AND",4,"INP",2, 0)
        #and4_inp[2] = 0;
        #callCaput(pvName, 2+1, 0)
        zebra2.setValue("AND",4,"INP",3, 0)
        #and4_inp[3] = 0;
        #callCaput(pvName, 3+1, 0)
        zebra2.setValue("AND",4,"INP",4, 0)
        
        #out1_ttl    = 34;
        #CAClient.put(zebra2Root+":OUT1_TTL", 34)
        zebra2.setValue("OUT",1,"TTL",-1, 34)
        #out1_nim    = 0;
        #CAClient.put(zebra2Root+":OUT1_NIM", 0)
        zebra2.setValue("OUT",1,"NIM",-1, 0)
        #out1_lvds   = 32;
        #CAClient.put(zebra2Root+":OUT1_LVDS", 32)
        zebra2.setValue("OUT",1,"LVDS",-1, 32)
        
        #out2_ttl    = 0;
        #CAClient.put(zebra2Root+":OUT2_TTL", 0)
        zebra2.setValue("OUT",2,"TTL",-1, 0)
        #out2_nim    = 0;
        #CAClient.put(zebra2Root+":OUT2_NIM", 0)
        zebra2.setValue("OUT",2,"NIM",-1, 0)
        #out2_lvds   = 33;
        #CAClient.put(zebra2Root+":OUT2_LVDS", 33)
        zebra2.setValue("OUT",2,"LVDS",-1, 33)
        
        #out3_ttl    = 0;
        #CAClient.put(zebra2Root+":OUT3_TTL", 0)
        zebra2.setValue("OUT",3,"TTL",-1, 0)
        #out3_oc     = 0;
        #CAClient.put(zebra2Root+":OUT3_OC", 0)
        zebra2.setValue("OUT",3,"OC",-1, 0)
        #out3_lvds   = 0;
        #CAClient.put(zebra2Root+":OUT3_LVDS", 0)
        zebra2.setValue("OUT",3,"LVDS",-1, 0)
        
        #out4_ttl    = 34;
        #CAClient.put(zebra2Root+":OUT4_TTL", 34)
        zebra2.setValue("OUT",4,"TTL",-1, 34)
        #out4_nim    = 0;
        #CAClient.put(zebra2Root+":OUT4_NIM", 0)
        zebra2.setValue("OUT",4,"NIM",-1, 0)
        #out4_pecl   = 0;
        #CAClient.put(zebra2Root+":OUT4_PECL", 0)
        zebra2.setValue("OUT",4,"PECL",-1, 0)
    
    #Set the scan type
    #CAClient.put(zebra2Root+":SCAN_TYPE", mode)
    zebra2.setValue("SCAN",-1,"TYPE",-1, mode)
    print "Finished setting Zebra2 to mode = %s" %mode
    
    
from epics_scripts.pv_scannable_utils import caputStringAsWaveform
from gdascripts.utils import caput, caget
import time
def setZebra2Mode(mode):
    z2_step_scan_cfg_file = "/dls_sw/i12/epics/zebra/default-step-z2.zeb"
    z2_cont_scan_cfg_file = "/dls_sw/i12/epics/zebra/default-continuous-z2.zeb"
    if mode != 1 and mode != 2:
        raise Exception("Bad input Zebra2 mode: "+`mode`)
    
    if mode == 1:   #step scan
        caputStringAsWaveform("BL12I-EA-ZEBRA-02:CONFIG_FILE", z2_step_scan_cfg_file)
        
    if mode == 2:   #continuous scan
        caputStringAsWaveform("BL12I-EA-ZEBRA-02:CONFIG_FILE", z2_cont_scan_cfg_file)
            
    time.sleep(1)
    caput("BL12I-EA-ZEBRA-02:CONFIG_READ.PROC", 1)      # tell z2 to read file
    #caget("BL12I-EA-ZEBRA-02:CONFIG_STATUS")
    print("Finished setting Zebra2 to mode = %s" %(mode))

    
def setZebra3BeforePixiumFlyScan():
    # set IN1 (BL12I-EA-ZEBRA-03:SOFT_IN:B0) to OFF 
    zebra3.setValue("SOFT",-1,"IN:B",0, 0)
    # set IN2 (BL12I-EA-ZEBRA-03:SOFT_IN:B1) to ON
    zebra3.setValue("SOFT",-1,"IN:B",1, 1)

# def setZebra3BeforePixiumFlyScan(divVal):
#     # BL12I-EA-ZEBRA-03:DIV1_DIV to div
#     zebra3.setValue("DIV",1,"DIV",-1, divVal)
#     # set IN1 (BL12I-EA-ZEBRA-03:SOFT_IN:B0) to OFF 
#     zebra3.setValue("SOFT",-1,"IN:B",0, 0)
#     # set IN2 (BL12I-EA-ZEBRA-03:SOFT_IN:B1) to ON
#     zebra3.setValue("SOFT",-1,"IN:B",1, 1)
    
def setZebra3AfterPixiumFlyScan():
    # set IN1 (BL12I-EA-ZEBRA-03:SOFT_IN:B0) to ON 
    zebra3.setValue("SOFT",-1,"IN:B",0, 1)
    # set IN2 (BL12I-EA-ZEBRA-03:SOFT_IN:B1) to OFF
    zebra3.setValue("SOFT",-1,"IN:B",1, 0)



