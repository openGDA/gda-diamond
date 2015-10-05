package uk.ac.gda.nano.views;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

public class RScanParameterPaser {
	Document doc;
	Element rootElement;

	public RScanParameterPaser(){
	}

	public RScanParameterPaser(File xmlFile){
		parseXmlFile(xmlFile);
	}
	

	public void parseXmlFile(File xmlFile){
		
		//parse the xml file and get the dom object

		//get the factory
		DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
		try {
			//Using factory get an instance of document builder
			DocumentBuilder db = dbf.newDocumentBuilder();
			//parse using builder to get DOM representation of the XML file
			doc = db.parse(xmlFile);
		}catch(ParserConfigurationException pce) {
			pce.printStackTrace();
		}catch(SAXException se) {
			se.printStackTrace();
		}catch(IOException ioe) {
			ioe.printStackTrace();
		}

		//get the root elememt
		rootElement = doc.getDocumentElement();
	}


	public void runExample() {
		
		String[] dl=getDevices("Motors");
		System.out.println("------------Motors: -----------------");
		for(int i=0; i<dl.length; i++){
			System.out.println(dl[i]);
		}

		dl=getDevices("Detectors");
		System.out.println("------------Detectors: -----------------");
		for(int i=0; i<dl.length; i++){
			System.out.println(dl[i]);
		}
		
		dl=getDevices("Monitors");
		System.out.println("------------Monitors: -----------------");
		for(int i=0; i<dl.length; i++){
			System.out.println(dl[i]);
		}
		
	}
	
	public String[] getDevices(String deviceListName){
		List<String> deviceList = new ArrayList<String>();
		
		//get a nodelist of <DetectorGroup> elements
		NodeList dgnl = rootElement.getElementsByTagName(deviceListName);
		
		for(int i = 0; i < dgnl.getLength(); i++) {
			Node dgn= dgnl.item(i);
			
			//get the individual detector group element
			NodeList dnl = dgn.getChildNodes();
			for(int j = 0; j < dnl.getLength(); j++) {
				Node dn=dnl.item(j);
				if(dn instanceof Element){
					Element de=(Element)dn;
					String name = de.getAttribute("name");
					deviceList.add(name);
					}
				}
		}
		
		String[] dla=deviceList.toArray(new String[deviceList.size()]);
		return dla;
	}


	

	private String getTextValue(Element ele, String tagName) {
		String textVal = null;
		NodeList nl = ele.getElementsByTagName(tagName);
		if(nl != null && nl.getLength() > 0) {
			Element el = (Element)nl.item(0);
			textVal = el.getFirstChild().getNodeValue();
			el.getAttribute("name");
		}

		return textVal;
	}

	
	private int getIntValue(Element ele, String tagName) {
		//in production application you would catch the exception
		return Integer.parseInt(getTextValue(ele,tagName));
	}

	
	public static void main(String[] args){
		//create an instance
		File xmlFile = new File("/dls_sw/i06-1/software/gda/config/templates/RegionalisedScanParameters.xml");
//		File xmlFile = new File("/scratch/dev/JavaDev/xml/scan.xml");
		
		RScanParameterPaser dps = new RScanParameterPaser(xmlFile);
		
		//call run example
		dps.runExample();
	}

}
