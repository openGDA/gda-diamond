from gda.jython.commands import GeneralCommands
from gda.epics import CAClient


zebra2Root ="BL12I-EA-ZEBRA-02"

def callCaput(name, index, val):
    name = name %(index)
    pvName = zebra2Root + name
    if CAClient.get(pvName) != val:
        CAClient.put(pvName, val)


def setZebra2Mode(mode):
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
