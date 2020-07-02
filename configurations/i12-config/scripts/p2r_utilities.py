import os
import csv
import time
from gda.jython.commands import GeneralCommands
from gda.jython.commands import ScannableCommands
from i12utilities import wd, pwd, nwd, nfn, cfn, getVisit
from gdascripts.metadata.metadata_commands import setTitle, getTitle
import i13tomographyScan


from gda.factory import Finder
p2r_rot=Finder.find("p2r_rot")

def flyp2r(title, inBeamPosition, outOfBeamPosition, exposureTime=1., start=0., stop=180., step=0.1, imagesPerDark=20, imagesPerFlat=20, speedForRewind=180.0):
    """
    Function to perform a tomography FLY SCAN with p2r rotation rig. 
    Arguments:
    title - description of the scan or the sample that is being scanned. This is generally user-specific information that may be used to map to this scan later and is available in the NeXus file)
    inBeamPosition - position of X drive to move sample into the beam to take a projection
    outOfBeamPosition - position of X drive to move sample out of the beam to take a flat field image
    exposureTime - exposure time in seconds (default = 1.0)
    start - first rotation angle (default=0.0)
    stop  - last rotation angle (default=180.0)
    step - rotation step size (default = 0.1)
    imagesPerDark - number of images to be taken for each dark-field sub-sequence (default=20)
    imagesPerFlat - number of images to be taken for each flat-field sub-sequence (default=20)
    
    General scan sequence is: D, F, P,..., P
    where D stands for dark field, F - for flat field, and P - for projection.
    speedForRewind - speed to be temporarily used by p2r to go back to start angle (this speed is re-set to original value before scan is executed.
    """
    
    print("Starting flyp2r scan with arguments:")
    
    scanfile=nwd()
    scanfile += ".nxs"
    print "Scan file will be: %s"%scanfile
    
    print("title = " + title)
    print("inBeamPosition = " + `inBeamPosition`)
    print("outOfBeamPosition = " + `outOfBeamPosition`)
    print("exposureTime = " + `exposureTime`)
    print("start angle = " + `start`)
    print("stop angle = " + `stop`)
    print("step angle = " + `step`)
    print("imagesPerDark = " + `imagesPerDark`)
    print("imagesPerFlat = " + `imagesPerFlat`)
    print("speed for rewinding = " + `speedForRewind`)
    
    speedBefore = p2r_rot.getSpeed()
    print("speed before = " + `speedBefore`)
    
    print("About to set p2r_rot speed to temporary rewind speed:" + `speedForRewind`)
    p2r_rot.setSpeed(speedForRewind)
    print("Finished setting p2r_rot speed to temporary rewind speed:" + `speedForRewind`)
    
    speedUserModified1 = p2r_rot.getSpeed()
    print("p2r_rot speed after setting it to temporary rewind speed:" + `speedUserModified1`)
    
    print("About to set p2r_rot rotation angle to:" + `start` + " (with temporary rewind speed = "+`speedUserModified1`+")")
    p2r_rot.moveTo(start)
    print("Finished setting p2r_rot rotation angle to:" + `start`)
    
    posBeforeScan = p2r_rot.getPosition()
    print("p2r_rot rotation angle after setting it to start angle:" + `posBeforeScan`)
    
    print("About to re-set p2r_rot speed to original value:" + `speedBefore`)
    p2r_rot.setSpeed(speedBefore)
    print("Finished re-setting p2r_rot speed to original value:" + `speedBefore`)
    
    speedUserModified2 = p2r_rot.getSpeed()
    print("p2r_rot speed after re-setting it to original value:" + `speedUserModified2`)
    
    print("About to run tomoFlyScan...")
#    clear_defaults()
    setTitle(title)
    #tomoFlyScan(inBeamPosition, outOfBeamPosition, exposureTime=1, start=0., stop=180., step=0.1, darkFieldInterval=0., flatFieldInterval=0.,
    #          imagesPerDark=20, imagesPerFlat=20, min_i=-1., setupForAlignment=True, beamline="I13")
    
    i13tomographyScan.tomoFlyScan(inBeamPosition=inBeamPosition,outOfBeamPosition=outOfBeamPosition, exposureTime=exposureTime, start=start, stop=stop, step=step, imagesPerDark=imagesPerDark, imagesPerFlat=imagesPerFlat, beamline="I12")
    setTitle("undefined")
    print("Finished tomoFlyScan.")
    
    scanfile=pwd()
    print "Scan file was: %s"%scanfile

    print("Finished flyp2r scan")

def stepp2r(title, inBeamPosition, outOfBeamPosition, exposureTime=1., start=0., stop=180., step=0.1, darkFieldInterval=0, flatFieldInterval=0, imagesPerDark=20, imagesPerFlat=20, speedForRewind=180.0):
    """
    Function to perform a tomography STEP SCAN with p2r rotation rig. 
    Arguments:
    title - description of the scan or the sample that is being scanned. This is generally user-specific information that may be used to map to this scan later and is available in the NeXus file)
    inBeamPosition - position of X drive to move sample into the beam to take a projection
    outOfBeamPosition - position of X drive to move sample out of the beam to take a flat field image
    exposureTime - exposure time in seconds (default = 1.0)
    start - first rotation angle (default=0.0)
    stop  - last rotation angle (default=180.0)
    step - rotation step size (default = 0.1)
    darkFieldInterval - number of projections between each dark-field sub-sequence. NOTE: at least 1 dark is ALWAYS taken both at the start and end of a tomogram (default=0: use this value if you DON'T want to take any darks between projections)
    flatFieldInterval - number of projections between each flat-field sub-sequence. NOTE: at least 1 flat is ALWAYS taken both at the start and end of a tomogram (default=0: use this value if you DON'T want to take any flats between projections)
    imagesPerDark - number of images to be taken for each dark-field sub-sequence (default=20)
    imagesPerFlat - number of images to be taken for each flat-field sub-sequence (default=20)
    
    General scan sequence is: D, F, P,..., P, F, D
    where D stands for dark field, F - for flat field, and P - for projection.
    speedForRewind - speed to be temporarily used by p2r to go back to start angle (this speed is re-set to original value before scan is executed.
    """
    
    print("Starting stepp2r scan with arguments:")
    
    scanfolder=nwd()
    print "Scan folder will be: %s"%scanfolder
    
    print("title = " + title)
    print("inBeamPosition = " + `inBeamPosition`)
    print("outOfBeamPosition = " + `outOfBeamPosition`)
    print("exposureTime = " + `exposureTime`)
    print("start angle = " + `start`)
    print("stop angle = " + `stop`)
    print("step angle = " + `step`)
    print("darkFieldInterval = " + `darkFieldInterval`)
    print("flatFieldInterval = " + `flatFieldInterval`)
    print("imagesPerDark = " + `imagesPerDark`)
    print("imagesPerFlat = " + `imagesPerFlat`)
    print("speed for rewinding = " + `speedForRewind`)
    
    speedBefore = p2r_rot.getSpeed()
    print("speed before = " + `speedBefore`)
    
    print("About to set p2r_rot speed to temporary rewind speed:" + `speedForRewind`)
    p2r_rot.setSpeed(speedForRewind)
    print("Finished setting p2r_rot speed to temporary rewind speed:" + `speedForRewind`)
    
    speedUserModified1 = p2r_rot.getSpeed()
    print("p2r_rot speed after setting it to temporary rewind speed:" + `speedUserModified1`)
    
    print("About to set p2r_rot rotation angle to:" + `start`+ " (with temporary rewind speed = "+`speedUserModified1`+")")
    p2r_rot.moveTo(start)
    print("Finished setting p2r_rot rotation angle to:" + `start`)
    
    posBeforeScan = p2r_rot.getPosition()
    print("p2r_rot rotation angle after setting it to start angle:" + `posBeforeScan`)
    
    print("About to re-set p2r_rot speed to original value:" + `speedBefore`)
    p2r_rot.setSpeed(speedBefore)
    print("Finished re-setting p2r_rot speed to original value:" + `speedBefore`)
    
    speedUserModified2 = p2r_rot.getSpeed()
    print("p2r_rot speed after re-setting it to original value:" + `speedUserModified2`)
    
    print("About to run tomoScan...")
#    for s in _default_scannables_i12:
#        add_default(s)
    
    #tomoScan(description, inBeamPosition, outOfBeamPosition, exposureTime=1.0, start=0.0, stop=180.0, step=0.1, darkFieldInterval=0, flatFieldInterval=0, imagesPerDark=10, imagesPerFlat=10, optimizeBeamInterval=0, pattern='default', tomoRotationAxis=0, addNXEntry=True, autoAnalyse=True, additionalScannables=[])
    tomoScan(description=title,inBeamPosition=inBeamPosition,outOfBeamPosition=outOfBeamPosition, exposureTime=exposureTime, start=start, stop=stop, step=step, darkFieldInterval=darkFieldInterval, flatFieldInterval=flatFieldInterval, imagesPerDark=imagesPerDark, imagesPerFlat=imagesPerFlat)
    print("Finished tomoScan.")
    setTitle("undefined")
    
    scanfolder=pwd()
    print "Scan folder was: %s"%scanfolder
    
    print("Finished stepp2r scan")


class p2r_telnet_connection():
    def __init__(self, connectable):
        try:
            connectable.motor.smc.bidiAsciiCommunicator
            self.connectable = connectable  # round brackets, ie (), at end are undesired
        except Exception, e:
            self.connectable = None
            msg = "Failed to access input connectable's motor.smc.bidiAsciiCommunicator: %s" %(str(e))
            print(msg)
    
    def close(self):
        self.connectable.motor.smc.bidiAsciiCommunicator.closeConnection()
    
    def reset(self, nattempts=4, wait_sec=1):
        self.close()
        time.sleep(wait_sec)
        attempts = 0
        for i in range(nattempts):
            try:
                self.connectable()  # round brackets, ie (), at end are necessary
                break
            except:
                attempts += 1
        return attempts, (attempts<nattempts)
    
    def get_address(self):
        out = None
        try:
            out = self.connectable.motor.smc.bidiAsciiCommunicator.getAddress()
        except Exception, e:
            msg = "Failed to get telnet connection address: %s" %(str(e))
            print(msg)
        return out
    
    def set_address(self, address):
        try:
            self.connectable.motor.smc.bidiAsciiCommunicator.setAddress(address)
        except Exception, e:
            msg = "Failed to set telnet connection address: %s" %(str(e))
            print(msg)
    
    def get_port(self):
        out = None
        try:
            out = self.connectable.motor.smc.bidiAsciiCommunicator.getPort()
        except Exception, e:
            msg = "Failed to get telnet connection port: %s" %(str(e))
            print(msg)
        return out
    
    def set_port(self, port):
        try:
            self.connectable.motor.smc.bidiAsciiCommunicator.setPort(port)
        except Exception, e:
            msg = "Failed to set telnet connection port: %s" %(str(e))
            print(msg)
    
    def get_timeout_ms(self):
        out = None
        try:
            out = self.connectable.motor.smc.bidiAsciiCommunicator.getTimeout()
        except Exception, e:
            msg = "Failed to get telnet connection timeout: %s" %(str(e))
            print(msg)
        return out
    
    def set_timeout_ms(self, timeout):
        try:
            self.connectable.motor.smc.bidiAsciiCommunicator.setTimeout(timeout)
        except Exception, e:
            msg = "Failed to set telnet connection timeout: %s" %(str(e))
            print(msg)
    
    def send_cmd_no_reply(self, cmd):
        try:
            self.connectable.motor.smc.bidiAsciiCommunicator.sendCmdNoReply(cmd)
        except Exception, e:
            msg = "Failed to send cmd: %s" %(str(e))
            print(msg)
    
    def send(self, cmd):
        try:
            reply_str = self.connectable.motor.smc.bidiAsciiCommunicator.send(cmd)
        except Exception, e:
            msg = "Failed to send cmd: %s" %(str(e))
            print(msg)
        return reply_str

class csv_column(object):
    def __init__(self, outdir, outfile, is_time_stamped):
        self.outdir = outdir
        self.outfile = outfile
        self.items = []
        self.is_time_stamped = is_time_stamped
    
    def _get_outdirpath(self):
        visitid = getVisit().replace("-", "_")
        return os.path.join(self.outdir, visitid)
    
    def _get_outfilepath(self):
        outdir = self._get_outdirpath()
        return os.path.join(self._get_outdirpath(), self.outfile)
    
    def add_item(self, item):
        self.items.append(item)
    
    def add_items(self, items):
        for v in items:
            self.add_item(v)
    
    def rm_item(self, item):
        self.items.remove(item)
    
    def rm_item(self, items):
        for v in items:
            self.rm_item(v)
    
    def report_items(self):
        return self.items
    
    def write_csv(self, nitems=None):
        outsuffix = ".csv"
        outdir = self._get_outdirpath()
        outfile = self._get_outfilepath()
        # create dirs, if they don't already exist
        try:
            os.makedirs(outdir)
        except OSError, e:
            if not os.path.isdir(outdir):
                msg = "Output location %s is not a directory: " %(outdir)
                raise ValueError(msg + str(e))
        if not nitems is None:
            n = min(nitems, len(self.items))
        else:
            n = len(self.items)
        if self.is_time_stamped:
            timestr = time.strftime("%d_%m_%Y-%H%M%S")
            outfile += "_"+timestr
        outfile += outsuffix
        fh = open(outfile, 'wb')
        try:
            wrt = csv.writer(fh)
            for v in self.items[:n]:
                wrt.writerow([v])
            msg = "Wrote %i item(s) to output file %s" %(n, outfile)
            print(msg)
        except Exception, e:
            msg = "Failed to write %i item(s) to output file %s: " %(n, outfile)
            print(msg + str(e))
            raise Exception(msg)
        finally:
            fh.close()
    
    def read_csv(self, inpath, nitems=None, overwrite=True):
        if os.path.isfile(inpath) and os.access(inpath, os.R_OK):
            fh = open(inpath, 'rU')
            try:
                rdr = csv.reader(fh)
                _items_read = [float(sv[0]) for sv in list(rdr) if sv]
                len_tot = len(_items_read)
                if not nitems is None:
                    n = min(nitems, len_tot)
                else:
                    n = len_tot
                _items_used = []
                for i in range(n):
                    _items_used.append(_items_read[i])
                if overwrite:
                    self.items = _items_used
                else:
                    self.items.extend(_items_used)
                msg = "Read %i (of available %i) item(s) from input file %s" %(i+1, len_tot, inpath)
                print(msg)
            except Exception, e:
                msg = "Failed to read item(s) from input file %s: " %(inpath)
                print(msg + str(e))
                raise Exception(msg + str(e))
            finally:
                fh.close()
        else: 
            msg = "Input file %s does not exist or is not readable!" %(inpath)
            print(msg)
        
class p2r_triggers(csv_column):
    def __init__(self, outdir="/dls_sw/i12/scripts/users/p2r/", outfile="p2r_triggers", is_time_stamped=True):
        super(p2r_triggers, self).__init__(outdir, outfile, is_time_stamped)
    
    
    
p2r_telnet = p2r_telnet_connection(p2r_rot)
