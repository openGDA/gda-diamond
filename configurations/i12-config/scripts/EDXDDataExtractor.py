'''
Created on 12 May 2010

@author: ssg37927
'''

import os
import string
from gda.jython import InterfaceProvider
from gda.data import NumTracker
from gda.analysis import ScanFileHolder
from gda.analysis.io import NexusLoader

from threading import Thread

class postExtractor(Thread):
    
    def __init__(self,nexusFile,pathname):
        '''
        Constructor
        '''
        Thread.__init__(self)
        self.nexusFileName = nexusFile
        self.pathname = pathname
        return
    
    def run(self):
        print "running extraction"
        self.postExtract(self.nexusFileName,self.pathname)
    
    def postExtract(self,nexusFile,pathname):
        # first make the directorys        
        os.mkdir(pathname)
        print "Made Directory %s" % pathname
            
        sfh = ScanFileHolder()
        sfh.load(NexusLoader(nexusFile)) 
 
        print "loaded data %s" % nexusFile
        for i in range(24) :
            
            print "Element %i" % i          
            # load in only the required data
            #sfh.load(NexusLoader(nexusfile,"EDXD_Element_%02d.data"%i))
            data = sfh.getAxis("EDXD_Element_%02d.data"%i)
            #sfh.load(NexusLoader(nexusfile,"EDXD_Element_%02d.edxd_q"%i))
            q = sfh.getAxis("EDXD_Element_%02d.edxd_q"%i)
            
            try :
                self.write_element(i, pathname, data, q)
            except :
                print "failed to write element %i" % i
        
        return
    
    def write_element(self,elementNumber,pathname, data, q):
        
        i = elementNumber
        
        elementpathname = os.path.join(pathname,"E%02d" % i)
        os.mkdir(elementpathname)
        
        if len(data.getDimensions()) == 2 :                
            for x in range(data.getDimensions()[0]) :
                file = open(os.path.join(elementpathname,"x_%04d"%x),'w')
                lines = []
                for p in range(data.getDimensions()[1]) :
                    lines.append("%.6g  %.6g" % ((q[p]),data[x][p]))
                file.write(string.join(lines,'\n'))
                file.close()
                
        elif len(data.getDimensions()) == 3 :                
            for x in range(data.getDimensions()[0]) :
                for y in range(data.getDimensions()[1]) :
                    file = open(os.path.join(elementpathname,"x_%04d_y_%04d"%(x,y)),'w')
                    lines = []
                    for p in range(data.getDimensions()[2]) :
                        lines.append("%.6g  %.6g" % ((q[p]),data[x][y][p]))
                    file.write(string.join(lines,'\n'))
                    file.close()
                 
        elif len(data.getDimensions()) == 4 :                
            for x in range(data.getDimensions()[0]) :
                for y in range(data.getDimensions()[1]) :
                    for z in range(data.getDimensions()[2]) :
                        file = open(os.path.join(elementpathname,"x_%04d_y_%04d_z_%04d"%(x,y,z)),'w')
                        lines = []
                        for p in range(data.getDimensions()[3]) :
                            lines.append("%.6g  %.6g" % ((q[p]),data[x][y][z][p]))
                        file.write(string.join(lines,'\n'))
                        file.close()


class EDXDDataExtractor(Thread):
    '''
    EDXD Data Extractor
    '''

    def __init__(self):
        '''
        Constructor
        '''
        Thread.__init__(self)
        return
    
    def run(self):
        print "running extraction"
        self.extract()
    
    def extract(self):
        '''
        Extractor method, this takes the location where the extraction should take place, and puts all the data there.
        '''        
        # first make the directorys
        
        # get the current working directory
        i12NumTracker = NumTracker("i12");
        dir = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
        filenumber = i12NumTracker.getCurrentFileNumber();
        pathname = os.path.join(dir,str(filenumber))
        nexusfile = os.path.join(dir,"%d.nxs"%filenumber)
        
        os.mkdir(pathname)
            
        sfh = ScanFileHolder()
        
        for i in range(24) :            
            sfh.load(NexusLoader(nexusfile), ["EDXD_Element_%02d.data"%i, "EDXD_Element_%02d.edxd_q"%i]) 
            data = sfh.getAxis("EDXD_Element_%02d.data"%i)
            q = sfh.getAxis("EDXD_Element_%02d.edxd_q"%i)
            
            self.write_element(i, pathname, data, q)
        
        return
    
    def postExtract(self,nexusFile,pathname):
        # first make the directorys      
        os.mkdir(pathname)
            
        sfh = ScanFileHolder()
        
        for i in range(24) :          
            # load in only the required data
            sfh.load(NexusLoader(nexusFile),"EDXD_Element_%02d.data"%i)
            data = sfh.getAxis("EDXD_Element_%02d.data"%i)
            sfh.load(NexusLoader(nexusFile),"EDXD_Element_%02d.edxd_q"%i)
            q = sfh.getAxis("EDXD_Element_%02d.edxd_q"%i)
            
            try :
                self.write_element(i, pathname, data, q)
            except :
                print "failed to write element %i" % i
        
        return
        
        
    def write_element(self,elementNumber,pathname, data, q):
        
        i = elementNumber
        
        elementpathname = os.path.join(pathname,"E%02d" % i)
        os.mkdir(elementpathname)
        
        if len(data.getDimensions()) == 2 :                
            for x in range(data.getDimensions()[0]) :
                file = open(os.path.join(elementpathname,"x_%04d"%x),'w')
                lines = []
                for p in range(data.getDimensions()[1]) :
                    lines.append("%d  %.6g  %.6g" % (p,(q[p]),data[x][p]))
                file.write(string.join(lines,'\n'))
                file.close()
                
        elif len(data.getDimensions()) == 3 :                
            for x in range(data.getDimensions()[0]) :
                for y in range(data.getDimensions()[1]) :
                    file = open(os.path.join(elementpathname,"x_%04d_y_%04d"%(x,y)),'w')
                    lines = []
                    for p in range(data.getDimensions()[2]) :
                        lines.append("%d  %.6g  %.6g" % (p,(q[p]),data[x][y][p]))
                    file.write(string.join(lines,'\n'))
                    file.close()
                 
        elif len(data.getDimensions()) == 4 :                
            for x in range(data.getDimensions()[0]) :
                for y in range(data.getDimensions()[1]) :
                    for z in range(data.getDimensions()[2]) :
                        file = open(os.path.join(elementpathname,"x_%04d_y_%04d_z_%04d"%(x,y,z)),'w')
                        lines = []
                        for p in range(data.getDimensions()[3]) :
                            lines.append("%d  %.6g  %.6g" % (p,(q[p]),data[x][y][z][p]))
                        file.write(string.join(lines,'\n'))
                        file.close()
                        
                        

from gda.device.scannable import PseudoDevice

class edxd2ascii(PseudoDevice):
    # constructor
    def __init__(self, name):
        self.setName(name) 
        self.setInputNames([])
        self.setExtraNames([])
        self.setOutputFormat([])
        self.running = False

    # returns the value this scannable represents
    def rawGetPosition(self):
        return

    # Does the operation this Scannable represents
    def rawAsynchronousMoveTo(self, new_position):
        return

    # Returns the status of this Scannable
    def rawIsBusy(self):
        return
    
    def atScanStart(self):
        self.running = True
        
    def atScanEnd(self):
        print "Running Conversion to ascii for EDXD nexus"
        extractor = EDXDDataExtractor()
        extractor.start()
        self.running = False
        
    def stop(self):
        if self.running :
            print "Running Conversion to ascii for EDXD nexus on aborted scan"
            extractor = EDXDDataExtractor()
            extractor.start()
