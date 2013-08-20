

from xml.dom import minidom, Node;
from pprint import pprint

import sys,string
import urllib

LabViewWebService_URL = 'http://diamrl5068.diamond.ac.uk:8080'
LabViewWebService_NS = 'http://xml.weather.yahoo.com/ns/rss/1.0' #xmlns:yweather="http://xml.weather.yahoo.com/ns/rss/1.0"
GEO_NS = 'http://www.w3.org/2003/01/geo/wgs84_pos#'    #xmlns:geo="http://www.w3.org/2003/01/geo/wgs84_pos#"


#http://diamrl5068.diamond.ac.uk:8080/Sum/DemoSum/5/9
def viadd(x, y):
	requestURL = LabViewWebService_URL + '/Sum/DemoSum/' + str(x) + '/' + str(y)

	doc = minidom.parse( urllib.urlopen(requestURL) )

	print "-----------------------------------------"
	walk(doc.documentElement, outFile=sys.stdout, level=0);

	print "-----------------------------------------"


	value = doc.getElementsByTagName('Terminal')[0].childNodes[1].firstChild.nodeValue
	
	result=float(value);

	return result;


#http://diamrl5068.diamond.ac.uk:8080/LoopStatus/DemoStatus/5/9
def vistatus(x, y):
	requestURL = LabViewWebService_URL + '/LoopStatus/DemoStatus/' + str(x) + '/' + str(y)

	doc = minidom.parse( urllib.urlopen(requestURL) )

	print "-----------------------------------------"
	walk(doc.documentElement, outFile=sys.stdout, level=0);

	print "-----------------------------------------"


	value = doc.getElementsByTagName('Terminal')[0].childNodes[1].firstChild.nodeValue
	
	result=float(value);

	return result;

def walk(parentNode, outFile, level):
	for node in parentNode.childNodes:
		if node.nodeType == Node.ELEMENT_NODE:
			#The element node name:
			printLevel(outFile, level);
			outFile.write('Element: %s\n' %node.nodeName);
			
			#Iterate over each attribute name and value in the node:
			attrs = node.attributes;
			for attrName in attrs.keys():
				attrValue=attrs.get(attrName).nodeValue;
				printLevel(outFile, level+2)
				outFile.write('Attribute -- Name: %s Value: %s\n' %(attrName, attrValue))
			#walk over any text nodes in the current node:
			content=[];
			for child in node.childNodes:
				if child.nodeType == Node.TEXT_NODE:
					content.append(child.nodeValue);
			if content:
				strContent = string.join(content)
				printLevel(outFile, level)
				outFile.write('Content: "')
				outFile.write(strContent)
				outFile.write('"\n')


		#Walk the child nodes iteratelly
		walk(node, outFile, level+1)


def printLevel(outFile, level):
	for idx in range(level):
		outFile.write('    ');


def getElements():
	pass



a=viadd(30,50);
print a;

b=vistatus(1,2)
print b;
