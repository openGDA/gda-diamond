
from gda.device.scannable import ScannableMotionBase;

class PtClass(ScannableMotionBase):
	
	def __init__(self):
		self.name="Silly";
		self.setInputNames(['InputPos']);
#		self.extraNames = ['OutPos'];
		self.setExtraNames(['OutPos'])
#		self.outputFormat = ['%f','%f'];
		self.setOutputFormat(['%f','%f']);
		
	def testS(self):
#		exNames = self.getExtraNames();
		exNames = list(self.getExtraNames());
		
		oFormat = list(self.getOutputFormat());

		exNames.extend(['X', 'Y']);
		exNames.append( 'Z' );

		oFormat.extend(['%f', '%f']);
		oFormat.append( '%f' );

		print "Debug  --> before: " + str(self.getExtraNames())
		print "Debug  --> exNames: ",
		print exNames;
#		self.extraNames = exNames;
		self.setExtraNames(exNames);
		print "Debug --> after: " + str(self.getExtraNames())
		self.setOutputFormat(oFormat);

	def asynchronousMoveTo(self, exposureTime):
		pass;

	def getPosition(self):
		of=self.getOutputFormat();
		result=[];
		i=0;
		for o in of:
			result.append(i);
			i+=10;	
		return result;

##########################################


pt = PtClass();
#pt.testS();


from gda.device.scannable import ScannableMotionBase;

class PdClass(ScannableMotionBase):
	pass;

import java;

>>>a=pd.getExtraNames()


>>>len(a)
1
>>>java.lang.reflect.Array.getLength(a)
1

>>>a.append('X')
>>>java.lang.reflect.Array.getLength(a)
3
>>>b=java.lang.reflect.Array.get(a, 0)
>>>b=java.lang.reflect.Array.get(a, 1)
>>>java.lang.reflect.Array.get(a, 0)
OutPos
>>>java.lang.reflect.Array.get(a, 1)
X
>>>b=java.lang.reflect.Array.get(a, 2)
>>>print b
None
>>>b=java.lang.reflect.Array.get(a, 3)
Traceback (most recent call last):
  File "<input>", line 1, in <module>
	at java.lang.reflect.Array.get(Native Method)
	at sun.reflect.GeneratedMethodAccessor110.invoke(Unknown Source)
	at sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:25)
	at java.lang.reflect.Method.invoke(Method.java:597)

java.lang.ArrayIndexOutOfBoundsException: java.lang.ArrayIndexOutOfBoundsException

