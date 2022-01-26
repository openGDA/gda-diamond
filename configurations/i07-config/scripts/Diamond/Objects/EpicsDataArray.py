from time import sleep
from java import lang
#from gda.device.scannable import ScannableBase
#from gda.device import Scannable
from gda.epics import CAClient

import scisoftpy as dnp

from gda.factory import Finder

'''
	<scanData desc="Fast Energy Scan Data" name="FASTSCAN.DATA">
		<COUNTER desc="no of elements read so far" pv="BL06I-MO-FSCAN-01:ELEMENTCOUNTER" ro="true" type="pv"/>
		<CH1DATA desc="CH1DATA" pv="BL06I-MO-FSCAN-01:CH1SUBARRAY" ro="true" type="array"/>
		<CH2DATA desc="CH2DATA" pv="BL06I-MO-FSCAN-01:CH2SUBARRAY" ro="true" type="array"/>
		<CH3DATA desc="CH3DATA" pv="BL06I-MO-FSCAN-01:CH3SUBARRAY" ro="true" type="array"/>
		<CH4DATA desc="CH4DATA" pv="BL06I-MO-FSCAN-01:CH4SUBARRAY" ro="true" type="array"/>
		<CH5DATA desc="CH5DATA" pv="BL06I-MO-FSCAN-01:CH5SUBARRAY" ro="true" type="array"/>
		<CH6DATA desc="CH6DATA" pv="BL06I-MO-FSCAN-01:CH6SUBARRAY" ro="true" type="array"/>
		<NODETECTORS desc="NODETECTORS" pv="BL06I-MO-FSCAN-01:NODETECTORS" ro="true" type="pv"/>
		<STARTINDEX desc="readout start index" pv="BL06I-MO-FSCAN-01:STARTINDEX" ro="false" type="pv"/>
		<NOELEMENTS desc="no of elements to readout" pv="BL06I-MO-FSCAN-01:NOELEMENTS" ro="false" type="pv"/>
		<UPDATE desc="UPDATE" pv="BL06I-MO-FSCAN-01:UPDATE" ro="false" type="pv"/>
	</scanData>
'''

#The Class for creating a EpicsArrayData object

#pvWaveFormHead Total number of element
#pvSubArrayIndex Starting index of the new subArray
#pvSubArraySize size of the new subArray
#pvUpdate Update request for filling the new subArray

# # PV definitions
# ################
# pvWaveFormHead='BL06I-MO-FSCAN-01:ELEMENTCOUNTER'
# pvSubArrayIndex='BL06I-MO-FSCAN-01:STARTINDEX'
# pvSubArraySize='BL06I-MO-FSCAN-01:NOELEMENTS'
# pvUpdate='BL06I-MO-FSCAN-01:UPDATE'
# 
# #Subarray Channels
# pvCh01='BL06I-MO-FSCAN-01:CH1SUBARRAY'
# pvCh02='BL06I-MO-FSCAN-01:CH2SUBARRAY'
# pvCh03='BL06I-MO-FSCAN-01:CH3SUBARRAY'
# pvCh04='BL06I-MO-FSCAN-01:CH4SUBARRAY'
# pvCh05='BL06I-MO-FSCAN-01:CH5SUBARRAY'
# pvCh06='BL06I-MO-FSCAN-01:CH6SUBARRAY'

maxLength = 20;
maxBlockSize = 1024;
#Steps:
#1. Set start index and number of elements to read
#2. Trigger the update
#3. Update the arrays with the new data by click update button

class EpicsDataArrayClass:
	def __init__(self):
		
		self.ccWaveFormHead=CAClient(pvWaveFormHead);
		self.ccSubArraySize=CAClient(pvSubArraySize);
		self.ccSubArrayIndex=CAClient(pvSubArrayIndex);
		self.ccUpdate=CAClient(pvUpdate);

		self.ccCh01=CAClient(pvCh01);
		self.ccCh02=CAClient(pvCh02);
		self.ccCh03=CAClient(pvCh03);
		self.ccCh04=CAClient(pvCh04);
		self.ccCh05=CAClient(pvCh05);
		self.ccCh06=CAClient(pvCh06);

		self.ccWaveFormHead.configure();
		self.ccSubArraySize.configure();
		self.ccSubArrayIndex.configure();
		self.ccUpdate.configure();

		self.ccCh01.configure();
		self.ccCh02.configure();
		self.ccCh03.configure();
		self.ccCh04.configure();
		self.ccCh05.configure();
		self.ccCh06.configure();

		self.length = 0;
		self.head=0;

		self.dataSetCh01=dnp.zeros([maxLength]); 
		self.dataSetCh01.setName("Channel 1");
		self.js = Finder.find("command_server");


	def setBlockSize(self, size):
		self.ccSubArraySize.caput(size);

	def setBlockIndex(self, index):
		self.ccSubArrayIndex.caput(index);

	#To get the number of valid data from the waveform
	def getDataNumbers(self):
		strLength = self.ccWaveFormHead.caget()
		return int(float(strLength));
		
	def getLength(self):
		return self.getDataNumbers();

	def hasNewData(self):
		self.length = self.getLength();
		if self.head < self.length:
			self.length = min(self.length, self.head + maxBlockSize);
			return True;
		else:
			return False;

	def display(self):
		self.js.notifyServer(0, self.dataSetCh01);
		return;


	def getNewData(self):
		if not self.hasNewData():
			print "No new Data.";
			return;
		
		self.setBlockIndex(self.head);
		self.setBlockSize(self.length-self.head)
		
		print "Head", self.head;
		print "Length", self.length;

		self.update();
		sleep(1);
		arrayCh01=[];
		arrayCh01=self.ccCh01.cagetArrayDouble(self.length-self.head);
		print "New Array";
		print arrayCh01;
		
		for i in range(self.head, self.length):
			self.dataSetCh01[i] = arrayCh01[i-self.head]
		
		self.head = self.length;
		
		print "New data: "
		self.dataSetCh01.disp();
		
		return;
	
		
	#trigger the fast scan
	def update(self):
		self.ccUpdate.caput(1);
		


ed=EpicsDataArrayClass();

ed.getNewData();


