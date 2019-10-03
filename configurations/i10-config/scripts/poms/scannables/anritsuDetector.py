""" #########################################################################################################
Detector for saving anritsu VNA traces
David Burn - 18/11/16


from poms.scannables.anritsuDetector import anritsuDetector
anritsu = anritsuDetector()
######################################################################################################### """

import time
import socket
import struct
import scisoftpy as dnp

from java.lang import Thread, Runnable
from gda.jython import InterfaceProvider
from gda.data import NumTracker
from gda.jython import InterfaceProvider
from gda.device.detector import DetectorBase




class anritsuDetector(DetectorBase):
    def __init__(self, host="172.23.110.209"):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, 5001))
        self.sock.send(str.encode("*IDN?\n"))
        print self.sock.recv(2056)

        self.bandwidth = None
        self.setup()

        self.setName("anritsu")
        
        self.setInputNames(['collectionTime'])
        self.setExtraNames([])
        self.setOutputFormat(["%s"])
        
        self.filename = ""
        
        #self.setInputNames([])
        #self.setExtraNames(["anritsu"])
        #self.setOutputFormat(["%d"])
        self.isCollecting = 0 

        self.myData = 0
        self.pointNum = 0

    def collectData(self):
        mythread = Thread(collectDataThread(self))
        mythread.start()

    def getStatus(self):
        return self.isCollecting

    def readout(self):
        return self.filename

    def getDataDimensions(self):
        return 1

    def createsOwnFiles(self):
        return True

    def atScanStart(self):
        pass

    def atPointStart(self):
        pass

    def stop(self):
        self.loop = False

    def writeDataToFile(self, data=[]):
        path = str(InterfaceProvider.getPathConstructor().createFromDefaultProperty())+"/anritsu/"
        if not os.path.exists(path): os.makedirs(path)

        filenumber = NumTracker("i10").getCurrentFileNumber();
        filename = "i10-%06d-%s_%04d.dat"   % (filenumber, self.getName(), self.pointNum)
        print "writing file: " + path + filename
        
        datafile=open(path + filename, 'w')

        data = dnp.array(data,  dtype=dnp.float)
        data = dnp.transpose(data)
        datafile.write(" &END\n")
        datafile.write("freq\ts12\ts21\ts11\ts22"'\n')

        for line in data:
            s = "".join("%10.5g\t" % x for x in line[0])
            datafile.write(s+'\n')
        datafile.flush()
        datafile.close()
        return path+filename

    def query(self, message):
        self.sock.send(str.encode(message+"\n"))
        return self.sock.recv(2056)

    def write(self, message):
        self.sock.send(str.encode(message+"\n"))

    def setup(self):
        """ display layout settings """
        self.write("CALCulate1:PARameter1:DEFine S11")
        self.write("CALCulate1:PARameter1:FORMat MLOGarithmic")

        self.write("CALCulate1:PARameter2:DEFine S21")
        self.write("CALCulate1:PARameter2:FORMat MLOGarithmic")

        self.write("CALCulate1:PARameter3:DEFine S22")
        self.write("CALCulate1:PARameter3:FORMat MLOGarithmic")

        self.write("CALCulate1:PARameter4:DEFine S12")
        self.write("CALCulate1:PARameter4:FORMat MLOGarithmic")

        self.write("SENSe:HOLD:FUNCtion HOLD")        # single sweep and hold

        """ data transfer settings """
        self.write(":FORMat:DATA REAL")                # ASC, REAL or REAL32
        #self.write(":FORMat:BORDer SWAP")            # MSB/LSB: Normal or Swapped
        self.write(":FORMat:BORDer Normal")            # MSB/LSB: Normal or Swapped


        self.setFrequency(0.1,8)
        self.setNumPoints(512)
        self.setBandwidth(5000) 

    def getTrace(self, par):
        # floating point with 8 bytes / 64 bits per number
        #self.write("SYST:ERR:CLE")
        #print self.query("*OPC?")

        #print self.query("SYST:ERR?")                #returns "No Error"

        self.write(":CALC:PAR%1d:DATA:SDAT?" % par)
        head =  self.sock.recv(2)                       # header part 1
        head =  self.sock.recv(int(head[1]))            # header part 2
        MSGLEN = int(head)            # extrace message len from header

        chunks = []
        bytes_recd = 0
        while bytes_recd < MSGLEN:
            chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        data = ''.join(chunks)

        extra = self.sock.recv(2048)
        #print len(extra)
        #print chr(extra)

        #print len(data), " bytes, ", len(data)/8, " numbers"

        num = len(data) / 8
        [data,] = struct.unpack('%dd' % num, data),
        
        #return [np.array(data[::2]), np.array(data[1::2]) ]
        return  dnp.array(data[::2])   + dnp.array(data[1::2])*1j

    def getFrequency(self):
        self.write("SYST:ERR:CLE")
        self.write(":SENSe:FREQuency:DATA?")
        head =  self.sock.recv(2)                # header part 1
        head =  self.sock.recv(int(head[1]))            # header part 2
        MSGLEN = int(head)            # extrace message len from header

        chunks = []
        bytes_recd = 0
        while bytes_recd < MSGLEN:
            chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        data = ''.join(chunks)

        #print len(data), " bytes, ", len(data)/8, " numbers"
        extra = self.sock.recv(2048)

        num = len(data) / 8
        [data,] = struct.unpack('%dd' % num, data),
        return dnp.array(data)/1e9

    def doSweep(self):
        self.write("SYST:ERR:CLE")
        opc = self.query("*OPC?")
        print "opc ", opc

        self.write("TRIG:SING")
        # there is a wait here until anritsu has finished collecting
        err = self.query("SYST:ERR?")
        print "err ", err

    def setFrequency(self, start, stop):
        """ frequency settings """
        start = start*1.0e9
        stop = stop*1.0e9
        self.write("SENS:FREQ:STAR %d" % start)
        self.write("SENS:FREQ:STOP %d" % stop)

    def setBandwidth(self,bandwidth):
        self.bandwidth = bandwidth
        self.write("SENS:BAND %6d" % bandwidth)                # IFBW Frequency (Hz)

    def setNumPoints(self,num):
        self.write("SENS:SWEEP:POINT %4d" % num)

########################################################################################################
########################################################################################################
########################################################################################################
class collectDataThread(Runnable):
    def __init__(self, theDetector):
        self.myDetector = theDetector

    def run(self):
        self.myDetector.isCollecting = 1

        self.myDetector.doSweep()
        freq = self.myDetector.getFrequency()
        s21= self.myDetector.getTrace(2)
        s12= self.myDetector.getTrace(4)
        
        self.myDetector.filename = self.myDetector.writeDataToFile([freq, s12, s21])

        self.myDetector.isCollecting = 0

########################################################################################################
########################################################################################################
########################################################################################################


