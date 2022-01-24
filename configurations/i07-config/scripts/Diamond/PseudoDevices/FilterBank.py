"""Class to control the Filter Set and individual filters via EPICS"""

from time import sleep
import random
import math


#from gda.device.scannable import ScannableMotionBase
from gda.device.scannable import ScannableBase

from gda.epics import CAClient;

#import threading;
#import synchronize;

import __main__ as gdamain

#class FilterSet(ScannableMotionBase):
class FilterSet(ScannableBase):
	"""Filter Set Class that implementing the GDA ScannableMotionBase interface"""

	
	def __init__(self, name, filters):
		"""
		
		name: the pseudo device name of filter set
		filters: a list of filters used as a filter set
		"""
		self.setName(name);
		self.setInputNames(['attenuation']);
		self.setExtraNames(["transmission", "thicknesses"]);
		self.setOutputFormat(["%5.5g", "%10.6g", "%s"]);
		
		self.filters = filters;
		self.activeFilters = [None for f in self.filters];

		self.lowAttenuation = 0;
		self.highAttenuation = 255;
		
		self.energyDevice = None;
		
	def setEnergyDevice(self, energyDevice):
		self.energyDevice = energyDevice;
		

	def setAttenuationRange(self, low=0, high=255):
		self.lowAttenuation = low;
		self.highAttenuation = high;
		
	def getActiveFilters(self):
		"""To get an ordered list of filters according to their attenuation scales."""
		for f in self.filters:
			order = f.getOrder();
			if order != None:
				self.activeFilters[order] = f;
		
		return self.activeFilters;

	#"""ScannableMotionBase Implementation"""
	def toString(self):
		p=self.getPosition();
		if p[1]>0.005: 
			ss='Attenuation: ' + str( p[0] ) + '; Thickness: ' + p[2] + '; Transmission: ' + str(p[1]) + '; Filter positions: ' + self.getPositionInBinary() + '.';
		else:
			ss='Attenuation: ' + str( p[0] ) + '; Thickness: ' + p[2] + '; Transmission: ' + str(p[1]) + '(3rd order transmission only); Filter positions: ' + self.getPositionInBinary() + '.';
		return ss;

	def getPosition(self):
		return [self.getAttenuation(), self.getTransmission(), self.getThicknesses()];

	def getPositionInBinary(self):
		positionList=[];
		for f in self.filters:
			positionList.append( f.getPosition() );

#		positionInBinaryString = ''.join(str(x) for x in positionList); #does not work, don't know why
#		positionInBinaryString = str(positionList[0:]).strip('[]').replace(', ', ''); #does not work, don't know why
		positionInBinaryString = str(positionList[0:]).strip('[]').replace(',', '').replace(' ', '');#works

		return 	positionInBinaryString;

	def asynchronousMoveTo(self,newAttenuation):
		if type(newAttenuation).__name__ == 'str':
			if newAttenuation.lower() == 'in': #Move all filters IN
				self.setFilterSet( len(self.filters) * '1');
				sleep(0.6);
			elif newAttenuation.lower() == 'out': #Move all filters OUT
				self.setFilterSet(len(self.filters) * '0');
				sleep(0.6);
			else:
				print "Please give a number for filter set attenuation or 'In/Out' for the whole set"
				return;
		else: #cast it into a integer
#TODO	I07 filter set is not a complete set. To avoid the missing filters by limiting the range
			if newAttenuation > self.highAttenuation: #Move all filters IN
				print "Attenuation higher than permitted. Nothing will change"
				#self.setFilterSet( len(self.filters) * '1');
			elif newAttenuation < self.lowAttenuation: #Move all filters OUT
				print "Attenuation lower than expected. All filters OUT"
				self.setFilterSet(len(self.filters) * '0');
			else:
				self.setAttenuation(int(newAttenuation));
			sleep(0.6);
			
		return;

	def isBusy(self):
		for f in self.filters:
			if f.isBusy():
				return True;
		return False;

	#"""Filter set functions"""
	def getAttenuation(self):
		"""Get the current filter set attenuation value"""
		positionList=[];

		self.getActiveFilters();
		for af in self.activeFilters:
			if af != None:
				positionList.append( af.getPosition() );
			else:
				positionList.append( 0 );

		positionInBinaryString = str(positionList[0:]).strip('[]').replace(',', '').replace(' ', '');
#		print 'Attenuation in Binary: ' + positionInBinaryString;
		
		attenuation = int(positionInBinaryString[::-1], 2);
		return attenuation;

	def setAttenuation(self,newAttenuation):
		"""Set filters based on the required attenuation value"""
		attStr=self.int2binStr(newAttenuation, len(self.filters));
#		print 'Attenuation in Binary: ' + attStr;
		attStr = attStr[::-1];

		self.getActiveFilters();
		
		#First to set the IN filters
#		print '<========== Filters IN:'
		for af in self.activeFilters:
			if attStr[self.activeFilters.index(af)] == '0':
				continue;
			else:
				if af != None:
					af.setFilterIn();
		sleep(1);
		#Then set the OUT filters
#		print '==========> Filters OUT:'
		for af in self.activeFilters:
			if attStr[self.activeFilters.index(af)] == '1':
				continue;
			else:
				if af != None:
#					print af.getName() + ': ' + str( int(attStr[self.activeFilters.index(af)]) );
					af.setFilterOut();
		
		return;

	def getTransmission(self, energy=None):
		if energy is None:
			energy=self.energyDevice.getPosition();#Energy in keV
			
#		f=self.getAttenuation(); # Attenuation;
#		t=100.0*math.exp(-231.72*f*math.pow(energy, -2.9253));
#		return t;
		thicknessMap=self.getThicknessesMap();
		thick_al=thicknessMap['Al']*1.0E-4;
		thick_mo=thicknessMap['Mo']*1.0E-4;
		thick_pb=thicknessMap['Pb']*1.0E-4;
		if thick_pb>0:#When the lead is down
			return 0;
		
		mu_al=50663*math.pow(energy, -2.882);

		if energy <=19.9995:
			mu_mo=451033*math.pow(energy, -2.71);
		else:
			mu_mo=2202141*math.pow(energy, -2.632);

		tra_al=math.exp(-1.0*thick_al*mu_al);
		tra_mo=math.exp(-1.0*thick_mo*mu_mo);
		t=100.0*tra_al*tra_mo;
		return t;

	def getThicknessesMap(self):
		"""Get the current filter set thickness information grouped in different materials used """
		thicknessMap={};
		
		self.getActiveFilters();
		for af in self.activeFilters:
			if af is None:
				continue;
			
			mo=af.getMaterial();
			thickness = thicknessMap.get(mo, 0);#Get the thickness of that material, or 0 if not exist yet
			
			if af.getPosition() == EpicsFilter.FILTER_POSITION_IN:
				thickness +=af.getThickness();
				
			thicknessMap[mo]=thickness
		return thicknessMap;
				
		s0='(';
		for material,thickness in thicknessMap.iteritems():
			s0 += material + ': ' + str(thickness) + ', ';
		ts=s0.rstrip(', ') + ')';
		
		return ts;

	def getThicknesses(self):
		thicknessMap=self.getThicknessesMap();
				
		s0='(';
		for material,thickness in thicknessMap.iteritems():
			s0 += material + ': ' + str(thickness) + ', ';
		ts=s0.rstrip(', ') + ')';
		
		return ts;

	def setFilterSet(self,newPositionInBinary):
		"""Set the filters in the Filter Set according to the input binary string, 0 for OUT, 1 for IN
		For example:
			setFilterSet('101')
		will set the first and third filter IN and all other filters OUT
		"""
		
		if not self.binaryCheck(newPositionInBinary):
			print 'Error: Please use a binary string as input!'
			return;

		positionInBinaryString = newPositionInBinary;
		print 'positionInBinaryString = ' + positionInBinaryString;
		
		if len(positionInBinaryString) > len(self.filters): #too long trunk it
			positionInBinaryString = positionInBinaryString[0:len(self.filters)];
		else: # too short, fill it with zeros
#			positionInBinaryString.ljust(len(self.filters),'0'); #does not work, don't know why
			positionInBinaryString = positionInBinaryString +  ( len(self.filters) - len(positionInBinaryString) ) * '0';


#		for i in range(len(positionInBinaryString)):
#			print 'filter ' +str(i+1) + ': ' + str( int(positionInBinaryString[i]) );
#			self.filters[i].asynchronousMoveTo(int(positionInBinaryString[i]));

		for i in range(len(positionInBinaryString)):
			if positionInBinaryString[i] == '1':
				print 'filter ' +str(i+1) + ': ' + str( int(positionInBinaryString[i]) );
#				self.filters[i].asynchronousMoveTo(int(positionInBinaryString[i]));
				self.filters[i].setFilterIn();
		for i in range(len(positionInBinaryString)):
			if positionInBinaryString[i] == '0':
				print 'filter ' +str(i+1) + ': ' + str( int(positionInBinaryString[i]) );
#				self.filters[i].asynchronousMoveTo(int(positionInBinaryString[i]));
				self.filters[i].setFilterOut();

		return;

	# convert a denary integer into a binary string (base 2)
	def denary2binary(self, n):
		"""convert denary integer n to binary string bStr"""
		bStr = ''

		if n < 0: raise ValueError #must be a positive integer
		if n == 0: return '0'
		while n > 0:
			bStr = str(n % 2) + bStr
			n = n >> 1

		return bStr

	def int2binStr(self, n, count=16):
		"""returns the binary string of an integer n, using count number of digits"""
		return "".join([str((n >> y) & 1) for y in range(count-1, -1, -1)])

	def binaryCheck(self, value):
		"""To check a give value is a binary string"""
		if type(value).__name__ != 'str':
			return False;
		for b in value:
			if b != '0' and b !='1':
				return False;
		return True;


#class EpicsFilter(ScannableMotionBase):
class EpicsFilter(ScannableBase):
	"""Filter Class that implementing the GDA ScannableMotionBase interface"""
	IN_LIMIT_STATUS_NOTIN, IN_LIMIT_STATUS_IN = range(2);
	IN_LIMIT_STRING = ['Not in', 'In'];
	
	OUT_LIMIT_STATUS_NOTOUT, OUT_LIMIT_STATUS_OUT = range(2);
	OUT_LIMIT_STRING  = ['Not out', 'Out'];
	
	FILTER_POSITION_OUT, FILTER_POSITION_IN, FILTER_POSITION_UNKNOWN = range(3);
	FILTER_POSITION_STRING = ['Out', 'In', 'Unknown'];

	FILTER_OUT, FILTER__IN = range(2);

	def __init__(self, name, rootPV):
		"""
		
		name: a pseudo device name for the filter
		rootPV: the EPICS base PV
		"""
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);
#		self.setLevel(7);
		self.filterRootPV = rootPV;
		self.material='Al';
		self.thickness=0;
		self.timeOutLimit = 30;
		self.inLimStatus = None;
		self.outLimStatus= None;
		self.filterPosition = None;
		
		self.scaleOrder = None;

		self.setup();
	
	def __del__(self):
		self.cleanChannel(self.chControl);
		self.cleanChannel(self.chInStatus);
		self.cleanChannel(self.chOutStatus);

	def setup(self):
		self.chControl=CAClient(self.filterRootPV+':CTRL'); self.configChannel(self.chControl);
		self.chInStatus=CAClient(self.filterRootPV+':INLIM'); self.configChannel(self.chInStatus);
		self.chOutStatus=CAClient(self.filterRootPV+':OUTLIM'); self.configChannel(self.chOutStatus);
		
		self.getFilterPosition();

	def configChannel(self, channel):
		if not channel.isConfigured():
			channel.configure();

	def cleanChannel(self, channel):
		if channel.isConfigured():
			channel.clearup();
	def setMaterial(self, m):
		self.material = m;
		
	def getMaterial(self):
		return self.material;

	def setThickness(self, t):
		self.thickness = t;
		
	def getThickness(self):
		return self.thickness;

	def setTimeOut(self, newTimeOut):
		self.timeOutLimit =  newTimeOut;

	def setOrder(self, newOrder):
		self.scaleOrder = newOrder;
		
	def getOrder(self):
		return self.scaleOrder;

	def setOrderValue(self, newOrderValue):
		if newOrderValue == None:
			self.scaleOrder = None;
			return;
#		self.scaleOrder = int(math.log(newOrderValue, 2)); #Does not work with Jython2.1
		self.scaleOrder = int(math.log(newOrderValue) / math.log(2) );

	def setFilter(self, newPosition):
#		self.chControl.caput(self.timeOutLimit, newPosition);
		self.chControl.caput(newPosition);

	def setFilterIn(self):
		if self.getFilterPosition() != EpicsFilter.FILTER_POSITION_IN:
			self.setFilter(EpicsFilter.FILTER__IN);

	def setFilterOut(self):
		if self.getFilterPosition() != EpicsFilter.FILTER_POSITION_OUT:
			self.setFilter(EpicsFilter.FILTER_OUT);

	def getFilterPosition(self):
#		if self.filterPosition == EpicsFilter.FILTER_POSITION_UNKNOWN: #just changed from GDA
#			sleep(0.3);
		self.inLimStatus = int( float(self.chInStatus.caget()) );
		self.outLimStatus = int( float(self.chOutStatus.caget()) );
#		print 'InLimStatus: ' + str(self.inLimStatus);
#		print 'OutLimStatus: ' + str(self.outLimStatus);
		
		if self.inLimStatus == EpicsFilter.IN_LIMIT_STATUS_IN and self.outLimStatus == EpicsFilter.OUT_LIMIT_STATUS_NOTOUT: #In status
			self.filterPosition = EpicsFilter.FILTER_POSITION_IN;
		elif self.inLimStatus == EpicsFilter.IN_LIMIT_STATUS_NOTIN and self.outLimStatus == EpicsFilter.OUT_LIMIT_STATUS_OUT: #Out status
			self.filterPosition = EpicsFilter.FILTER_POSITION_OUT;
		else: #Something wrong
			self.filterPosition = EpicsFilter.FILTER_POSITION_UNKNOWN;


#		self.positionString = EpicsFilter.FILTER_POSITION_STRING[self.filterPosition];
#		print 'Filter Position: ' + str(self.filterPosition);
		return self.filterPosition;

	"""ScannableMotionBase Implementation"""
	def toString(self):
		self.getPosition();
		ss=self.getName() + ': ' + EpicsFilter.FILTER_POSITION_STRING[self.filterPosition] ;
		return ss;

	def getPosition(self):
		return self.getFilterPosition();

	def asynchronousMoveTo(self,newPosition):
		if type(newPosition).__name__ == 'str':
			if newPosition.lower() == 'in':
				value = 1;
			elif newPosition.lower() == 'out':
				value = 0;
			else:
				value=None;
		elif type(newPosition).__name__ == 'int':
			if newPosition == 0 or newPosition == 1:
				value = newPosition;
			else:
				value = None;
		else:
			value = None;


		if self.getFilterPosition() != value:
			self.filterPosition = EpicsFilter.FILTER_POSITION_UNKNOWN;
			self.setFilter(value);
			sleep(0.6);
				
		return;

	def isBusy(self):
#		print 'Filter Position from isBusy:' + str(self.filterPosition);
		if self.getFilterPosition() == EpicsFilter.FILTER_POSITION_UNKNOWN:
			return True;
		else:
			return False;


#filterPVs=['BL07I-OP-FILT-01:FILTER1', 'BL07I-OP-FILT-01:FILTER2', 'BL07I-OP-FILT-01:FILTER3', 'BL07I-OP-FILT-01:FILTER4',
#		   'BL07I-OP-FILT-01:FILTER5', 'BL07I-OP-FILT-01:FILTER6', 'BL07I-OP-FILT-01:FILTER7', 'BL07I-OP-FILT-01:FILTER8',
#		   'BL07I-OP-FILT-01:FILTER9','BL07I-OP-FILT-01:FILTER10', 'BL07I-OP-FILT-01:FILTER11','BL07I-OP-FILT-01:FILTER12' ];

#filters = [];
#for i in range(len(filterPVs)):
#	filters.append( EpicsFilter('filter'+str(i+1), filterPVs[i]) );
	
#F1  = filters[0]; filters[0].setOrderValue(2);
#F2  = filters[1]; filters[1].setOrderValue(8);
#F3  = filters[2]; filters[2].setOrderValue(1);
#F4  = filters[3]; filters[3].setOrderValue(None);
#F5  = filters[4]; filters[4].setOrderValue(2048);
#F6  = filters[5]; filters[5].setOrderValue(None);
#F7  = filters[6]; filters[6].setOrderValue(4);
#F8  = filters[7]; filters[7].setOrderValue(None);
#F9  = filters[8]; filters[8].setOrderValue(128);
#F10 = filters[9]; filters[9].setOrderValue(16);
#F11 = filters[10]; filters[10].setOrderValue(64);
#F12 = filters[11]; filters[11].setOrderValue(32);

#filterSet = FilterSet('FilterSet', filters);
#filterSet.setAttenuationRange(0, 255);
