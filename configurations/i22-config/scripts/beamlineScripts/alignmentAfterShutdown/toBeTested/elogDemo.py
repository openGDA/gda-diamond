import scisoftpy as dnp
from gda.util import ElogEntry
from time import sleep
from gda.configuration.properties import LocalProperties

class Elog:
    def __init__(self, title, userID, visit, logID, groupID):
        self.log = ElogEntry(title, userID, visit, logID, groupID)
        self.peakCount = 0
        self.edgeCount = 0
        self.count = 0
        
    def addText(self, text):
        self.log.addText(text)
    
    def addPeak(self, caption):
        path = "/tmp/peakFit-%d.png" % self.peakCount
        self._addPlot("Peak Fit Plot", caption, path)
        self.peakCount += 1

    def addEdge(self, caption):
        path = "/tmp/edgeFit-%d.png" % self.edgeCount
        self._addPlot("Edge Fit Plot", caption, path)
        self.edgeCount += 1
        
    def _addPlot(self, plotname, caption, path=None):
        if path is None:
            path = "/tmp/%s-%d.png" %(plotname, self.count)
            self.count += 1
        dnp.plot.export(name=plotname, format="png", savepath=path)
        sleep(3)
        self.log.addImage(path, caption)
    
    def post(self, file=None):
        if file is None:
            self.log.post()
        else:
            self.log.postFile(file)

if __name__ == "__main__":
    elog = Elog("Beam Alignment", "i22user", LocalProperties.get(LocalProperties.GDA_DEF_VISIT), "BLI22", "BLI22")
#     elog = Elog( TITLE, USER, VISIT, LOG, GROUP)
    
    scan(showtime, 1,7,1,bsdiode)
    elog.addText("scan(t, 1,10,1,bsdiode)")
    elog.addPeak("Peak fit caption")
    elog.addEdge("Edge fit caption")
    scan(showtime, 1,7,1,bsdiode)
    elog.addText("scan(t, 1,10,1,bsdiode)")
    elog.addPeak("Peak fit caption2")
    elog.addEdge("Edge fit caption2")
    elog.post("/tmp/logFile.html")
