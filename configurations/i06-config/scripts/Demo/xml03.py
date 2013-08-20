import sys,string

from xml.dom import minidom, Node;


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




doc = minidom.parse("people.xml")

#print doc.toprettyxml(indent="    ");#prettier print

######################################################
#2 To walk through the dom and access the child nodes

rootNode = doc.documentElement
walk(rootNode, outFile=sys.stdout, level=0);

doc.getElementsByTagName('interest')[2].childNodes[0].nodeValue
doc.getElementsByTagName('interest')[2].firstChild.nodeValue

print doc.getElementsByTagName('person')[2].firstChild.toprettyxml()

vs=doc.getElementsByTagName('person')[2].firstChild.lastChild.toxml()
pirnt vs

doc.getElementsByTagName('person')[0].firstChild.lastChild.data


