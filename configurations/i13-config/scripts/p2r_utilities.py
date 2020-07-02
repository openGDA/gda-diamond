import os
import csv
import time
from gda.jython.commands import GeneralCommands
from gda.jython.commands import ScannableCommands

from gda.factory import Finder
p2r_rot=Finder.find("p2r_rot")

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
    def __init__(self, outdir="/dls_sw/i13/scripts/users/p2r/", outfile="p2r_triggers", is_time_stamped=True):
        super(p2r_triggers, self).__init__(outdir, outfile, is_time_stamped)
    
    
    
p2r_telnet = p2r_telnet_connection(p2r_rot)
    
