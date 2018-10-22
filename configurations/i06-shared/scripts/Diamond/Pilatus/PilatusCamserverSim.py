from time import sleep
import cPickle as pickle
import threading;
import socket;
import zipfile;
import sys;

#sys.path.append("/home/xr56/Dev/gdaDev/gda-config-local/localBase/scripts");

from Diamond.Pilatus.ImageProducer import ImageProducerClass;
from Diamond.Pilatus.PilatusInfo import PilatusInfo;


#Method one: using the Python Threading package
class ServingPythonThread(threading.Thread):
	parseLock=threading.Lock();
	id=0;
	
	def __init__(self, newSocket, type):
		threading.Thread.__init__(self);
		self.myid=ServingPythonThread.id;
		ServingPythonThread.id += 1;

		self.hostSocket = newSocket;
		self.imageProducer=ImageProducerClass(type);

		self.exposureTime = 0;
		self.status = PilatusInfo.DETECTOR_STATUS_STANDBY;

#		self.filePath = None;
#		self.fileName = 'simPilatus';
		self.fileFormat = "%s%s%4.4d.tif";
		self.numberOfImages = 1;
		
		(self.connection, address) = self.hostSocket.accept() # connection is a new socket
		print 'New Python thread to deal with Pilatus client from ', address;
	
		
	def run(self):
		while True:
			data = self.connection.recv(1024) # receive up to 1K bytes
			if not data:# return zero byte means connection closed by client
				print "Client closed";
				break;
			print 'Received -> ', data;
	
			td=data.strip(' \n\r');
	
			if td != "quit": #client send quit
				ServingPythonThread.parseLock.acquire();
				reply = self.parse(td);
				ServingPythonThread.parseLock.release();
				if reply[0] != None:
					self.connection.send(reply[0]);
				if reply[1] != None:
					sleep(self.exposureTime);
					self.connection.send(reply[1]);
			else:
				print "Client quitting";
				break;
		self.connection.close();
		
	def parse(self, inStr):
		reply = [None, None];
		rlist = inStr.split(' ',1);
		
		if rlist[0] == 'menu':
			reply[0] = 'Unimplemented command:' + inStr;
		elif rlist[0] == 'delay':
			reply[0] = 'Unimplemented command:' + inStr;
		elif rlist[0] == 'nexpframe':
			reply[0] = 'Unimplemented command:' + inStr;
		elif rlist[0] == 'extenable':
			reply[0] = 'Unimplemented command:' + inStr;
		elif rlist[0] == 'expperiod':
			reply[0] = 'Unimplemented command:' + inStr;
		elif rlist[0] == 'dcb_init':
			reply[0] = 'Unimplemented command:' + inStr;
		
		elif rlist[0] == 'exptime':
			if len(rlist) == 1:
				reply[0] = '15 OK   Exposure time set to: ' + str(self.exposureTime) + ' sec.' + CamServerSimClass.TERMINATER_18
			else:
				self.exposureTime=float(rlist[1]);
				reply[0] = '15 OK   Exposure time set to: ' + str(self.exposureTime) + ' sec.' + CamServerSimClass.TERMINATER_18

		elif rlist[0] == 'exposure':
			if len(rlist) == 2:
				#ss=self.imageProducer.getNextImage(rlist[1]);
				reply[0] = '15 OK   Starting 3.000000 second background: 2009/Jul/06 12:10:01.058 '  + CamServerSimClass.TERMINATER_18;
				reply[1] = '7 OK ' + self.imageProducer.getNextImage(rlist[1]) + CamServerSimClass.TERMINATER_18;
			else:
				reply[0]=self.imageProducer.getNextImage();
			print 'Single image created: ';
			

		elif rlist[0] == 'exttrigger':
			if len(rlist) == 2:
				for i in range(self.numberOfImages):
					ss=self.imageProducer.getNextImage(rlist[1] + "_%05.0f" % (i+1));
			else:
				for i in range(self.numberOfImages):
					ss=self.imageProducer.getNextImage();
				
			reply[0] = 'OK';

		elif rlist[0] == 'imgpath':
			if len(rlist) == 1:
				reply[0] = '10 OK ' + self.imageProducer.getFilePath()+ CamServerSimClass.TERMINATER_18;
			else:
				self.imageProducer.setFilePath(rlist[1]);
				reply[0] = '10 OK ' + self.imageProducer.getFilePath() + CamServerSimClass.TERMINATER_18;
				
		elif rlist[0] == 'nimages':
			if len(rlist) == 1:
				reply[0] = '15 OK N images (frames) set to: ' + str(self.numberOfImages) + CamServerSimClass.TERMINATER_18;
			else:
				self.numberOfImages=int(float(rlist[1]));
				reply[0] = '15 OK N images (frames) set to: ' + str(self.numberOfImages)  + CamServerSimClass.TERMINATER_18;
				#reply = 'OK';

		else:
			reply[0] = 'Unknown Command: ' + inStr;

		return reply;


class CamServerSimClass(object):
#	terminators = '\n\x15\x18';
	TERMINATER_15 = '\x15';
	TERMINATER_18 = '\x18';
	TERMINATER = '\n';

	def __init__(self, hostName, port, type):
		
		self.hostName=hostName;
		self.port=port;
		self.type=type;

		self.mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM); # create a TCP socket
		self.mySocket.bind((self.hostName, self.port));         # bind it to the server port
		self.mySocket.listen(5);                      # allow 5 simultaneous

		self.threadList = [];

	def start(self):
		for i in range(2):#Up to two clients can connect to this server
			# wait for next client to connect
			spt=ServingPythonThread(self.mySocket, self.type);
			self.threadList.append(spt);
			spt.start();

	def join(self):
		#wait until all serving thread done
		for st in self.threadList:
			st.join();#join the thread with the main thread so that the main thread can finish only when all jointed threads terminated. 

	def shutdown(self):
		self.mySocket.close();
		print "Bye Bye";

	def setout(self):
		self.start();
		self.join();
		self.shutdown();


#hostName = socket.gethostname();
#portNumber = 2741;
#camserver=CamServerSimClass(hostName, portNumber, PilatusInfo.PILATUS_MODEL_100K);
#camserver.setout();
