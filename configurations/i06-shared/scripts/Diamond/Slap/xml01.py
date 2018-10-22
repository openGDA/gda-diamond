
#XML handling

import xml.dom.minidom   

doc=xml.dom.minidom.Document()

#The base element: GDA
gda=doc.createElementNS("http://www.diamond.ac.uk/dasc/gda", "GDA")
doc.appendChild(gda)

doc.childNodes
doc.childNodes[0] #<DOM Element: GDA at 0x1>
doc.childNodes[0].namespaceURI #'http://www.diamond.ac.uk/dasc/gda'
doc.childNodes[0].localName #'GDA'


#Address element:
address=doc.createElementNS("http://www.diamond.ac.uk/dasc/gda", "Address")
gda.appendChild(address)

doc.childNodes[0].childNodes[0] #<DOM Element: Address at 0x3>
doc.childNodes[0].childNodes[0].localName #'Address'

addressText = doc.createTextNode("Diamond House, OX11 0DE, Oxon, UK")
address.appendChild(addressText)
doc.childNodes[0].childNodes[0].childNodes[0].nodeValue


#address.getAttributeNS("http://www.diamond.ac.uk/dasc/gda", "name")


team=doc.createElement("team");
gda.appendChild(team)

member=doc.createElement("member");
member.setAttribute("name", "Alan Johnson");
member.setAttribute("id", "0001");
member.setAttribute("Age", "35");
member.setAttribute("Gendar", "M");
team.appendChild(member)

member=doc.createElement("member");
member.setAttribute("name", "Bob Kinder");
member.setAttribute("id", "0002");
member.setAttribute("Age", "31");
member.setAttribute("Gendar", "M");
team.appendChild(member)

member=doc.createElement("member");
member.setAttribute("name", "Cath Lott");
member.setAttribute("id", "0002");
member.setAttribute("Age", "25");
member.setAttribute("Gendar", "F");
team.appendChild(member)

#print
print doc.toprettyxml(indent="\t")

#Write to file
f=open("b.xml", 'w')
doc.writexml(f);
f.close()



#Open a xml file:

ngf=xml.dom.minidom.parse('b.xml')
main=ngf.getElementsByTagName('GDA');
print main[0].localName;

