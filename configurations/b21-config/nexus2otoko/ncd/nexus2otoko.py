'''
converter of nexus files with daresbury style detectors recorded in them to 
the legacy otoko/bsl format

Ideally additional scannables found in the data are recorded as calibration data 
'''
import datetime
import re
import os
import sys
import numpy, nxs
import logging

LOG_FILENAME = '/dls_sw/b21/logs/nexus2otoko.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

class DetInfo:
    def __init__(self, path, dimensions):
        self.path = path
        self.dimensions = dimensions[0].tolist()
    
class nexus2otoko:
    def __init__(self, nexusname):
        self.logger = logging
        self.detdict = {}
        self.det2fileno = { "SAXS": 1, "CALIB": 2, "WAXS": 3, "TIMES": 4}

	self.logger.info(  "looking at "+nexusname+" "+datetime.datetime.now().__str__() )

        self.nexusname = nexusname
        self.nexusfile = nxs.open(self.nexusname)
                
        self.instrumentname = "DLS"
        self.inspectfile()

	self.iscommissioningvisit = False
	self.isindlsdata = False
	
	components = self.nexusname.split("/")
	if len(components) > 6:
		if "dls" == components[1]:
			if "data" == components[3]:
				try: 
					int(components[4])
					# is int
					self.isindlsdata = True
					self.logger.debug(  "is in dls data" )
					if components[5].startswith("cm"):
						self.iscommissioningvisit = True
						self.logger.debug(  "is commissioning" )
				except:
					#not in year dir
					self.logger.debug(  "no int year" )
					pass
		
    def parseISOdate(self, datestr):
        ## std python does not handle timezone parsing in any way
        datestr=datestr[0:-6]
        dt=datetime.datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%S")
        return dt
    
    def inspectfile(self):
        self.filetime = self.nexusfile.getattrs()["file_time"]
        self.filetime = self.parseISOdate(self.filetime)
        entries = self.nexusfile.getentries()
        if len(entries) != 1:
            self.logger.warning("unexpected number of root entries, reading first one only")
        self.nexusfile.opengroup(entries.keys()[0])
        entries = self.nexusfile.getentries()
        if not "scan_dimensions" in entries:
            raise RuntimeError("scan dimensions missing")
        self.nexusfile.opendata("scan_dimensions")
        self.scandimensions = self.nexusfile.getdata()
        if isinstance(self.scandimensions, numpy.ndarray):
            self.scandimensions = self.scandimensions.tolist()
        else:
            self.scandimensions = [ self.scandimensions ]
        #print self.scandimensions, type(self.scandimensions)
        self.nexusfile.closedata()
        self.title=""
        for i in ["title", "scan_command"]:
            if i in entries:
                self.nexusfile.opendata(i)
                self.title = self.nexusfile.getdata()
                self.nexusfile.closedata()
                break
        self.nexusfile.opengroup("instrument")
        entries = self.nexusfile.getentries()
        for entry in entries:
            if entries.get(entry) == "NXdetector":
                self.nexusfile.opengroup(entry)
                detentries = self.nexusfile.getentries()
                if "sas_type" in detentries.keys():
                    self.nexusfile.opendata("sas_type")
                    dettype=self.nexusfile.getdata()
                    #print "sas detector "+entry+"("+dettype+")"
                    self.nexusfile.closedata()
                    self.nexusfile.opendata("data")
                    detdatainfo=self.nexusfile.getinfo()
                    #print "sas detector "+entry+"("+dettype+")"
                    self.nexusfile.closedata()
                    self.detdict[dettype] = DetInfo(self.nexusfile.path, detdatainfo)
                self.nexusfile.closegroup()
            elif entry == "name":
                self.nexusfile.opendata(entry)
                self.instrumentname = self.instrumentname + "-" + self.nexusfile.getdata()
                self.nexusfile.closedata()
        self.canbeconverted = 0
        for i in ["SAXS","CALIB","WAXS"]:
            if i in self.detdict.keys():
                self.canbeconverted = 1
                break          

    def writeout(self):
        if self.canbeconverted:
            self.genoutfileinfo()
            headerfilename = self.filebase % 0
            self.logger.info( "header file name "+headerfilename )
            self.logger.info( "header file dir "+os.path.dirname(headerfilename ))
            try:
            	os.makedirs(os.path.dirname(headerfilename))
            except Exception as e:
            	self.logger.error("error creating directory: "+e.__str__())
            headerfile = open(headerfilename, "w")
            headerdate = self.filetime.strftime("%A %d/%m/%y at %H:%M:%S")
            headerfile.write("Created at %s on %s\r\n" % (self.instrumentname, headerdate))
            headerfile.write(self.title+"\r\n")
            for det in ["SAXS", "CALIB", "WAXS", "TIMES"]:
                if not det in self.detdict:
                    continue
                detinfo = self.detdict.get(det)
                detdims = (len(detinfo.dimensions) - len(self.scandimensions) - 1)
                self.logger.debug(  det + detdims.__str__() + detinfo.dimensions.__str__() + detinfo.path.__str__() )
                frames = 1
                puredims = []
                for i in range(len(detinfo.dimensions)):
                    if i < len(self.scandimensions):
                        if self.scandimensions[i] != detinfo.dimensions[i]:
                            self.logger.warn("dimensions mismatch for %s: dimension %d has %d from scan and %d for detector" % (det, i, self.scandimensions[i], detinfo.dimensions[i]))
                        frames *= detinfo.dimensions[i]
                    elif i == len(self.scandimensions):
                        frames *= detinfo.dimensions[i]
                    else:
                        puredims.insert(0, detinfo.dimensions[i])
                detfilename = self.filebase % self.det2fileno.get(det)
                fmt=""
                endian=1
                for i in range(10):
                    fmt=fmt+" % 7d"
                fmt=fmt[1:]+"\r\n"
                filler=[0,0,0,0,0,1]
                if det == "TIMES":
                    filler[-1] = 0
                if det in [ "TIMES", "CALIB" ]:
                    reversedims = True
                    headerdims = [ frames ] + list(puredims)
                else:
                    reversedims = False
                    headerdims = list(puredims)
                    headerdims.append(frames)
                if len(headerdims) == 2:
                    headerdims.append(1)
                headerfile.write(fmt % tuple(headerdims + [ endian ] + filler))
                headerfile.write(os.path.basename(detfilename)+"\r\n")
                     
                self.logger.debug(  frames.__str__() + " Frames " + puredims.__str__() )
                if not reversedims:
                    self.writedet(detinfo, frames, puredims, detfilename)
                else:
                    self.writereversedet(detinfo, frames, puredims, detfilename)
            headerfile.close()
            self.logger.info( "done converting ")
        else:
            self.logger.info( "no ncd detectors recognised" )
            
    def writedet(self, detinfo, frames, puredims, filename):
        file = open(filename, "w")
        self.nexusfile.openpath(detinfo.path)
        self.nexusfile.opendata("data")
        offset = []
        shape = []
        scandim = 0
        for i in range(len(detinfo.dimensions)):
            offset.append(0)
            if i < len(detinfo.dimensions) - len(puredims):
                shape.append(1)
                scandim += 1
            else:
                shape.append(detinfo.dimensions[i]) 
        self.logger.debug( offset.__str__() + shape.__str__() )
        while True:
            self.logger.debug( "getslab " + offset.__str__() )
            slab = self.nexusfile.getslab(offset, shape)
            file.write(slab.astype(numpy.float32).tostring())
            cur=scandim-1
            while cur>=0:
                offset[cur] += 1
                if cur>0 and offset[cur] == detinfo.dimensions[cur]: 
                    offset[cur] = 0
                    cur -= 1
                    continue
                break
            if offset[0]==detinfo.dimensions[0]:
                break
        self.nexusfile.closedata()
        file.close()
        
    def writereversedet(self, detinfo, frames, puredims, filename):
        if not len(puredims):
            raise RuntimeError("multidimensional calibration detectors not supported")
        file = open(filename, "w")
        self.nexusfile.openpath(detinfo.path)
        self.nexusfile.opendata("data")
        offset = []
        for i in range(len(detinfo.dimensions)):
            offset.append(0)
        shape = list(detinfo.dimensions)
        shape[-1] = 1
        self.logger.debug( offset.__str__() + shape.__str__() )
        for i in range(detinfo.dimensions[-1]):
            offset[-1] = i
            self.logger.debug( "getslab " + offset.__str__() )
            slab = self.nexusfile.getslab(offset, shape)
            file.write(slab.astype(numpy.float32).tostring())
        self.nexusfile.closedata()
        file.close()
        
    def genoutfileinfo(self):
        nexusbasename = os.path.basename(self.nexusname)
        [ nexusbase, ext ] = os.path.splitext(self.nexusname)
        if ext != ".nxs":
            raise RuntimeError("no nexus extension")
	comps = nexusbase.split("/")
	if self.isindlsdata:
		comps.insert(6,"bsl")
		self.logger.debug( "bsl inserted" )
	otokodir = "/".join(comps)
	self.logger.debug( "otokodir is %s" % otokodir )

        [ scanname, ext ] = os.path.splitext(nexusbasename)
	# remove first hyphen, should be beamline name
	scanname = scanname.split("-",1)[-1]
        scannumber = "".join(re.findall("[0-9]", scanname))
        scannumber = int(scannumber)
        
        otokonumber = scannumber % 100
        otokoletter = ( scannumber / 100 ) % 26
        otokoletter = chr(ord("A") + otokoletter)
        
        otokodate = "%X%02d" % ( self.filetime.month, self.filetime.day )
        
        self.filebase = "%s/%c%02d%%003d.%s" % (otokodir, otokoletter, otokonumber, otokodate)
                
if __name__ == '__main__':
	for file in sys.argv[1:]:
		try:
			n2o=nexus2otoko(file)
			if not n2o.iscommissioningvisit:
				n2o.writeout()
		except Exception as e:
			logging.error("exception treating "+file+": "+e.__str__())


