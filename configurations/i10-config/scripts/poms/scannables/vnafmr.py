import scisoftpy as dnp
import time
import h5py

from gda.data.scan.datawriter import NexusDataWriter


class vnafmrClass():
    def __init__(self, vna, mag, path):
        self.vna = vna
        self.mag = mag
        self.path = path
        
        self.f = None
        self.freqPts = 0
        
    def startNewScan(self):
        count = 0
        #count = np.loadtxt("./scanCounter.dat", dtype="d")
        #count = count + 1
        #np.savetxt("./scanCounter.dat", [count], fmt="%06d")
        print "Starting scan #%06d" % count
        self.f = h5py.File(self.path + "/rasor-vnafmr-%06d.hdf5" % count, "w", libver='latest')
#        self.f = h5py.File(self.path + "/rasor-vnafmr-%06d.hdf5" % count, "w")

        
    def fieldScan(self, start, stop, step):
        self.scanStart()
        if (stop > start) :
            fields = np.arange(start, (stop+0.1), step)            # 0.1 extra so stop is included
        else:
            fields = np.arange(start, (stop-0.1), step)            # 0.1 extra so stop is included        
        self.f.create_dataset('field', (0,), chunks=(1,), maxshape=(None,))
        
        #self.f.attrs['power'] = self.vna.power 
        self.f.attrs['bandwidth'] = self.vna.bandwidth
        #self.f.attrs['averages'] = self.vna.averages 
        
        
        for field in fields:
            self.mag.setField(field)            
            time.sleep(2)
            
            i = np.shape(self.f['field'])[0]
            self.scanStep(i)
            self.f['field'].resize((i+1,))
            self.f['field'][i] = field
            self.f.flush()
            
        self.f.close()
        
    def dummyScan(self,steps):
        self.scanStart()
        dummy = np.arange(1, steps, 1)
        self.f.create_dataset('dummy', (0,), chunks=(1,), maxshape=(None,))
        
        for d in dummy:
            print "dummy: %4d " % d
            i = np.shape(self.f['dummy'])[0]
            self.f['dummy'].resize((i+1,))
            self.scanStep(i)
            self.f.flush()
    

    def tempScan(self, start, stop, rate):
        from rasorTemperature import rasorTemperature
        rasorTemp = rasorTemperature()

        rasorTemp.waitForStableTemp(start)    

        self.scanStart()
        self.f.create_dataset('waveguide_temp', (0,), chunks=(1,), maxshape=(None,))
        self.f.create_dataset('cryo_temp', (0,), chunks=(1,), maxshape=(None,))


        
        rasorTemp.startSweep(start, stop, rate)
            
        while rasorTemp.isSweepRunning():

            i = np.shape(self.f['waveguide_temp'])[0]
            self.scanStep(i)
            waveguide, cryo = rasorTemp.getTemp()
            self.f['waveguide_temp'].resize((i+1,))
            self.f['cryo_temp'].resize((i+1,))
            self.f['waveguide_temp'][i] = waveguide
            self.f['cryo_temp'][i] = cryo
            self.f.flush()

            print "temp: %0.2f mT" % waveguide
        rasorTemp.setTemp(stop)
        self.f.close()
            
    
    
    def scanStart(self):
        self.startNewScan()
        self.vna.doSweep()
        freq = self.vna.getFrequency()
        self.freqPts = len(freq)
        freqPts = self.freqPts

        grp = self.f
        grp.create_dataset('freq', data=freq)
        grp.create_dataset('s12', (0,freqPts), chunks=(1,freqPts), maxshape=(None,freqPts), dtype=np.complex)
        grp.create_dataset('s21', (0,freqPts), chunks=(1,freqPts), maxshape=(None,freqPts), dtype=np.complex)

        grp.create_dataset('s12r', (0,freqPts), chunks=(1,freqPts), maxshape=(None,freqPts), dtype=np.complex)
        grp.create_dataset('s21r', (0,freqPts), chunks=(1,freqPts), maxshape=(None,freqPts), dtype=np.complex)

        grp.swmr_mode = True



        
    def scanStep(self, i):
        self.vna.doSweep()
        #print "after do sweep"
        s12, s21 = self.vna.getData()
        #print "after get data"
        grp = self.f
        freqPts = self.freqPts
        grp['s12'].resize((i+1, freqPts))
        grp['s21'].resize((i+1, freqPts))

        grp['s12'][i,:] = s12
        grp['s21'][i,:] = s21
        



