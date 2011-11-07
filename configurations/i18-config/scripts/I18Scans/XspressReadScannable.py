from gda.device.scannable import ScannableBase
from gdascripts.messages import handle_messages 
import sys
import time

class XspressReadScannable(ScannableBase):
    
    def __init__(self, name, delegate):
        self.delegate = delegate
        self.name = name
        self.das=finder.find("daserver")
        self.outputNames = ["total", "resets","windows"]
        self.outputFormat = ['%.3f','%.3f','%.3f']
        
    def asynchronousMoveTo(self, position):
        pass
    
    def getPosition(self):
        return self.readScalarData( self.delegate.getCurrentFrame())
    
    def isBusy(self):
        return self.delegate.isBusy()
    
    def stop(self):
        self.delegate.stop()
        
    def readScalarDataNoRetry(self,point):
        global error
        scalarData=[]
        scalarstring=''
        command = "read 0 0 %d 3 9 1 from 1" % (point)
        scalarString=self.das.getData(command)
        for t in range(10):
            if scalarString =="" :
                print str(t),"reading scaler from memory "
                time.sleep(1)
                scalarString=self.das.getData(command)
            else:
                break           
       
        try:
            for j in range(3):
                 scalarData.append(range(9))
            k=0
            for i in range(9):
                for j in range(3):
                    scalarData[j][i]=int(scalarString[k])
                    k=k+1
            return scalarData
        except:
            etype, exception, traceback = sys.exc_info()
            self.readError = self.readError + 1
            self.readErrorList.append(point)
            handle_messages.log(None,"Error in readScalarDataNoRetry - scalarString = " + `scalarString` + " readErrorList = " + `self.readErrorList`, etype, exception, None, True)
            raise exception,None,traceback
            

    def readScalarData(self,point):
        data = None
        #timeout = self.das.getSocketTimeOut()
        try:
            #self.das.setSocketTimeOut(10)
            #for i in range(20):
             #   self.readScalarDataNoRetry(point)
             #   thread.start_new_thread(self.readScalarDataNoRetry, (point,))
            data = self.readScalarDataNoRetry(point)
            #self.das.setSocketTimeOut(timeout)
        except:
            etype, exception, traceback = sys.exc_info()
            handle_messages.log(None,"Error in readScalarData - retrying", etype, exception, traceback, False)
        #retry once
        #self.das.setSocketTimeOut(timeout)
        if(data == None):
            try:
                data =  self.readScalarDataNoRetry(point)
            except:
                etype, exception, traceback = sys.exc_info()
                handle_messages.log(None,"Error in readScalarData - Giving up after 4 retries, returning zeroes", etype, exception, traceback, False)
                scalarData=[]
                for j in range(3):
                    scalarData.append(range(9))
                for i in range(9):
                    for j in range(3):
                        scalarData[j][i]=0                    
                return scalarData
        else:
            return data