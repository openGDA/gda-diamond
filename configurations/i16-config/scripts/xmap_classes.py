from gda.analysis.datastructure import *
from gda.analysis import *
import java.io.FileNotFoundException
# test = ScanFileContainer()
# test.loadPilatusData("/dls/i16/data/Pilatus/test1556.tif")
# test.plot()
# matrix = test.getImage().doubleMatrix()

class XmapAcquireClass(PseudoDevice):
	'''
	Simple XMAP PD. Give real time. Returns real time and roi1,2,3
	'''

	def __init__(self,name,pvroot):
		self.setName(name);
		self.setOutputFormat(['%.2f','%.0f','%.0f','%.0f'])
		self.setLevel(9)
		self.setInputNames(['time'])
		self.setExtraNames(['ROI1','ROI2','ROI3'])
		self.ClientRoot=pvroot
		self.CAtpre=CAClient(self.ClientRoot+'TPRE'); 
		self.CAtpre.configure();
		self.CAtpre.caput(1);		#preset live time mode
		self.CAstop=CAClient(self.ClientRoot+'MCA:STOP'); self.CAstop.configure();		#stop
		self.CAstat=CAClient(self.ClientRoot+'0:MCA:ACQSTAT'); self.CAstat.configure();		#get acquire status
		self.CAestart=CAClient(self.ClientRoot+'MCA:ERST'); self.CAestart.configure();		#erase & start
		self.CAertm=CAClient(self.ClientRoot+'0:MCA.ERTM');self.CAertm.configure();	#get real time
		self.CApreval=CAClient(self.ClientRoot+'PREVAL');self.CApreval.configure();	#set preset value
		self.CAroi1=CAClient(self.ClientRoot+'0:MCA.R0');self.CAroi1.configure();	#roi1
		self.CAroi2=CAClient(self.ClientRoot+'0:MCA.R1');self.CAroi2.configure();	#roi1
		self.CAroi3=CAClient(self.ClientRoot+'0:MCA.R2');self.CAroi3.configure();	#roi1
		self.CAtrigth=CAClient(self.ClientRoot+'TRIGTH');self.CAtrigth.configure(); self.CAtrigth.caput(1000);	#trig thresh
		self.CAbaseth=CAClient(self.ClientRoot+'BASETH');self.CAbaseth.configure(); self.CAbaseth.caput(1000);	#baseline thresh
		self.CAenergyth=CAClient(self.ClientRoot+'ENERGYTH');self.CAenergyth.configure();  self.CAenergyth.caput(0);	#energy thresh
		self.CAmcan=CAClient(self.ClientRoot+'MCA:NBINS');self.CAmcan.configure(); self.CAmcan.caput(16384);	#mca nbins
		self.CAbinw=CAClient(self.ClientRoot+'BINWIDTH');self.CAbinw.configure();  self.CAbinw.caput(10);	#bin width
		self.CAdrange=CAClient(self.ClientRoot+'DRANGE');self.CAdrange.configure();  self.CAdrange.caput(47200);	#drange
		self.CAcalen=CAClient(self.ClientRoot+'CALEN');self.CAcalen.configure();  self.CAcalen.caput(5900);	#cal energy
		self.CApeakt=CAClient(self.ClientRoot+'PEAKT');self.CApeakt.configure();  self.CApeakt.caput(0.0);	#peak time
		self.CAstatt=CAClient(self.ClientRoot+'MCA:STAT.SCAN');self.CAstatt.configure();  self.CAstatt.caput(9);	#status update time 0.1 sec
		self.CAreadt=CAClient(self.ClientRoot+'MCA:READ.SCAN');self.CAreadt.configure();  self.CAreadt.caput(9);	#data readout time 0.1 sec

		self.CAtrigthresh=CAClient(self.ClientRoot+'TRIGTH');self.CAtrigthresh.configure();
		self.CAbaselinethresh=CAClient(self.ClientRoot+'BASETH');self.CAbaselinethresh.configure();

		self.CAtrigthresh.caput(1000)		#set for Vortex
		self.CAbaselinethresh.caput(1000)	#set for Vortex

	def isBusy(self):
		stat=int(float(self.CAstat.caget()))
#		sleep(.5)
		#print stat
		return not stat==2

	def stop(self):
		self.CAstop.caput(1)

	def getPosition(self):
		return [float(self.CAertm.caget()),float(self.CAroi1.caget()),float(self.CAroi2.caget()),float(self.CAroi3.caget())] 

	def asynchronousMoveTo(self,newpos):
		self.CAstop.caput(1)
		#sleep(.05)
		self.CApreval.caput(newpos)
		#sleep(.05)
		self.CAestart.caput(1)
		sleep(.5)
		#sleep(1)#sleep(.7) not enough
		#for ii in range(40):
		#	sleep(.1)
		#	print int(float(self.CAstat.caget()))

#	def atScanStart(self):
#		self.stop()

class XmapAcquireClassNew(PseudoDevice):
	'''
	Simple XMAP PD. Give real time. Returns real time and roi1,2,3
	Temp new version  - change some PV names
	'''

	def __init__(self,name,pvroot):
		self.setName(name);
		self.setOutputFormat(['%.2f','%.0f','%.0f','%.0f'])
		self.setLevel(9)
		self.setInputNames(['time'])
		self.setExtraNames(['ROI1','ROI2','ROI3'])
		self.ClientRoot=pvroot
		self.CAtpre=CAClient(self.ClientRoot+'TPRE'); 
		self.CAtpre.configure();
		self.CAtpre.caput(1);		#preset live time mode
		self.CAstop=CAClient(self.ClientRoot+'MCA:STOP'); self.CAstop.configure();		#stop
		self.CAstat=CAClient(self.ClientRoot+'0:MCA:ACQSTAT'); self.CAstat.configure();		#get acquire status
		self.CAestart=CAClient(self.ClientRoot+'MCA:ERST'); self.CAestart.configure();		#erase & start
		self.CAertm=CAClient(self.ClientRoot+'0:MCA.ERTM');self.CAertm.configure();	#get real time
		self.CApreval=CAClient(self.ClientRoot+'PREVAL');self.CApreval.configure();	#set preset value
		self.CAroi1=CAClient(self.ClientRoot+'0:MCA.R0');self.CAroi1.configure();	#roi1
		self.CAroi2=CAClient(self.ClientRoot+'0:MCA.R1');self.CAroi2.configure();	#roi1
		self.CAroi3=CAClient(self.ClientRoot+'0:MCA.R2');self.CAroi3.configure();	#roi1
		self.CAtrigth=CAClient(self.ClientRoot+'TRIGTH');self.CAtrigth.configure(); self.CAtrigth.caput(1000);	#trig thresh
		self.CAbaseth=CAClient(self.ClientRoot+'BASETH');self.CAbaseth.configure(); self.CAbaseth.caput(1000);	#baseline thresh
		self.CAenergyth=CAClient(self.ClientRoot+'ENERGYTH');self.CAenergyth.configure();  self.CAenergyth.caput(0);	#energy thresh
		self.CAmcan=CAClient(self.ClientRoot+'MCA:NBINS');self.CAmcan.configure(); self.CAmcan.caput(16384);	#mca nbins
		self.CAbinw=CAClient(self.ClientRoot+'BINWIDTH');self.CAbinw.configure();  self.CAbinw.caput(10);	#bin width
		self.CAdrange=CAClient(self.ClientRoot+'DRANGE');self.CAdrange.configure();  self.CAdrange.caput(47200);	#drange
		self.CAcalen=CAClient(self.ClientRoot+'CALEN');self.CAcalen.configure();  self.CAcalen.caput(5900);	#cal energy
		self.CApeakt=CAClient(self.ClientRoot+'PEAKT');self.CApeakt.configure();  self.CApeakt.caput(0.0);	#peak time
		self.CAstatt=CAClient(self.ClientRoot+'MCA:STAT.SCAN');self.CAstatt.configure();  self.CAstatt.caput(9);	#status update time 0.1 sec
		self.CAreadt=CAClient(self.ClientRoot+'MCA:READ.SCAN');self.CAreadt.configure();  self.CAreadt.caput(9);	#data readout time 0.1 sec

		self.CAtrigthresh=CAClient(self.ClientRoot+'TRIGTH');self.CAtrigthresh.configure();
		self.CAbaselinethresh=CAClient(self.ClientRoot+'BASETH');self.CAbaselinethresh.configure();

		self.CAtrigthresh.caput(1000)		#set for Vortex
		self.CAbaselinethresh.caput(1000)	#set for Vortex

	def isBusy(self):
		stat=int(float(self.CAstat.caget()))
#		sleep(.5)
		#print stat
		return not stat==2

	def stop(self):
		self.CAstop.caput(1)

	def getPosition(self):
		return [float(self.CAertm.caget()),float(self.CAroi1.caget()),float(self.CAroi2.caget()),float(self.CAroi3.caget())] 

	def asynchronousMoveTo(self,newpos):
		self.CAstop.caput(1)
		#sleep(.05)
		self.CApreval.caput(newpos)
		#sleep(.05)
		self.CAestart.caput(1)
		sleep(.5)
		#sleep(1)#sleep(.7) not enough
		#for ii in range(40):
		#	sleep(.1)
		#	print int(float(self.CAstat.caget()))

#	def atScanStart(self):
#		self.stop()











#BL16I-EA-XMAP-01:XMAP0:0:MCA.R0
#caget('BL16I-EA-XMAP-01:XMAP0:0:MCA.ACQG')
#caget('BL16I-EA-XMAP-01:XMAP0:0:MCA:ACQSTAT')
#BL16I-EA-XMAP-01:XMAP0:0:MCA:ACQSTAT
try:
	xm=XmapAcquireClass('xm','BL16I-EA-XMAP-01:XMAP0:')
except java.lang.IllegalStateException, e:
	print "Problem connecting to xmap device: ", `e`
#BL16I-EA-XMAP-01:XMAP0:0:MCA.ELTM0
#BL16I-EA-XMAP-01:XMAP0:0:MCA.ERTM
#BL16I-EA-XMAP-01:XMAP0:MCA:ERST
#BL16I-EA-XMAP-01:XMAP0:TPRE
