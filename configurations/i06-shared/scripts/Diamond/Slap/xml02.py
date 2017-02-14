
from xml.dom import minidom, Node

doc=minidom.Document()

#To add the root element: people
people=doc.createElementNS("http://www.mywebsite.org/people", "people")
doc.appendChild(people)

#To add an element: person 1:
person=doc.createElement('person')
people.appendChild(person);

person.setAttribute('id', '1')
person.setAttribute('value', 'abcd')
person.setAttribute('ratio', '3.2')

#To add an element with text inside:
name=doc.createElement('name');
name.appendChild(doc.createTextNode('Alberta'))
person.appendChild(name);

interest=doc.createElement('interest');
interest.appendChild(doc.createTextNode('gardening'));
person.appendChild(interest);

interest=doc.createElement('interest');
interest.appendChild(doc.createTextNode('reading'));
person.appendChild(interest);

category=doc.createElement('category')
category.appendChild(doc.createTextNode('5'));
person.appendChild(category)



#To add an element: person 2:
person=doc.createElement('person')
people.appendChild(person);

person.setAttribute('id', '2')

#To add an element with text inside:
name=doc.createElement('name');
name.appendChild(doc.createTextNode('Bernardo'))
person.appendChild(name);

interest=doc.createElement('interest');
interest.appendChild(doc.createTextNode('programming'));
person.appendChild(interest);

category=doc.createElement('category')
person.appendChild(category)

agent=doc.createElement('agent');
person.appendChild(agent);
firstname=doc.createElement('firstname')
firstname.appendChild(doc.createTextNode('Darren'))
lastname=doc.createElement('lastname')
lastname.appendChild(doc.createTextNode('Diddly'))
agent.appendChild(firstname);
agent.appendChild(lastname);


#To add an element: person 3:
person=doc.createElement('person')
people.appendChild(person);

person.setAttribute('id', '3')

#To add an element with text inside:
name=doc.createElement('name');
name.appendChild(doc.createTextNode('Charlie'))
person.appendChild(name);

interest=doc.createElement('interest');
interest.appendChild(doc.createTextNode('people'));
person.appendChild(interest);
interest=doc.createElement('interest');
interest.appendChild(doc.createTextNode('cats'));
person.appendChild(interest);
interest=doc.createElement('interest');
interest.appendChild(doc.createTextNode('dogs'));
person.appendChild(interest);

category=doc.createElement('category')
category.appendChild(doc.createTextNode('8'));
person.appendChild(category)

#First promotoer
promoter=doc.createElement('promoter');
person.appendChild(promoter);
firstname=doc.createElement('firstname')
firstname.appendChild(doc.createTextNode('David'))
lastname=doc.createElement('lastname')
lastname.appendChild(doc.createTextNode('Donaldson'))
promoter.appendChild(firstname);
promoter.appendChild(lastname);


client=doc.createElement('client');
promoter.appendChild(client);
fullname=doc.createElement('fullname')
fullname.appendChild(doc.createTextNode('Arnold Applebee'))
refid=doc.createElement('refid')
refid.appendChild(doc.createTextNode('10001'))
client.appendChild(fullname)
client.appendChild(refid)

#The other promoter
promoter=doc.createElement('promoter');
person.appendChild(promoter);
firstname=doc.createElement('firstname')
firstname.appendChild(doc.createTextNode('Edward'))
lastname=doc.createElement('lastname')
lastname.appendChild(doc.createTextNode('Eddleberry'))
promoter.appendChild(firstname);
promoter.appendChild(lastname);

client=doc.createElement('client');
promoter.appendChild(client);
fullname=doc.createElement('fullname')
fullname.appendChild(doc.createTextNode('Arnold Applebee'))
refid=doc.createElement('refid')
refid.appendChild(doc.createTextNode('10001'))
client.appendChild(fullname)
client.appendChild(refid)

#print:
print doc.toxml();#simple print

print doc.toprettyxml(indent="    ");#prettier print

#Write to file
f=open("people.xml", 'w')
doc.writexml(f);
f.close()


