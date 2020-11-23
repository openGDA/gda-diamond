import sys
import re
from gdascripts.messages import handle_messages
from gda.device.scannable import ScannableBase
from gda.device import DeviceException
from gda.factory import Finder
from gda.io.socket import SocketBidiAsciiCommunicator
class leem2000:
    def __init__(self):
        self.comms_started=False
        try:
            self.leem_com=(Finder.find("leem2000_objects")).get("leem2000_com")
            self.leem_com.setReplyTerm('\0')
            self.leem_com.setCmdTerm('\0')
        except:
            exceptionType, exception, traceback=sys.exc_info();
            handle_messages.log(None, "Error getting leem2000_com from leem2000_objects", exceptionType, exception, traceback, True)

    def close(self):
        """
        Function to close the connection to LEEM2000 gracefully
        If this is not done before closing the telnet connection
        LEEM2000 will not allow future connections.
        """
        if self.comms_started:
            self.comms_started=False
            self.leem_com.sendCmdNoReply("clo")
            self.leem_com.closeConnection()

    def send(self, cmd):
        if not self.comms_started:
            try:
                self.leem_com.send("asc")
                self.comms_started=True
            except:
                exceptionType, exception, traceback=sys.exc_info();
                handle_messages.log(None, "Error sending asc command to leem2000 at " + str(self.leem_com.address) + ":" + str(self.leem_com.port) +". Try restarting Leem2000 ", exceptionType, exception, traceback, True)
        return self.leem_com.send(cmd)
       
    def reconnect(self):
        try:
            #have to close the old one if it's not broken
            self.leem_com.sendCmdNoReply("clo")
        except DeviceException:
            pass #we expect this
        new_com = SocketBidiAsciiCommunicator()
        new_com.setAddress( self.leem_com.address )
        new_com.setPort( self.leem_com.port )
        new_com.setCmdTerm( self.leem_com.cmdTerm )
        new_com.setReplyTerm( self.leem_com.replyTerm )
        new_finder_map = {"leem2000_com" : new_com}
        Finder.find("leem2000_objects").setMap(new_finder_map)
        self.leem_com = new_com

class leem_scannable(ScannableBase):
    def __init__(self, name, moduleName, format, leem2000):
        self.name = name
        self.setOutputFormat([format])
        self.moduleName=moduleName
        self.setInputNames([name]);
        self.leem2000=leem2000
        self.lastValue = 0;
        self.readOnly=False
        self._offset=0.0
        
    def setOffset(self, value):
        self._offset=value
    
    def getOffset(self):
        return self._offset

    def isBusy(self):
        if self.readOnly:
            return False
        reply = self.leem2000.send("get " + self.moduleName + "\0")
        return reply == "ErrorCode -102"

    def getPosition(self):
        try:
            if self.readOnly:
                return float(self.leem2000.send(self.moduleName)) - self.getOffset()
            else:
                return float(self.leem2000.send("get " + self.moduleName + "\0"))
        except:
            return self.lastValue

    def asynchronousMoveTo(self,new_position):
        if self.readOnly:
            raise Exception("This is a read-only scannable.")
        cmd="set " + self.moduleName +"="+`new_position`
        reply=self.leem2000.send(cmd)
        if reply != "0":
            raise Exception("Failed in command " + `cmd` + " reply=" + `reply` + "")
        self.lastValue = new_position
        return

class leem_readonly(ScannableBase):
    def __init__(self, name, command, leem2000):
        self.name = name
        self.setOutputFormat(["%s"])
        self.setInputNames([name]);
        self.command=command
        self.leem2000=leem2000
        # find number at beginning of the string, be it integer, float, or scientific notation
        self.trimRegexPattern = re.compile(r'^([-+]?\d+\.?\d*([Ee][-+]?\d*)?)') 

    def isBusy(self):
        return False

    def getPosition(self):
        ro_val = self.leem2000.send(self.command)
        return self.trimToNumeric(ro_val)    # trim off UTF-8 string postfixed to the value

    def asynchronousMoveTo(self,new_position):
        raise Exception(self.name + " is readonly")

    def trimToNumeric(self, posVal):
        if self.command=='prl':
            matchNumeric = self.trimRegexPattern.search(posVal)
            if matchNumeric:
                resVal = matchNumeric.group(0)
            else:
                resVal = ''
        else:
                resVal = posVal
        return resVal

