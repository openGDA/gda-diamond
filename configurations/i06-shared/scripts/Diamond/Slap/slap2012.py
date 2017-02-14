

from xml.dom import minidom, Node;
from pprint import pprint

import sys,string
import urllib2



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
	return;


#LabViewWebService_URL = 'http://diamrl5068.diamond.ac.uk:8080/SlapWebServices'
#LabViewWebService_URL = 'http://i06-ws006.dc.diamond.ac.uk:8080/SlapWebServices'

#LabViewWebService_URL = 'http://172.23.106.130:8080/SlapWebServices'
LabViewWebService_URL = 'http://172.23.7.62:8080/SlapWebServices'

LabViewWebService_NS = 'http://xml.weather.yahoo.com/ns/rss/1.0' #xmlns:yweather="http://xml.weather.yahoo.com/ns/rss/1.0"

#http://diamrl5068.diamond.ac.uk:8080/SlapWebServices/InitService
def callInitService():
	requestURL = LabViewWebService_URL + '/InitService'
	doc = minidom.parse( urllib2.urlopen(requestURL) )

	print "-----------------------------------------"
	walk(doc.documentElement, outFile=sys.stdout, level=0);

	print "-----------------------------------------"
	value = doc.getElementsByTagName('Terminal')[0].childNodes[1].firstChild.nodeValue
	fpsEnable=int(value);

	value = doc.getElementsByTagName('Terminal')[1].childNodes[1].firstChild.nodeValue
	loopGain=float(value);

	value = doc.getElementsByTagName('Terminal')[2].childNodes[1].firstChild.nodeValue
	harmPhaseShift=float(value);

	value = doc.getElementsByTagName('Terminal')[3].childNodes[1].firstChild.nodeValue
	fundPhaseShift=float(value);

	value = doc.getElementsByTagName('Terminal')[4].childNodes[1].firstChild.nodeValue
	delay=float(value);

	return [fpsEnable, loopGain, harmPhaseShift, fundPhaseShift, delay];


#http://diamrl5068.diamond.ac.uk:8080/SlapWebServices/StopService
def callStopService():
	requestURL = LabViewWebService_URL + '/StopService'
	doc = minidom.parse( urllib2.urlopen(requestURL) )

	print "-----------------------------------------"
	walk(doc.documentElement, outFile=sys.stdout, level=0);
	return



#http://diamrl5068.diamond.ac.uk:8080/SlapWebServices/SetValueService/Delay/FundPhaseShift/HarmPhaseShift/LoopGain
def callSetValueService(loopGain, harmPhaseShift, fundPhaseShift, delay):
	requestURL = LabViewWebService_URL + '/SetValueService/'+str(delay)+'/'+str(fundPhaseShift)+'/'+str(harmPhaseShift)+'/'+str(loopGain)
	doc = minidom.parse( urllib2.urlopen(requestURL) )
	print "-----------------------------------------"
	walk(doc.documentElement, outFile=sys.stdout, level=0);

	print "-----------------------------------------"
	value = doc.getElementsByTagName('Terminal')[0].childNodes[1].firstChild.nodeValue
	de=float(value);

	value = doc.getElementsByTagName('Terminal')[1].childNodes[1].firstChild.nodeValue
	fps=float(value);

	value = doc.getElementsByTagName('Terminal')[2].childNodes[1].firstChild.nodeValue
	hps=float(value);

	value = doc.getElementsByTagName('Terminal')[3].childNodes[1].firstChild.nodeValue
	lg=float(value);

	return [lg, hps, fps, de];


#http://diamrl5068.diamond.ac.uk:8080/SlapWebServices/SetValueService/Delay/FundPhaseShift/HarmPhaseShift/LoopGain
def callSingleSetService(fundEnable, loopGain, harmPhaseShift, fundPhaseShift, delay):
	requestURL = LabViewWebService_URL + '/SingleSetService/'+str(fundEnable)+'/'+str(delay)+'/'+str(fundPhaseShift)+'/'+str(harmPhaseShift)+'/'+str(loopGain)
	doc = minidom.parse( urllib2.urlopen(requestURL) )
	print "-----------------------------------------"
	walk(doc.documentElement, outFile=sys.stdout, level=0);

	print "-----------------------------------------"
	value = doc.getElementsByTagName('Terminal')[0].childNodes[1].firstChild.nodeValue
	de=float(value);

	value = doc.getElementsByTagName('Terminal')[1].childNodes[1].firstChild.nodeValue
	fps=float(value);

	value = doc.getElementsByTagName('Terminal')[2].childNodes[1].firstChild.nodeValue
	hps=float(value);

	value = doc.getElementsByTagName('Terminal')[3].childNodes[1].firstChild.nodeValue
	lg=float(value);

	value = doc.getElementsByTagName('Terminal')[4].childNodes[1].firstChild.nodeValue
	fpsEnable=int(value);

	return [fpsEnable, lg, hps, fps, de];


#http://diamrl5068.diamond.ac.uk:8080/SlapWebServices/ReadOnlyService
def callReadOnlyService():
	requestURL = LabViewWebService_URL + '/ReadOnlyService'
	doc = minidom.parse( urllib2.urlopen(requestURL) )
	print "-----------------------------------------"
	walk(doc.documentElement, outFile=sys.stdout, level=0);

	print "-----------------------------------------"
	value = doc.getElementsByTagName('Terminal')[0].childNodes[1].firstChild.nodeValue
	fpsEnable=int(value);

	value = doc.getElementsByTagName('Terminal')[1].childNodes[1].firstChild.nodeValue
	lg=float(value);

	value = doc.getElementsByTagName('Terminal')[2].childNodes[1].firstChild.nodeValue
	hps=float(value);

	value = doc.getElementsByTagName('Terminal')[3].childNodes[1].firstChild.nodeValue
	fps=float(value);

	value = doc.getElementsByTagName('Terminal')[4].childNodes[1].firstChild.nodeValue
	de=float(value);

	return [fpsEnable, lg, hps, fps, de];

def setFPS(newFPS):
	[fpsEnable, lg, hps, fps, de] = callReadOnlyService()
	callSingleSetService(fpsEnable, lg, hps, newFPS, de)
	
def getFPS():
	[fpsEnable, lg, hps, fps, de] = callReadOnlyService()
	return fps;


def fpsToTime(offset):
	
	fps=getFPS()
	time=13*(float(fps-offset)/65536.0)
	return time;

def timeToFps(time, offset):
	
	fps = int( (time/13.0)*65536+offset )
	setFPS(fps)
	return fps;

#callInitService()

#callSingleSetService(50, 12345, 54321,15)

#callReadOnlyService()
#callStopService()

#setFPS(10010)

