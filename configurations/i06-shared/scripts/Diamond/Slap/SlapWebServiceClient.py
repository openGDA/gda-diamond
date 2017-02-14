

from xml.dom import minidom, Node;
from pprint import pprint
from time import sleep

import sys,string
import urllib2


from java.lang import StringBuilder, Exception;
from java.io import File, BufferedReader, InputStreamReader;
from java.net import URL;

#from org.w3c.dom import Document;

from javax.xml.parsers import DocumentBuilderFactory;
from javax.xml.parsers import DocumentBuilder;
from javax.xml.transform.dom import DOMSource
from javax.xml.transform import Transformer, TransformerFactory
from javax.xml.transform.stream import StreamResult


from gda.device.scannable import ScannableBase

class SlapClass(object):
	def __init__(self, wsURL=None):
		self.baseURL=wsURL;
		
		self.timebase = 13;
		self.offset=0;
		self.llm = 0.0;
		self.hlm = 14000;
		self.maxStep=100;
		self.phase2delay_ce=[]
		self.delay2phase_ce=[]
		
	def setMaxStep(self, maxStep):
		self.maxStep=int(maxStep);
		print "Maxium steps in phase is set to %d" %(self.maxStep);
		
		
	def walk(self, parentNode, outFile, level):
		for node in parentNode.childNodes:
			if node.nodeType == Node.ELEMENT_NODE:
				#The element node name:
				self.printLevel(outFile, level);
				outFile.write('Element: %s\n' %node.nodeName);
				
				#Iterate over each attribute name and value in the node:
				attrs = node.attributes;
				for attrName in attrs.keys():
					attrValue=attrs.get(attrName).nodeValue;
					self.printLevel(outFile, level+2)
					outFile.write('Attribute -- Name: %s Value: %s\n' %(attrName, attrValue))
				#walk over any text nodes in the current node:
				content=[];
				for child in node.childNodes:
					if child.nodeType == Node.TEXT_NODE:
						content.append(child.nodeValue);
				if content:
					strContent = string.join(content)
					self.printLevel(outFile, level)
					outFile.write('Content: "')
					outFile.write(strContent)
					outFile.write('"\n')
	
	
			#Walk the child nodes iteratelly
			self.walk(node, outFile, level+1)
	
	
	def printLevel(self, outFile, level):
		for idx in range(level):
			outFile.write('    ');
	
	
	def getElements(self):
		return;
	
	def setHost(self, hostName):
		self.baseURL = 'http://' + hostName +':8080/SlapWebServices';
		return self.baseURL;
	
	'''To read the xml response via Java HttpURLConnection'''
	def getDoc(self, url):
		doc=None;
		try:
			responseBuilder = StringBuilder();
			
			newurl = URL( url );
			conn = newurl.openConnection();
			
			rd = BufferedReader( InputStreamReader(conn.getInputStream()) );
			
			line = rd.readLine();
			while line != None:
				responseBuilder.append(line + '\n');
				line = rd.readLine();
			rd.close();
		except Exception, e:
			print 'Failed to reach a server.'
			print 'Details', str(e);
			return doc;
			
		txt=responseBuilder.toString();
		doc = minidom.parseString( txt )
		return doc;
	
	'''To read the xml response via Python urllib2. 
		For some reason the connection can not be closed which leads to "Too man file open" Error'''
	def getDocOld(self, url):
		doc=None;
		try:
			response = urllib2.urlopen(url)
		except urllib2.HTTPError, e:
			print 'The server couldn\'t fulfill the request.'
			print 'Error code: ', e.code
		except urllib2.URLError, e:
			print 'We failed to reach a server.'
			print 'Reason: ', e.reason
		else:
#			print "URL open OK"
			doc = minidom.parse( response );
			response.close();
			response=None;
				
		return doc;
		
	'''The xml file returned:
	<Response>
		<Terminal>
			<Name>FundamentalEnableFeedback</Name>
			<Value>1</Value>
		</Terminal>
		<Terminal>
			<Name>LoopGainFeedback</Name>
			<Value>79</Value>
		</Terminal>
		<Terminal>
			<Name>HarmPhaseShiftFeedback</Name>
			<Value>39754</Value>
		</Terminal>
		<Terminal>
			<Name>FundPhaseShiftFeedback</Name>
			<Value>42630</Value>
		</Terminal>
		<Terminal>
			<Name>DelaySetValueFeedback</Name>
			<Value>0.000000</Value>
		</Terminal>
	</Response>	
	'''
	def getValueFromDoc(self, doc, index):
		value = doc.getElementsByTagName('Terminal')[index].childNodes[1].firstChild.nodeValue
		return value;
		
	def callInitService(self):
		requestURL = self.baseURL + '/InitService'
		doc = self.getDoc(requestURL);
	
		value = self.getValueFromDoc(doc, 0)
		fpsEnable=int(value);
	
		value = self.getValueFromDoc(doc, 1)
		loopGain=float(value);
	
		value = self.getValueFromDoc(doc, 2)
		harmPhaseShift=float(value);
	
		value = self.getValueFromDoc(doc, 3)
		fundPhaseShift=float(value);
	
		value = self.getValueFromDoc(doc, 4)
		delay=float(value);
	
		return [fpsEnable, loopGain, harmPhaseShift, fundPhaseShift, delay];
	
	
	#http://diamrl5068.diamond.ac.uk:8080/SlapWebServices/StopService
	def callStopService(self):
		requestURL = self.baseURL + '/StopService'
		doc = self.getDoc(requestURL);
		return
	
	
	#http://diamrl5068.diamond.ac.uk:8080/SlapWebServices/SetValueService/Delay/FundPhaseShift/HarmPhaseShift/LoopGain
	def callSetValueService(self, loopGain, harmPhaseShift, fundPhaseShift, delay):
		requestURL = self.baseURL + '/SetValueService/'+str(delay)+'/'+str(fundPhaseShift)+'/'+str(harmPhaseShift)+'/'+str(loopGain)
		doc = self.getDoc(requestURL);
	
		value = self.getValueFromDoc(doc, 0)
		de=float(value);
	
		value = self.getValueFromDoc(doc, 1)
		fps=float(value);
	
		value = self.getValueFromDoc(doc, 2)
		hps=float(value);
	
		value = self.getValueFromDoc(doc, 3)
		lg=float(value);
	
		return [lg, hps, fps, de];
	
	
	#http://diamrl5068.diamond.ac.uk:8080/SlapWebServices/SetValueService/Delay/FundPhaseShift/HarmPhaseShift/LoopGain
	def callSingleSetService(self, fundEnable, loopGain, harmPhaseShift, fundPhaseShift, delay):
		requestURL = self.baseURL + '/SingleSetService/'+str(fundEnable)+'/'+str(delay)+'/'+str(fundPhaseShift)+'/'+str(harmPhaseShift)+'/'+str(loopGain)
		doc = self.getDoc(requestURL);
	
		value = self.getValueFromDoc(doc, 0)
		de=float(value);
	
		value = self.getValueFromDoc(doc, 1)
		fps=float(value);
	
		value = self.getValueFromDoc(doc, 2)
		hps=float(value);
	
		value = self.getValueFromDoc(doc, 3)
		lg=float(value);
	
		value = self.getValueFromDoc(doc, 4)
		fpsEnable=int(value);
	
		return [fpsEnable, lg, hps, fps, de];
	
	
	#http://diamrl5068.diamond.ac.uk:8080/SlapWebServices/ReadOnlyService
	def callReadOnlyService(self):
		requestURL = self.baseURL + '/ReadOnlyService'
		doc = self.getDoc(requestURL);
		
		value = self.getValueFromDoc(doc, 0)
		fpsEnable=int(value);
	
		value = self.getValueFromDoc(doc, 1)
		lg=float(value);
	
		value = self.getValueFromDoc(doc, 2)
		hps=float(value);
	
		value = self.getValueFromDoc(doc, 3)
		fps=float(value);
	
		value = self.getValueFromDoc(doc, 4)
		de=float(value);
	
		return [fpsEnable, lg, hps, fps, de];

	def setFps(self, newFPS):
		self.jogFps(newFPS);
		
	def setFpsOld(self, newFPS):
		if 0 <= newFPS <= 65535:
#			self.callSingleSetService(fpsEnable, lg, hps, newFPS, de)
			pass
		else:
			print "Wrong number"
		return;


	def jogFps(self, newFPS):
		'''To move fps in small steps'''
		[fpsEnable, lg, hps, fps, de] = self.callReadOnlyService()
		
		if 0 <= newFPS <= 65535:
			if newFPS > fps:#move upward
				newPositions=[p for p in range(fps+self.maxStep, newFPS, self.maxStep)]
				newPositions.append(newFPS);
			else:#move downward
				newPositions=[p for p in range(fps-self.maxStep, newFPS, -self.maxStep)]
				newPositions.append(newFPS);

			#jogging step by step
			for p in newPositions:
				self.callSingleSetService(fpsEnable, lg, hps, p, de);
				sleep(1);
		else:
			print "Target out of range."

		return;
		
	def getFps(self):
		[fpsEnable, lg, hps, fps, de] = self.callReadOnlyService()
		return fps;

	def getLocking(self):
		[fpsEnable, lg, hps, fps, de] = self.callReadOnlyService()
		return fpsEnable;
	
	
	def getDelayTime(self):
		fps=self.getFps()
#		time=self.timebase*(float(fps-self.offset)/65535.0);
		time=self.phaseToDelay(fps);		
		return time;
	
	def setDelayTime(self, time):
#		fps = int( (time*1.0/self.timebase)*65535.0+self.offset )
		fps = self.delayToPhase(time);
		self.setFps(fps)
		return fps;

	def setOffset(self, new_offset):
		self.offset=new_offset;
		return self.getLimits();

	def getOffset(self):
		return self.offset;
		
	def setTimebase(self, new_timebase):
		self.timebase=new_timebase;
		return self.getLimits();

	def getLimits(self):
#		self.llm = (0.0-self.offset)*self.timebase/65535.0;
#		self.hlm = (65535.0-self.offset)*self.timebase/65535.0;
		self.llm, self.hlm = 0.0, 14000.00;
		return [self.llm, self.hlm];

	def phaseToDelay(self, phase):
#		if phase < 2000:
#			print "Warning: for FPS less than 2000, the calculated delay time is not accurate!";
		
		#original calibration data 	
#		ce=[-314.54743880779006, 0.2178067078267, -4.42112289919133E-5, 6.23201260834173E-9, -4.56389485255816E-13, 1.87822227452686E-17, -4.38244545149381E-22, 5.74992260755205E-27, -3.95507764236028E-32, 1.10917614752542E-37];
		#new calibration data provided on 01/05/2012
#		ce=[-0.0058976070255, 1.31253880142145E-4, -2.26326432895618E-8, 3.53663784002266E-12, -2.63010486113614E-16, 1.04042843159956E-20, -2.16666613588553E-25, 2.26190976227321E-30, -9.58629545249244E-36, 2.90678349766489E-42];
		# new calibration from Thomas Forrest on 24 March 2016
#		ce=[250.936271279245, 13.6034842059384, 0.000656983157377759, -2.08799828953862E-06, 7.56552965866636E-10, -1.38088907300248E-13, 1.45660372818405E-17, -8.96012702104993E-22, 2.98195847300446E-26, -4.14229055816086E-31]
		delay=self.simple_polynomial(phase, self.phase2delay_ce)
		return delay;
					
				
	def delayToPhase(self, delay):
#		ce=[2091.8453502214797, 13.77230216629964, -6.26019393495315E-4, -1.43939298680241E-6, 6.07660339122771E-10, -1.20844686370414E-13, 1.37221846732618E-17,-9.06457446332099E-22, 3.23991999300214E-26, -4.83871779102917E-31];
#		ce=[-88.36914666723533, 12855.32380237554, 824.10592216745135, -1946.0535305088042, 664.20982780807435, -115.31870988361487, 11.61543948306145, -0.68333494362544, 0.02173576685147, -2.87621826209067E-4];
		# new calibration from Thomas Forrest on 24 March 2016
#		ce=[-23.9209961982287, 0.142095153813483, -2.32220343219571E-05, 3.20115386459306E-09, -2.14561959061541E-13, 7.62576731446377E-18, 1.35627681022786E-22, 9.97611012094939E-28, 4.20630921302906E-34, -2.84482027189109E-38]
		phase = self.simple_polynomial(delay, self.delay2phase_ce)
		return phase;

	'''
	ce=[c0, c1, c2, ...]
	y=c0 + c1*x + c2*x^2 + c3*x^3 + ...
	'''
	def simple_polynomial(self, x, ce):
		y=0.0;
		for n in range( len(ce) ):
			y += ce[n] * pow(x, n)
	
		return y;



class JavaSlapClass(SlapClass):
	def __init__(self, wsURL=None):
		SlapClass.__init__(self, wsURL);
	
	'''To get a xml doc from url using pure Java approach'''
	def getDoc(self, url):
		doc=None;
		try:
			newurl = URL( url );
			dbf = DocumentBuilderFactory.newInstance();
			db = dbf.newDocumentBuilder();
			doc = db.parse( newurl.openStream() );
		except Exception, e:
			print 'Failed to reach a server.'
			print 'Details', str(e);
			
		return doc;

	def getValueFromDoc(self, doc, index):
		value = doc.getElementsByTagName('Terminal').item(index).item(1).getFirstChild().getNodeValue()
		return value;
		
	def toFile(self, doc, filename):
		source = DOMSource(doc)
		file = File(filename);
		result = StreamResult(file);
		xformer = TransformerFactory.newInstance().newTransformer();
		
		xformer.transform(source, result);



class LaserPhaseDeviceClass(ScannableBase):
	def __init__(self, name, laserControl):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);
		self.setOutputFormat(["%6.3f"]);
		
		self.laser=laserControl;
		self.fps=None;
	
		
	def getPosition(self):
		self.fps=self.laser.getFps();
		return self.fps;

	def asynchronousMoveTo(self, new_position):
		self.laser.setFps(new_position)
	
	def isBusy(self):
		return False;

	def stop(self):
		pass

	def toString(self):
		ss=self.getName() + " : " + str(self.getPosition());
		return ss;

	def toFormattedString(self):
		ss=self.getName() + " : " + str(self.getPosition());
		return ss;



class LaserDelayDeviceClass(ScannableBase):
	def __init__(self, name, laserControl):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);
		self.setOutputFormat(["%6.3f"]);
		
		self.unit = 'ns';
		self.delay=None
		
		self.laser=laserControl;

	def getOffset(self):
		return self.laser.getOffset();

	def setOffset(self, new_offset):
		self.laser.setOffset(new_offset);


	def getPosition(self):
		self.delay=self.laser.getDelayTime();
		return self.delay

	def asynchronousMoveTo(self,new_position):
		self.laser.setDelayTime(new_position);
	
	def isBusy(self):
		return False;

	def stop(self):
		pass

	def toString(self):
		ss=self.getName() + " : " + str(self.getPosition()) + " " + self.unit + " (" + str(self.laser.getLimits()[1]) + " : "+ str(self.laser.getLimits()[0]) + ")";
		return ss;

	def toFormattedString(self):
		ss=self.getName() + " : " + str(self.getPosition()) + " " + self.unit + " (" + str(self.laser.getLimits()[1]) + " : "+ str(self.laser.getLimits()[0]) + ")";
		return ss;

class LaserLockingStateDeviceClass(ScannableBase):
	def __init__(self, name, laserControl):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);
		self.setOutputFormat(["%1.0d"]);
		
		self.laser=laserControl;
		self.locking=0;
	
		
	def getPosition(self):
		self.locking=self.laser.getLocking();
		return self.locking;

	def asynchronousMoveTo(self, new_position):
		pass;
	
	def isBusy(self):
		return False;

	def stop(self):
		pass

	def toString(self):
		ss=self.getName() + " : " + str(self.getPosition());
		return ss;

	def toFormattedString(self):
		ss=self.getName() + " : " + str(self.getPosition());
		return ss;


#Dell Laptop
#LabViewWebServiceURL = 'http://diamrl5068.diamond.ac.uk:8080/SlapWebServices'

#I06 Sony Laptop
#LabViewWebServiceURL = 'http://diamrl5098.diamond.ac.uk:8080/SlapWebServices'

#The value readback service for testing: http://diamrl5098.diamond.ac.uk:8080/SlapWebServices/ReadOnlyService

#laser=SlapClass(LabViewWebServiceURL);
#laser.setHost("diamrl5068.diamond.ac.uk");
#laser.setOffset(20000);

#laserphase=LaserPhaseDeviceClass("laserphase", laser)
#laserdelay=LaserDelayDeviceClass("laserdelay", laser)



