
from time import sleep;
import sys;
import socket;

sys.path.append("/home/xr56/Dev/gdaDev/gda-config-local/localBase/scripts");
#sys.path.append("/home/xr56/Dev/gdaDev/gda-config/i07/scripts");
#sys.path.append("/dls/i07/software/gda_versions/gdaDev/dev_gdaConfig/i07/scripts");
#sys.path.append("/home/cop98/Dev/gdaDev/gda-config-local/localBase/scripts");

from Diamond.Comm.SocketDevice import SocketDeviceClass, SingleSessionSocketDeviceClass;
from Diamond.Comm.JavaSocketDevice import JavaSocketDeviceClass;
from Diamond.Comm.SocketDevice import SocketError;

#serverHost = 'localhost';
serverHost = socket.gethostname();

serverPort = 41234;

#sc = SocketDeviceClass(serverHost, serverPort);
sc = JavaSocketDeviceClass(serverHost, serverPort);
sc.setTimeout(5)

while True:
	strInput = raw_input("Send: ");
	if strInput == 'quit':
		print 'Send out --> ' + strInput;
		sc.send(strInput);
		break;
	try:
		print 'Send out --> ' + strInput;
#		reply = sc.sendAndReply(strInput);
		reply = sc.resilientSendAndReply(strInput);
		print "Received <-- " + repr(reply);
	except SocketError:
		print "Catch a Timeout Error";
		
		

