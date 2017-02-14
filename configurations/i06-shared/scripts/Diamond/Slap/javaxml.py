
#All the imports for using the JAXP APIs

import javax.xml.parsers.DocumentBuilder; 
import javax.xml.parsers.DocumentBuilderFactory; 
import javax.xml.parsers.FactoryConfigurationError; 
import javax.xml.parsers.ParserConfigurationException; 

#for the exceptions that can be thrown when the XML document is parsed:
import org.xml.sax.SAXException; 
import org.xml.sax.SAXParseException; 

#to read the sample XML file and identify errors:
import java.io.File;
import java.io.IOException; 

#the W3C definition for a DOM and DOM exceptions:
import org.w3c.dom.Document;
import org.w3c.dom.DOMException; 


DocumentBuilderFactory factory=DocumentBuilderFactory.newInstance();


javadoc=Document

