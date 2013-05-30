
import xmlrpclib;

from xmlrpclib import Server;
from xmlrpclib import ServerProxy;

server = Server("http://diamrl5067.diamond.ac.uk/xml-rpc/server.php");
#server = ServerProxy("http://diamrl5067.diamond.ac.uk/xml-rpc/server.php");
#print server.system.listMethods();

serialNumber = server.FindNext(0)

print "The serial number: " + str(serialNumber);


