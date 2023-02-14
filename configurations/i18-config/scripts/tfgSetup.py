from gda.epics import CAClient
from time import sleep
import time
import csv

class TFG():
    def __init__(self):
        self.das = finder.find("daserver")
        self.tfg = finder.find("tfg")
        self.converter = finder.find("auto_mDeg_idGap_mm_converter_Si111")
        self.energyPos = []
        self.ionChamberHandle = 0
        dataFolder = "/dls/i18/data/2022/cm31141-5/ascii" #"/dls/i18/data/2021/sp28403-1/ascii"
        timestamp = time.strftime('%a_%H_%M_%S')
        self.filename = "%s/raw_%s.dat" % (dataFolder,timestamp)
        self.fileNorm = "%s/Norm_%s.dat" % (dataFolder,timestamp)
    
    def run(self, reps, cycles, frames, collection, deadTime):
        self.noOfReps = reps
        self.noOfCycles = cycles
        self.noOfFrames = frames
        self.collectionTime = collection
        self.deadTime = deadTime
        
        self.get_energy_pos()
        
        print "starting script"
        # Write the data to the file
        self.write_energy_time_to_file()
        self.perform_TFG()
        print "output files: \n"+self.filename+"\n"+self.fileNorm
        print "Script Finished"
    

    def get_energy_pos(self):
        energyValue=6500
        energyStep=1
        numPoints=30
        for i in range(numPoints):
            # Add the energy value to energyPos list for each point
            self.energyPos.append(energyValue)
            # Increase the energyValue by the step
            energyValue+=energyStep
    
    def get_user_info(self):
        with open(self.userValuesFolder, 'rb') as f:
            reader = csv.reader(f, delimiter=',')
            counter=0
            for row in reader:
                # Ignore all rows that start with a #
                if row[0][0]=='#':
                    continue
                
                if counter==0:
                    self.noOfReps = int(row[0])
                elif counter==1:
                    self.noOfCycles = int(row[0])
                elif counter==2:
                    self.noOfFrames = int(row[0])
                elif counter==3:
                    self.collectionTime = row[0]
                elif counter==4:
                    self.deadTime = float(row[0])
                # Increase the row counter by fg read framone
                counter+=1

    """
    Write the total collection per frame, i.e. number of cycles * collection time, to the files
    """
    def write_energy_time_to_file(self):
        ioContent = ""
        itContent = ""
        irefContent = ""
        norm_itContent = ""
        norm_irefContent = ""
        for i in range(self.noOfFrames+1):
            # Set the raw file content
            ioContent += " i0Frame" + str(i)
            itContent += " itFrame"+str(i)
            irefContent += " irefFrame"+str(i)
            # Set the norm file content
            norm_itContent += " Norm_itFrame"+str(i)
            norm_irefContent += " Norm_irefFrame"+str(i)
        self.write_to_file(self.filename, "w", "#EnergyTime"+ioContent+itContent+irefContent)
        self.write_to_file(self.fileNorm, "w", "#Energy Time"+norm_itContent+norm_irefContent)
    
    def write_to_file(self, fName, strategy, content):
        f = open(fName, strategy)
        f.write(content)
        f.close()
    
    def perform_TFG(self):
        e=1
        for ePos in self.energyPos:
            print "Move "+str(e)+"/"+str(len(self.energyPos))
            e+=1
            self.converter.disableAutoConversion()
            pos energy ePos
            self.converter.enableAutoConversion()
            i0,it,iref,time = self.run_repetitions()
            
            i0Content = ''
            itContent = ''
            irefContent = ''
            fNorm_itContent = ''
            fNorm_irefContent = ''
            print "Writing results to file"
            for i in range(len(i0)):
                i0Content+=' '+str(i0[i])
                itContent+=' '+str(it[i])
                irefContent+=' '+str(iref[i])
                fNorm_itContent += ' '+str(it[i]/i0[i])
                fNorm_irefContent += ' '+str(iref[i])
            # Write file content
            self.write_to_file(self.filename, "a", '\n'+str(ePos)+' '+str(time)+ i0Content + itContent + irefContent)
            self.write_to_file(self.fileNorm, "a", '\n'+str(ePos)+' '+str(time)+fNorm_itContent+fNorm_irefContent)
    
    def run_repetitions(self):
        i0, it, iref = [],[],[]
        for rep in range(self.noOfReps):
            print "Running repetition "+str(rep+1)+"/"+str(self.noOfReps)
            self.setup()
            i=0
            while self.das.sendCommand("tfg read status") != "IDLE":
                #print self.das.sendCommand("tfg read frame")
                if i>=10:
                    break
                i+=1
            results = self.collect_data()
            
            print "Results retrieved:", len(results)
            for r in results:
                i0.append(r[1])
                it.append(r[2])
                iref.append(r[3])
                
            sleep(1)
        return i0,it,iref,r[0]
    
    def setup(self):
        print "Setting up TFG..."
        try:
            self.das.sendCommand("tfg init")
            self.das.sendCommand("disable %d" %(self.ionChamberHandle))
            self.das.sendCommand("clean %d" %(self.ionChamberHandle))
            self.das.sendCommand("enable %d" %(self.ionChamberHandle))
            self.das.sendCommand('tfg config "etfg0" tfg2')
            command="tfg setup-groups cycles %d"%(self.noOfCycles)
            command+="\n%d %d %s 0 0 0 0"%(self.noOfFrames, self.deadTime, self.collectionTime)
            command+="\n1 2e-6 0 0 0 0 0"
            command+="\n-1 0 0 0 0 0 0"
            self.das.sendCommand(command)
            self.das.sendCommand("tfg start")
            print "TFG started..."
            return
        except:
            print "Error configuring TFG, check da.server is running"
            return
    
    def collect_data(self):
        return counterTimer01.readoutFrames(0,self.noOfFrames)
    
def run_tfg(cycles, energy, frame, collection, dead):
    t=TFG()
    t.run(cycles, energy, frame, collection, dead)
