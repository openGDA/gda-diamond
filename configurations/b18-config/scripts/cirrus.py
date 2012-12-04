import threading
import datetime
from time import sleep

class ThreadClass(threading.Thread):
    def run(self):
        pressure = cirrus.getPressure()
        dataDir = PathConstructor.createFromProperty("gda.data.scan.datawriter.datadir");
        f=open(dataDir,'w')
        for i in range(5):
            now = datetime.datetime.now()
            cirrus.collectData()
            data = cirrus.readout()
            f.write("time")
            for d in data:
                f.write("    "+str(d))
            f.write("\n")
            sleep(1)
        f.close()



cirrus.setMasses([2, 28, 32])

t = ThreadClass()
t.setName("cirrus")
t.start()