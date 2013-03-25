import sys
from time import sleep
from gda.jython.commands import InputCommands
from gda.device.detector.odccd import CrysalisRun
from gda.device.detector.odccd import CrysalisRunList
from gda.device.detector.odccd import CrysalisRunListValidator
import gda.configuration.properties.LocalProperties as LocalProperties
import gdascripts.parameters
from gdascripts.messages import handle_messages
from gdascripts.messages.handle_messages import simpleLog
from operationalControl import moveMotor


#code to extract runlist from crysalis                
class Item:
    def __init__(self, name):
        self.name = name
        self.type = None
        self.dimension=None
        self.value = None
    
    def initFromDescription(self, description):
        #need to cope with strings e.g. string = "garnet" 
        #print description
        if description[0:6]=="string":
            self.type = "string"
            self.dimension=""
            self.value = description.split("=")[1].strip().replace("\"","")
        else:
            self.type = description[0:description.find("[")]
            self.dimension=description[description.find("[")+1:description.find("]")]
            self.value = description[description.find("=")+1:]
        
    def __str__(self):
        return self.name + ":" + `self.type` + `self.dimension` + " = " + `self.value`

def MakeItem(name, type, dimension, value):
    i = Item(name)
    i.type=type
    i.dimension=dimension
    i.value=value
    return i        

class Folder:
    def extractFolders(self, ls, controller):
        folders = {}
        lines =  ls.splitlines()
        prefix = "api:[+] ("
        for line in lines:
            start_api = line.find(prefix)
            if start_api >= 0:
                name = line[start_api+len(prefix):line.rfind(")")]
                f = Folder(self.target, name)
                f.initFromController(controller)
                folders[name] = f
        return folders

    def extractItems(self, ls, controller):
        items = {}
        lines =  ls.splitlines()
        prefix = "api:    ("
        for line in lines:
            start_api = line.find(prefix)
            if start_api >= 0:
                colon=line.rfind(":")
                name = line[start_api+len(prefix):line.rfind(")")]
                i = Item(name)
                i.initFromDescription(line[colon+1:])
                items[name] = i
        return items
    
    def initFromController(self,controller):    
#        print self.target
        controller.runScript("api script stop")
        controller.runScript("db ls -v " + self.target + ";");
        controller.readInputUntil("api:(" + self.target + ")");
        listEnd = controller.readInputUntil("api:End of list.");        
#        print ls
        self.subfolders = self.extractFolders(listEnd, controller)
        self.items = self.extractItems(listEnd, controller)
        
    def __init__(self, parent , name):
        self.name = name
        self.target = parent + "/" + name
        self.subfolders = None
        self.items = None

    def dump(self):
        print "Folder name = " + self.name
        print "Target = " + self.target + " contains:"
        for item in self.items:
            print "Item " + str(self.items[item])
        for f in self.subfolders:
            self.subfolders[f].dump()

def readRunListFromDB(odccd_controller, root, folderName, runFolder, runFile):
    #read from teh odccd controller and create a local variable - Folder
    folder = Folder(root,folderName)
    folder.initFromController(odccd_controller)
#    folder.dump()
    #unpack Folder into a CrysalisRunlist
    runList = CrysalisRunList()
    runList.setRunFolder(runFolder)
    runList.setRunFile(runFile)
    if( len(folder.subfolders) == 0):
        raise "readRunListFromDB - runlist empty - is the run file valid?"
    for f in folder.subfolders:
        sf = folder.subfolders[f]
        if sf.name == "runs":
            for irun in range(0,len(sf.subfolders)):
                crysalisRun = CrysalisRun()
                runFolder = sf.subfolders["run"+`(irun+1)`]
                crysalisRun.setName(runFolder.name)
                crysalisRun.setDomegaindeg(float(runFolder.items["domegaindeg"].value))
                crysalisRun.setDdetectorindeg(float(runFolder.items["ddetectorindeg"].value))
                crysalisRun.setDkappaindeg(float(runFolder.items["dkappaindeg"].value))
                crysalisRun.setDphiindeg(float(runFolder.items["dphiindeg"].value))
                crysalisRun.setDscanstartindeg(float(runFolder.items["dscanstartindeg"].value))
                crysalisRun.setDscanendindeg(float(runFolder.items["dscanendindeg"].value))
                crysalisRun.setDscanwidthindeg(float(runFolder.items["dscanwidthindeg"].value))
                crysalisRun.setDscanspeedratio(float(runFolder.items["dscanspeedratio"].value))
                crysalisRun.setDexposuretimeinsec(float(runFolder.items["dexposuretimeinsec"].value))
                crysalisRun.setInum(int(float(runFolder.items["inum"].value)))
                crysalisRun.setIrunscantype(int(float(runFolder.items["irunscantype"].value)))
                crysalisRun.setDwnumofframes(int(float(runFolder.items["dwnumofframes"].value)))
                crysalisRun.setDwnumofframesdone(int(float(runFolder.items["dwnumofframesdone"].value)))
                runList.addRun(crysalisRun)
        elif sf.name == "info":
            runList.setName(sf.name);
            runList.setDwtotalnumofframes(int(float(sf.items["dwtotalnumofframes"].value)))
            runList.setWreferenceframefrequency(int(float(sf.items["wreferenceframefrequency"].value)))
            runList.setWversioninfo(int(float(sf.items["wversioninfo"].value)))
            runList.setInumofruns(int(float(sf.items["inumofruns"].value)))
            runList.setWisreferenceframes(int(float(sf.items["wisreferenceframes"].value)))
            runList.setInumofreferenceruns(int(float(sf.items["inumofreferenceruns"].value)))
            runList.setCexperimentname(sf.items["cexperimentname"].value)
            runList.setCexperimentdir(sf.items["cexperimentdir"].value)
    odccd_controller.flush()

    return runList

def getRunList(odccd_controller, runFolder, runFile):
    """
    Reads a Crysalis run file and returns a CrysalisRunList object
    e.g.
    rl=RunListLoader().getRunList(ccd,'X:/data/currentdir/GDA/garnet','garnet.run')
    rl=RunListLoader().getRunList(ccd, "C:/Data/GDA/garnet","garnet.run")
    """
    root = "/root"
    folderName = "gda_run"
    #local to make code easier to read
    targetRunFile=runFolder +"/" +runFile
    target = root + "/" + folderName
    odccd_controller.runScript("call importRunList " + "\"" + targetRunFile + "\" \"" + target + "\"");
    #I have observed IS not returning 'importRunList completed.' in which case we needed to put a sleep
    try:
        odccd_controller.readInputUntil("importRunList completed.");
    except:
        sleep(2)
    odccd_controller.flush()
    return readRunListFromDB(odccd_controller, root, folderName, runFolder, runFile)


def updateFrameDoneInRunFile(odccd_controller, crysalisRunList):
    odccd_controller.flush()
    targetRunFile=crysalisRunList.getRunFolder() +"/" +crysalisRunList.getRunFile()
    root = "/root"
    folderName = "gda_run"
    target = root + "/" + folderName

    #check the only difference in the number of frames done
    currentRunFile = getRunList(odccd_controller, crysalisRunList.getRunFolder(), crysalisRunList.getRunFile())
    for current, actual in zip(currentRunFile.getRunList(), crysalisRunList.getRunList()):
        current.dwnumofframesdone = actual.dwnumofframesdone
        
    if currentRunFile != crysalisRunList:
        raise "currentRunFile does not match. \nCurrentRunFile =  " + `currentRunFile` + "\ncrysalisRunList = " + `crysalisRunList`
    
    for run in crysalisRunList.getRunList():
        dwnumofframesdone_target = target + "/runs/"+ run.name + "/dwnumofframesdone"
        cmd = "call setInteger " + "\"" + dwnumofframesdone_target + "\" " + `run.getDwnumofframesdone()`
        #simpleLog("Execeuting script " + cmd)
        odccd_controller.runScript(cmd);
        #I have observed IS not returning 'importRunList completed.' in which case we needed to put a sleep
        try:
            odccd_controller.readInputUntil("setInteger completed.");
        except:
            sleep(2)
    odccd_controller.flush()
    readBack = readRunListFromDB(odccd_controller, root, folderName, crysalisRunList.getRunFolder(), crysalisRunList.getRunFile())
    if readBack != crysalisRunList:
        raise "readBack is incorrect " + readBack
    odccd_controller.runScript("call exportRunList " + "\"" + target + "\" \"" + targetRunFile + "\"");    
    odccd_controller.flush()

def moveIfOKed( motor, pos):
    moveMotor( motor, pos)
#    ok = InputCommands.requestInput("Press y to move " + motor.getName() + " from " + `motor()` + " to " + `pos`)
#    if ok == "y":
#        moveMotor( motor, pos)
#    else:
#        raise "move skipped on user request"
    
def executeRun(run, ruby, dkphi, dktheta, ddelta, dkappa, experimentName, runNumber):
    simpleLog("\nExecuting run : \n" + `run`)
    start = run.getStart()
    end = run.getEnd()
    motor = dkphi
    isOmegaScan = run.scanType() == CrysalisRun.SCANTYPE.OMEGA
    if isOmegaScan:
        motor = dktheta
        start -= 90.
        end -= 90.

    simpleLog("\nScan " + motor.getName() + " from " + `start` + " to " + `end`)
    moveIfOKed(dkappa, run.getDkappaindeg())
    moveIfOKed(ddelta, run.getDdetectorindeg())
    if isOmegaScan:
        moveIfOKed(dkphi, run.getDphiindeg())
    else:
        moveIfOKed(dktheta, run.getDomegaindeg()-90.)
    simpleScan(motor, start, end, run.getStepSize(), ruby, run.getExposureTime(), 1, experimentName+"_"+str(runNumber))
    run.dwnumofframesdone = run.dwnumofframes

def checkValidity(crysalisRunList):
    try:
        CrysalisRunListValidator().checkValidity(crysalisRunList)
    except:
        type, exception, traceback = sys.exc_info()
        handle_messages.log(None, "runScan", type, exception, traceback, True)

def executeRunList(crysalisRunList, ruby, dkphi, dktheta, ddelta, dkappa):
    validator = CrysalisRunListValidator()
    validator.checkValidity(crysalisRunList)
    ruby.setDir(crysalisRunList.runFolder+"/frames")
    runNumber=0
    for run in crysalisRunList.getRunList():
        runNumber += 1
        if run.dwnumofframesdone == run.dwnumofframes:
            simpleLog("Skipping run " + `runNumber` + " as all frames already done")
        else:
            executeRun(run, ruby, dkphi, dktheta, ddelta, dkappa, crysalisRunList.getCexperimentname(), runNumber)
            simpleLog("runScan - updating the Crysalis runFile")
            updateFrameDoneInRunFile(ruby.detector,crysalisRunList)
    #get runlist again and check they match - i.e. the done numbers are the same
    runListCheck = getRunList(ruby.detector, crysalisRunList.getRunFolder(), crysalisRunList.getRunFile())
    if runListCheck != crysalisRunList:
        raise "executeRunList - runsLists do not match " + `runListCheck` + "\n" + `crysalisRunList`
 
def testExceuteRunList(ruby, dkphi, dktheta, ddelta, dkappa):
    runList = CrysalisRunList.createFromXML(LocalProperties.get("gda.config") + "/xml/TestCrysalisRunList.xml")
    simpleLog(`runList`)
    executeRunList(runList, ruby, dkphi, dktheta, ddelta, dkappa)
    
def runScan(ruby, runFolder, runFile):
    """
    Reads, executes and updates a Crysalis runlist
    e.g. runScan(ruby, "C:/Data/GDA/garnet","garnet.run")
    """
    try:
        jythonNameMap = gdascripts.parameters.beamline_parameters.JythonNameSpaceMapping()
        dkphi = jythonNameMap.dkphi   
        dktheta = jythonNameMap.dktheta   
        ddelta = jythonNameMap.ddelta   
        dkappa = jythonNameMap.dkappa   
        simpleLog("runScan: runFolder = " + `runFolder` + " runFile = " + `runFile` + " dkphi = " + `dkphi.getName()`)
        simpleLog("runScan - getting runlist from Crysalis")
        crysalisRunList = getRunList(ruby.detector, runFolder, runFile)
        simpleLog("runList = \n" + `crysalisRunList`)
        xmlfile = LocalProperties.get("gda.config") + "/var/CrysalisRunList_" + crysalisRunList.getCexperimentname() + ".xml"
        simpleLog("runScan - saving runlist to " + `xmlfile`)
        crysalisRunList.writeToXML(xmlfile)
        input = InputCommands.requestInput("Enter \"y\" to perform the data collection?" )
        if input != "y":
            simpleLog("Data collection aborted on user request")
        else:
            simpleLog("runScan - executing runlist")
            executeRunList(crysalisRunList, ruby, dkphi, dktheta, ddelta, dkappa)
    except:
        type, exception, traceback = sys.exc_info()
        handle_messages.log(None, "runScan", type, exception, traceback, True)
    simpleLog("runScan completed")
