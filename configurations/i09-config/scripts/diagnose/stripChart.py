'''
Created on 26 Sep 2012

@author: fy65
'''
from gda.device.detector import DetectorBase
from gda.device import Detector
from gda.epics import CAClient
from gov.aps.jca.event import MonitorListener
from threading import Timer
import scisoftpy as dnp
from gda.data import NumTracker
from gda.jython import InterfaceProvider
import os
import array

i09NumTracker = NumTracker("i09");
def nextDataFile():
    '''query the absolute path of the next working file'''
    curdir = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    filenumber = i09NumTracker.incrementNumber();
    return os.path.join(curdir,str(filenumber)+".txt")
    
class StripChart(MonitorListener):
    '''
    plot y dataset against x dataset for a fixed length, new data added push oldest data out in the datasets.
    '''

    def __init__(self, xpv, ypv, controlpv, numberofpointstoplot=1000,save=False):
        '''
        Constructor
        '''
        self.xpv=xpv
        self.ypv=ypv
        self.xcli=CAClient(xpv)
        self.ycli=CAClient(ypv)
        self.control=CAClient(controlpv)
        self.x=array.array('d')
        self.y=array.array('d')
        self.plotsize=numberofpointstoplot
        self.isSave=save
        
    def start(self):
        if not self.xcli.isConfigured():
            self.xcli.configure()
        if not self.ycli.isConfigured():
            self.ycli.configure()
        if not self.control.isConfigured():
            self.control.configure()
        self._first=True
        self.xmonitor=self.xcli.camonitor(self)
        self.ymonitor=self.ycli.camonitor(self)
        self.control.caput(1)

    def stop(self):
        self.control.caput(0)
        self.xcli.removeMonitor(self.xmonitor)
        self.ycli.removeMonitor(self.ymonitor)
        if self.xcli.isConfigured():
            self.xcli.clearup()
        if self.ycli.isConfigured():
            self.ycli.clearup()
        if self.control.isConfigured():
            self.control.clearup()
        
    def monitorChanged(self, mevent):
        if self._first:
            self._first=False
            return
        if str(mevent.getSource().getName()).trim()==self.xpv:
            self.x.append(float(mevent.getDBR().getDoubleValue()[0]))
        if str(mevent.getSource().getName()).trim()==self.ypv:
            self.y.append(float(mevent.getDBR().getDoubleValue()[0]))
        if self.x.count() == self.y.count():
            if self.x.count() <= self.plotsize:
                dnp.plot.line(self.x, self.y, "Plot")
            else:
                dnp.plot.plot(self.x[-self.plotsize:], self.y[-self.plotsize:], "Plot")
        
    def writeData(self):
        self.stop()
        self.stattimestamp.removeMonitor(self.timemonitor)
        self.stattotal.removeMonitor(self.countmonitor)
        filename=nextDataFile()
        print "saving data to %s, please wait..." % filename
        #length=min(self.timedata.getData().size, self.countdata.getData().size)
        timedataset=self.timedata.getData()
        countdataset=self.countdata.getData()
        dnp.plot.plot(timedataset, countdataset, "Plot")
        outfile=open(filename,"w")
        for time, count in zip(timedataset.getData().tolist(), countdataset.getData().tolist()):
            outfile.write("%f\t%d\n"% (time, count))
        outfile.close()
        #dnp.io.save(filename, [timedataset, countdataset], format="text") # write 2 text fileseach with one dataset
        print "collection completed."

class EpicsMonitor(MonitorListener):
    def __init__(self, name):
        self.data=[]
        self.name=name
        
    def monitorChanged(self, mevent):
        self.data.append(float(mevent.getDBR().getDoubleValue()[0]))
        
    def getData(self):
        dataset=dnp.asDataset(self.data[1:]) #@UndefinedVariable
        dataset.setName(self.name)
        return dataset

