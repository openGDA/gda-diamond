from gda.analysis.utils.optimisation import *
from gda.analysis.utils import *
from gda.analysis.functions.dataset import Integrate2D
from time import sleep 
import math

# b=BimorphSolve(vfm,"BL22I-DI-PHDGN-10:CAM:DATA","/dls/i22/data/2010/cm1904-3/ga")

class BimorphSolve(ProblemDefinition):

	def __init__(self, bimorph, cameraDataPV, dirbase):
		self.bimorph=bimorph
		self.dir=dirbase
		#self.initialset=[184.2, -55.8, 160, 100, 250, -100, 100, -170, 133.2, 138.7, -200, 257.3, 200, 300, 115.8, 115.8]
		self.initialGAValues=[0.8, 0.36, 0.76, 0.57, .99, 0.2, 0.735, 0.17, 0.78, 0.82, 0.02, 0.99, 0.75, 0.93, 0.6, 0.64]
		# set up the camera
		self.cd=CAClient(cameraDataPV)
		self.cd.configure()
		# set up the integrator
		self.integrator = Integrate2D(000,100,500,700)

	def getNumberOfParameters(self):
		return len(self.bimorph.getInputNames())
	
	def setVoltages(self, voltages):
		if len(voltages) != self.getNumberOfParameters():
			raise "wrong number of parameters"
		print voltages
		self.bimorph.asynchronousMoveTo(voltages)
		while self.bimorph.isBusy():
			sleep(1)
		if not self.bimorph.isAt(voltages):
				raise "bimorphs bokrne"

	def dothescan(self, fname, step):
		message="d2diode low or topup imminet -- waiting"
		while d2diode.getPosition() < 1.0 or topup.getPosition() < 5.0:
			if not message == None:
				print message
				message=None
			sleep(6)
			#Feedback().reset()
		ds=DataSet(768,1024,self.cd.cagetArrayDouble())
		saver=gda.analysis.io.PNGSaver("%s/images/camera %s %02d.png" % (self.dir, fname, step))
		sfh=ScanFileHolder()
		sfh.addDataSet("d10camera",ds)
		saver.saveFile(sfh)
		return self.integrator.execute(ds)[0]

	def eval(self, parameters):
		if len(parameters) != self.getNumberOfParameters():
			raise "wrong number of parameters"
		self.setVoltages(self.bimorphscale(parameters))
		value=self.measure(parameters)	
		print "evaluated to "+value.__str__()," ", parameters
		return value

	def measure(self,parameters):
		# for testing, and as an initial quick method, try the scan multiple times
		notimes=20
		sfh=ScanFileHolder()
		profile = []
		values = []
		fname="%d%02d%02d %02d:%02d:%02d" % time.localtime()[:6]
		for p in parameters:
			fname+=" %1.4f" % p
		for i in range(notimes):
			integrated = self.dothescan(fname, i)
			integrated.__isub__( (integrated.min() + integrated[0] + integrated[len(integrated)-1])/3 )
			values.append(self.scrutinise(integrated)/ringcurrent.getPosition())
			profile += [integrated]
			sfh.addDataSet("profile%02d" % i, integrated)
		# for the purpose of checking, lets plot this to the screen to make sure it looks ok.
		RCPPlotter.plot("Plot 1", DataSet.arange(len(profile[0])), profile)
		values.sort()
		saver=gda.analysis.io.AsciiScanFileHolderSaver("%s/scans/%s.dat" % (self.dir, fname))
		saver.saveFile(sfh)		
		return 1/sum(values[5:-3])

	def scrutinise(self,y):
		result = 0
		maxPos = y.maxPos()[0]
		length = len(y)
		for i in range(length):
			weight=1-abs((i-float(maxPos))/(1*length))**0.7
			result += y[i]*weight
		return result

	def batchEval(self, parameterList):
		results=[]
		for p in parameterList:
			results.append(self.eval(p))
		return results

	def bimorphscale(self, parameters):
		inmin=0.0
		inmax=1.0
		min=-400.0
		max=400.0
		maxdiff=500.0
		para=[]
		for i in range(len(parameters)):
			val=parameters[i]
			if val > inmax:
				raise "parameter too big"
			if val < inmin: 
				raise "parameter too small"
			para.append((val-inmin)/(inmax-inmin)*(max-min)+min)
		
		diffs=[]
		for i in range(0,len(para)-1,1):
			diffs.append(para[i]-para[i+1])
		korrs=[[]]
		for i in range(0,len(para)-1,1):
			diff=diffs[i]
			korr=0.0
			if abs(diff)>(maxdiff/3.0):
				korr=(abs(diff)-(maxdiff/3.0))*3.0/5.0
				korr=korr*diff/abs(diff)/2.0
			korrs[i].append(-korr)
			korrs.append([korr])

		for i in range(0,len(para),1):
			sign=1.0
			sum=0.0
			for j in korrs[i]:
				sign*=j
				sum+=j
			if len(korrs[i]) == 1:
				#boundary element
				para[i]=para[i]+(sum*1)
			elif sign > 0:
				#both corrections same way
				maxtouse=0
				for j in korrs[i]:
					if abs(j) > abs(maxtouse):
						maxtouse=j
				para[i]=para[i]+maxtouse
			else:
				para[i]=para[i]+sum
		return para
