from gda.factory import Finder

finder = Finder.getInstance()

class TimeResolvedTFG():



    ##############################################################################    
    # hatrx parts old
    ##############################################################################
    #HI     = "1 0 " +     "0.002 0 1 0 0 \n"
    #LO     = "1 0 " +     "0.002 0 0 0 0 \n"
    #LLO    = "1 0 " +     "0.004 0 0 0 0 \n"
    #GAP    = "1 0.002 "+  "0.000005 0 0 0 0 \n"
    #TR_HI  = "1 0 " +     "0.002 0 1 8 0 \n"
    #TR_LO  = "1 0 " +     "0.002 0 0 8 0 \n"
    #TR_LLO = "1 0 " +     "0.004 0 0 8 0 \n"

    #SEQ_END = "-1 \n"
    #SEQ_DEF = "tfg setup-groups sequence 'collect' \n"
    
    #SEQ0 = TR_HI    +GAP    +HI    +GAP    +HI     +LO    +HI           #1110100
    #SEQ1 = TR_HI    +GAP    +HI    +LO     +HI     +LLO   +HI           #1101001
    #SEQ2 = TR_HI    +LO     +HI    +LLO    +HI     +GAP   +HI           #1010011
    #SEQ3 = TR_LO    +HI     +LLO   +HI     +GAP    +HI    +GAP + HI     #0100111
    #SEQ4 = TR_HI    +LLO    +HI    +GAP    +HI     +GAP   +HI           #1001110
    #SEQ5 = TR_LLO   +HI     +GAP   +HI     +GAP    +HI    +LO    +HI    #0011101
    #SEQ6 = TR_LO    +HI     +GAP   +HI     +GAP    +HI    +LO    +HI    #0111010

    #SEQ_FULL = SEQ0 + SEQ1 + SEQ2 + SEQ3 + SEQ4 + SEQ5 + SEQ6
    #SEQ_COMMAND = SEQ_DEF + SEQ_FULL + SEQ_END
    
    ##############################################################################
    # fast hatrx 1 us
    ##############################################################################
    #TR_HI1us = "1 0 0.000001 0 1 8 0 \n"
    #TR_HI2us = "1 0 0.000002 0 1 8 0 \n"
    #TR_HI3us = "1 0 0.000003 0 1 8 0 \n"
    #HI1us = "1 0 0.000001 0 1 0 0 \n"
    #HI2us = "1 0 0.000002 0 1 0 0 \n"
    #HI3us = "1 0 0.000003 0 1 0 0 \n"
    #TR_GAP1us = "1 0 0.000001 0 0 8 0 \n"
    #TR_GAP2us = "1 0 0.000002 0 0 8 0 \n"
    #GAP1us = "1 0 0.000001 0 0 0 0 \n"
    #GAP2us = "1 0 0.000002 0 0 0 0 \n"

    #SEQ0 = "blank"
    #SEQ1 = TR_HI3us   + GAP1us  + HI1us                         #1110100   2 peaks
    #SEQ2 = TR_HI2us   + GAP1us  + HI1us  + GAP2us  + HI1us      #1101001   3 peaks
    #SEQ3 = TR_HI1us   + GAP1us  + HI1us  + GAP2us  + HI2us      #1010011   3 peaks
    #SEQ4 = TR_GAP1us  + HI1us   + GAP2us + HI3us                #0100111   2 peaks
    #SEQ5 = TR_HI1us   + GAP2us  + HI3us                         #1001110   2 peaks
    #SEQ6 = TR_GAP2us  + HI3us   + GAP1us  + HI1us               #0011101   2 peaks
    #SEQ7 = TR_GAP1us  + HI3us   + GAP1us  + HI1us               #0111010   2 peaks

    ##############################################################################    
    # original hatrx 1 us
    ##############################################################################
    HI      = "1 0 " +               "0.000002 0 1 0 0 \n"
    LO      = "1 0 " +               "0.0000014 0 0 0 0 \n"
    LLO     = "1 0 " +               "0.0000026 0 0 0 0 \n"
    GAP     = "1 0 " +               "0.0000002 0 0 0 0 \n"
    TR_HI   = "1 0 " +     "0.000002 0 1 8 0 \n"
    TR_LO   = "1 0 " +     "0.0000012 0 0 8 0 \n"
    TR_LLO  = "1 0 " +     "0.0000024 0 0 8 0 \n"
    GAP_3ms = "1 0 " +               "0.003 0 0 8 0 \n"

    SEQ_END = "-1 \n"
    SEQ_DEF = "tfg setup-groups sequence 'collect' \n"
    
    SEQ0 = SEQ0_single = TR_HI    +GAP    +HI    +GAP    +HI     +LO    +HI                      #1110100
    SEQ1 = SEQ1_single = TR_HI    +GAP    +HI    +LO     +HI     +LLO   +HI                      #1101001
    SEQ2 = SEQ2_single = TR_HI    +LO     +HI    +LLO    +HI     +GAP   +HI                      #1010011
    SEQ3 = SEQ3_single = TR_LO    +HI     +LLO   +HI     +GAP    +HI    +GAP    + HI             #0100111
    SEQ4 = SEQ4_single = TR_HI    +LLO    +HI    +GAP    +HI     +GAP   +HI                      #1001110
    SEQ5 = SEQ5_single = TR_LLO   +HI    +GAP    +HI     +GAP    +HI    +LO     +HI              #0011101
    SEQ6 = SEQ6_single = TR_LO    +HI    +GAP    +HI     +GAP    +HI    +LO     +HI              #0111010
   
    numberSeq = 1
    while numberSeq < 170:
        SEQ0 = SEQ0 + SEQ0_single
        numberSeq = numberSeq +1
    SEQ0 = SEQ0 + GAP_3ms

    numberSeq = 1
    while numberSeq < 170:
        SEQ1 = SEQ1 + SEQ1_single
        numberSeq = numberSeq +1
    SEQ1 = SEQ1 + GAP_3ms

    numberSeq = 1
    while numberSeq < 170:
        SEQ2 = SEQ2 + SEQ2_single
        numberSeq = numberSeq +1
    SEQ2 = SEQ2 + GAP_3ms

    numberSeq = 1
    while numberSeq < 170:
        SEQ3 = SEQ3 + SEQ3_single
        numberSeq = numberSeq +1
    SEQ3 = SEQ3 + GAP_3ms

    numberSeq = 1
    while numberSeq < 170:
        SEQ4 = SEQ4 + SEQ4_single
        numberSeq = numberSeq +1
    SEQ4 = SEQ4 + GAP_3ms

    numberSeq = 1
    while numberSeq < 170:
        SEQ5 = SEQ5 + SEQ5_single
        numberSeq = numberSeq +1
    SEQ5 = SEQ5 + GAP_3ms

    numberSeq = 1
    while numberSeq < 170:
        SEQ6 = SEQ6 + SEQ6_single
        numberSeq = numberSeq +1
    SEQ6 = SEQ6 + GAP_3ms

    SEQ_FULL = SEQ0 + SEQ1 + SEQ2 + SEQ3 + SEQ4 + SEQ5 + SEQ6
    SEQ_COMMAND = SEQ_DEF + SEQ_FULL + SEQ_END

    ##############################################################################
    #single shot, single pulse waveforms
    ##############################################################################
    
    # mircosecond
    SEQ_2us_0usdelay =  "19970 0.00000 0.000002 0 1 8 0 \n" + "1 0 0.003 0 0 8 0 \n" 
    SEQ_2us_10usdelay = "19970 0.00001 0.000002 0 1 8 0 \n" + "1 0 0.003 0 0 8 0 \n"
    SEQ_2us_20usdelay = "19970 0.00002 0.000002 0 1 8 0 \n" + "1 0 0.003 0 0 8 0 \n"
    SEQ_2us_50usdelay = "19970 0.00005 0.000002 0 1 8 0 \n" + "1 0 0.003 0 0 8 0 \n"
    SEQ_2us_90usdelay = "19970 0.00009 0.000002 0 1 8 0 \n" + "1 0 0.003 0 0 8 0 \n"    
    
    # nanosecond
    SEQ_100ns = "19970 0 0.0000001 0 1 8 0 \n" + "1 0 0.003 0 0 8 0 \n"
    SEQ_100ns_1usdelay = "19970 0.00001 0.0000001 0 1 8 0 \n" + "1 0 0.003 0 0 8 0 \n"
    SEQ_100ns_500usdelay = "19970 0.0005 0.0000001 0 1 8 0 \n" + "1 0 0.003 0 0 8 0 \n"

    #Region: Jonathan's Meddling
    
    SEQ_20us_0usdelay = "19970 0 0.00002 0 1 8 0 \n" + "1 0 0.003 0 0 8 0 \n"
    
    #EndRegion
  
    def __init__(self):
        self.tfg = finder.find("tfg")
        self.daserver = finder.find("daserver")
        self.cyc = ""
        self._config()
        
    def _config(self):
        self.daserver.sendCommand("tfg config 'etfg0' tfg2\n")
        
    def _sendSequence(self,sequence=None):
        if sequence == None:
            self.cyc = self.SEQ_COMMAND
        else:
            self.cyc = self.SEQ_DEF + sequence + self.SEQ_END
        self.daserver.sendCommand(self.cyc)
        
    def runSequence(self,sequence=None,numCycles=2000000):
        self._sendSequence(sequence)
        self.daserver.sendCommand("tfg setup-groups cycles %d \n1 collect\n -1 \n" % numCycles)
        self.tfg.start()                  

    def getLastCycle(self):
        return self.cyc
            
    def run(self,numCycles=2000000):
        self.runSequence(self.SEQ_FULL,numCycles)
        
    def status(self):
        return self.daserver.sendCommand("tfg read status")
    
    def stop(self):
        self.tfg.stop()
        return self.status()
        
tfgen = TimeResolvedTFG()
