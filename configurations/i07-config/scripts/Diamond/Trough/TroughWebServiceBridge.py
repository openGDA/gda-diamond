from time import sleep

from java.lang import StringBuilder, Exception;
from java.io import File, BufferedReader, InputStreamReader;
from java.net import URL;

from javax.xml.parsers import DocumentBuilderFactory;
from javax.xml.parsers import DocumentBuilder;
from javax.xml.transform.dom import DOMSource
from javax.xml.transform import Transformer, TransformerFactory
from javax.xml.transform.stream import StreamResult

import __main__ as gdamain

#The Class for creating a WebService based device to control the Nima Langmuir-Blodgett Trough
class NimaLangmuirBlodgettTroughBridgeClass(object):
	
	NLBT_CONTROL_MODE = {"SPEED"   : 0,
						 "PRESSURE": 1,
						 "AREA"	: 2 };


	def __init__(self, name, webServiceHostName, dataSocketHostName):
		self.name = name;
		self.wsHost=None;
		self.dsHost=None;
		self.baseURL=None;
		self.timeout = 5000
		self.setHosts(webServiceHostName, dataSocketHostName)

		self.mode = 2;
		self.speed = 30.0;
		self.pressure = None;
		self.area = None;
		self.temperature = None;
		self.time = None;
		self.pressureB = None;
		self.areaB = None;
		self.spot = None;
		
		
		self.minArea=0;
		self.maxArea=900;
		self.minSpeed=5;
		self.maxSpeed=100;
		
		self.running=False;
		
		self.deadbandArea = 1.0;
		self.deadbandPressure = 0.1;
		self.onTarget = False;
		
		self.speedCorrectionFactor=1.0;
		
	def	getSpeedCorrectionFactor(self):
		return self.speedCorrectionFactor;
	
	def setSpeedCorrectionFactor(self, newFactor):
		self.speedCorrectionFactor = newFactor;

	def __del__(self):
		return;

	def setHosts(self, webServiceHostName, dataSocketHostName):
		self.wsHost = webServiceHostName;
		self.dsHost = dataSocketHostName;
		#Example url for reading all: 'http://diamrd2316.diamond.ac.uk:8080/TroughBridgeWS/BridgeWS_ReadAll/localhost''
		self.baseURL = 'http://' + self.wsHost + ':8080/TroughBridgeWS';
		
		return self.baseURL;

	
	'''To get a xml doc from url using pure Java approach'''
	def getDoc(self, url):
		doc, connection, stream = None, None, None;
		try:
			newurl = URL( url );
			connection = newurl.openConnection()
			connection.setConnectTimeout(self.timeout)
			connection.connect()
			dbf = DocumentBuilderFactory.newInstance();
			db = dbf.newDocumentBuilder();
			stream = connection.getInputStream()
			doc = db.parse( stream );
		except Exception, e:
			print 'Failed to reach trough server, please check it is running.'
			print 'Details', str(e);
		finally:
			try :
				if stream is not None :
					stream.close()
			except Exception, e:
				raise e
			finally :
				connection.disconnect()
			
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

	#Web service call
	#Example url for reading all: 'http://diamrd2316.diamond.ac.uk:8080/TroughBridgeWS/BridgeWS_ReadAll/localhost'
	def bridgeWS_ReadAll(self):
		requestURL = self.baseURL + '/BridgeWS_ReadAll/' + self.dsHost
		doc = self.getDoc(requestURL);
		
		value = self.getValueFromDoc(doc, 0)
		temp=float(value);
	
		value = self.getValueFromDoc(doc, 1)
		ti=float(value);
	
		value = self.getValueFromDoc(doc, 2)
		piA=float(value);
	
		value = self.getValueFromDoc(doc, 3)
		spot=float(value);
	
		value = self.getValueFromDoc(doc, 4)
		piB=float(value);
		
		value = self.getValueFromDoc(doc, 5)
		area=float(value);
		
		value = self.getValueFromDoc(doc, 6)
		areaB=float(value);
		
		value = self.getValueFromDoc(doc, 7)
		status=int(value);
	
		return [status, area, piA, temp, ti, areaB, piB, spot];
	
	#http://diamrd2316.diamond.ac.uk:8080/TroughBridgeWS/BridgeWS_SetMode/1/diamrd2316.diamond.ac.uk 
	def bridgeWS_SetMode(self, newValue):
		requestURL = self.baseURL + '/BridgeWS_SetMode/'+str(newValue)+'/' + self.dsHost
		doc = self.getDoc(requestURL);
	
		value = self.getValueFromDoc(doc, 0)
		success = (int(value)==0);
	
		return success;

	#http://diamrd2316.diamond.ac.uk:8080/TroughBridgeWS/BridgeWS_SetStart/1/diamrd2316.diamond.ac.uk 
	def bridgeWS_SetStart(self, newValue):
		requestURL = self.baseURL + '/BridgeWS_SetStart/'+str(newValue)+'/' + self.dsHost
		doc = self.getDoc(requestURL);
	
		value = self.getValueFromDoc(doc, 0)
		success = (int(value)==0);
	
		return success;

	#http://diamrd2316.diamond.ac.uk:8080/TroughBridgeWS/BridgeWS_SetStop/1/diamrd2316.diamond.ac.uk 
	def bridgeWS_SetStop(self, newValue):
		requestURL = self.baseURL + '/BridgeWS_SetStop/'+str(newValue)+'/' + self.dsHost
		doc = self.getDoc(requestURL);
	
		value = self.getValueFromDoc(doc, 0)
		success = (int(value)==0);
	
		return success;

	#http://diamrd2316.diamond.ac.uk:8080/TroughBridgeWS/BridgeWS_SetArea/100/diamrd2316.diamond.ac.uk 
	def bridgeWS_SetArea(self, newValue):
		requestURL = self.baseURL + '/BridgeWS_SetArea/'+str(newValue)+'/' + self.dsHost
		doc = self.getDoc(requestURL);
	
		value = self.getValueFromDoc(doc, 0)
		success = (int(value)==0);
	
		return success;

	#http://diamrd2316.diamond.ac.uk:8080/TroughBridgeWS/BridgeWS_SetPressure/4/diamrd2316.diamond.ac.uk 
	def bridgeWS_SetPressure(self, newValue):
		requestURL = self.baseURL + '/BridgeWS_SetPressure/'+str(newValue)+'/' + self.dsHost
		doc = self.getDoc(requestURL);
	
		value = self.getValueFromDoc(doc, 0)
		success = (int(value)==0);
	
		return success;

	#http://diamrd2316.diamond.ac.uk:8080/TroughBridgeWS/BridgeWS_SetSpeed/50/diamrd2316.diamond.ac.uk 
	def bridgeWS_SetSpeed(self, newValue):
		requestURL = self.baseURL + '/BridgeWS_SetSpeed/'+str(newValue)+'/' + self.dsHost
		doc = self.getDoc(requestURL);
	
		value = self.getValueFromDoc(doc, 0)
		success = (int(value)==0);
	
		return success;

	#General trough interface:
	def update(self):
		all = self.bridgeWS_ReadAll();
		retry=0;
		while( all[0] == 1 ): # Error status, try again
			sleep(0.1);
			all = self.bridgeWS_ReadAll();
			retry += 1;
			if retry == 10:
				print "Readback operation failed ten times. Please check all servers running.";
				break;
		[self.area, self.pressure, self.temperature, self.time, self.areaB, self.pressureB, self.spot]=all[1:];
		return [self.area, self.pressure, self.temperature, self.time, self.areaB, self.pressureB, self.spot];

	def isRunning(self):
		return self.running;
	
	def setAreaLimits(self, low, high):
		self.minArea, self.maxArea = low, high;

	def getAreaLimits(self):
		return [self.minArea, self.maxArea];
	
	def setSpeedLimits(self, low, high):
		self.minSpeed, self.maxSpeed = low, high;

	def getSpeedLimits(self):
		return [self.minSpeed, self.maxSpeed];

	def getMode(self):
		print "Trough Mode: " + self.NLBT_CONTROL_MODE.keys()[self.NLBT_CONTROL_MODE.values().index( self.mode )]
		return self.mode;
		
	def setMode(self, newMode):
		if newMode in self.NLBT_CONTROL_MODE.values():
			self.mode = newMode;
		elif newMode.upper() in self.NLBT_CONTROL_MODE.keys():
			self.mode =self.NLBT_CONTROL_MODE[ newMode.upper() ];
		else:
			print "Please use the right mode: 'speed/pressure/area' or 0/1/2. ";
			return;
		
		self.bridgeWS_SetMode(self.mode);

	def setArea(self, newValue):
		self.bridgeWS_SetArea(newValue);
		sleep(1);
		
	def getArea(self):
		self.update();
		return self.area;
		
	def setPressure(self, newValue):
		self.bridgeWS_SetPressure(newValue)

	def getPressure(self):
		self.update();
		return self.pressure;
		
	def setSpeed(self, newValue):
		self.speed = newValue;
		self.bridgeWS_SetMode(self.NLBT_CONTROL_MODE['SPEED'])
		self.bridgeWS_SetSpeed(newValue);
		
	def getSpeed(self):
		return self.speed;

	def getTemperature(self):
		self.update();
		return self.temperature;

	def readValues(self):
		return self.update();

	def start(self):
		if self.running:
			return;

		self.bridgeWS_SetStart(1);
		sleep(0.2);
		self.bridgeWS_SetStart(0);

		self.running = True;
		
	def stop(self):
		self.bridgeWS_SetStop(1);
		sleep(0.2);
		self.bridgeWS_SetStop(0);
		self.running = False;

	def sync(self):
		self.update();
		self.setArea(self.area);

	def getStatus(self):
		return True;

	def asynchronousAreaMoveTo(self,newArea):
		self.setMode(self.NLBT_CONTROL_MODE['AREA']);
		self.setArea(newArea);
		if not self.isRunning():
			self.start();

	def synchronousAreaMoveTo(self,newArea):
		self.onTarget = False;
		self.asynchronousAreaMoveTo(newArea);
		while( not self.onTarget ):
			self.onTarget = abs(newArea - self.getArea()) <= self.deadbandArea;
			sleep(1)

##Trough using WebService over LabVIEW
##Example url for reading all: 'http://diamrd2316.diamond.ac.uk:8080/TroughBridgeWS/BridgeWS_ReadAll/localhost''

#wsHost='diamrd2316.diamond.ac.uk'
##wsHost='i07-solo.diamond.ac.uk'

#dsHost='diamrd2316.diamond.ac.uk'
##dsHost='i07-pw001.diamond.ac.uk'


