
from java.lang import StringBuilder
from java.io import BufferedReader, InputStreamReader;
from java.net import URL;

from java.io import File;
from org.w3c.dom import Document;

from javax.xml.parsers import DocumentBuilderFactory;
from javax.xml.parsers import DocumentBuilder;
from javax.xml.transform.dom import DOMSource

from javax.xml.transform import Transformer, TransformerFactory
from javax.xml.transform.stream import StreamResult

responseBuilder = StringBuilder();
ru='http://172.23.106.80:8080/SlapWebServices/ReadOnlyService'

url = URL( ru );

'''
conn = url.openConnection();
rd = BufferedReader( InputStreamReader(conn.getInputStream()) );
line = rd.readLine();
while line != None:
	responseBuilder.append(line + '\n');
	line = rd.readLine();
rd.close();
txt=responseBuilder.toString();
'''

dbf = DocumentBuilderFactory.newInstance();
db = dbf.newDocumentBuilder();

doc = db.parse( url.openStream() );

value = doc.getElementsByTagName('Terminal').item(1).item(1).getFirstChild().getNodeValue()
lg=float(value);
print lg


source = DOMSource(doc)
file = File("/tmp/aaa.xml");
result = StreamResult(file);
xformer = TransformerFactory.newInstance().newTransformer();

xformer.transform(source, result);
        
        
'''
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<Response>
	<Terminal>
		<Name>FundamentalEnableFeedback</Name>
		<Value>1</Value>
	</Terminal>
	<Terminal><Name>LoopGainFeedback</Name><Value>79</Value>
	</Terminal><Terminal><Name>HarmPhaseShiftFeedback</Name><Value>39754</Value></Terminal>
	<Terminal><Name>FundPhaseShiftFeedback</Name><Value>42977</Value></Terminal>
	<Terminal><Name>DelaySetValueFeedback</Name><Value>0.000000</Value></Terminal>
</Response>

'''        
        