

from Diamond.PseudoDevices.FilterBank import EpicsFilter, FilterSet;
from gda.device.scannable import DummyScannable

if LocalProperties.get("gda.mode") == "live":
	
	filter1PVs=['BL07I-OP-FILT-01:FILTER1', 'BL07I-OP-FILT-01:FILTER2', 'BL07I-OP-FILT-01:FILTER3', 'BL07I-OP-FILT-01:FILTER4',
			   'BL07I-OP-FILT-01:FILTER5', 'BL07I-OP-FILT-01:FILTER6', 'BL07I-OP-FILT-01:FILTER7', 'BL07I-OP-FILT-01:FILTER8',
			   'BL07I-OP-FILT-01:FILTER9','BL07I-OP-FILT-01:FILTER10', 'BL07I-OP-FILT-01:FILTER11','BL07I-OP-FILT-01:FILTER12' ];
	##			  Order: [Thickness, Element ]
	FilterInfo = {0:  [1,      61, 'Aluminum'  ],
				  1:  [2,      95, 'Aluminum'  ],
				  2:  [4,     160, 'Aluminum'  ],
				  3:  [8,     349, 'Aluminum'  ],
				  4:  [16,    648, 'Aluminum'  ],
				  5:  [32,   1318, 'Aluminum'  ],
				  6:  [64,   2560, 'Aluminum'  ],
				  7:  [128,  5121, 'Aluminum'  ],
				  8:  [256,   100, 'Molybdenum'],
				  9:  [512,   200, 'Molybdenum'],
				  10: [1024,  400, 'Molybdenum'],
				  11: [2048, 1000, 'Lead'      ]  }

	filters = [];
	for i in range(len(filter1PVs)):
		filters.append( EpicsFilter('filter'+str(i+1), filter1PVs[i]) );

	f1  = filters[0]; filters[0].setOrderValue(2);   filters[0].setThickness(95)  ; filters[0].setMaterial('Al');
	f2  = filters[1]; filters[1].setOrderValue(8);   filters[1].setThickness(346) ; filters[1].setMaterial('Al');
	f3  = filters[2]; filters[2].setOrderValue(1);   filters[2].setThickness(61)  ; filters[2].setMaterial('Al');
	f4  = filters[3]; filters[3].setOrderValue(1024);filters[3].setThickness(400) ; filters[3].setMaterial('Mo');
	f5  = filters[4]; filters[4].setOrderValue(2048);filters[4].setThickness(1000); filters[4].setMaterial('Pb');
	f6  = filters[5]; filters[5].setOrderValue(256); filters[5].setThickness(100) ; filters[5].setMaterial('Mo');
	f7  = filters[6]; filters[6].setOrderValue(4);   filters[6].setThickness(160) ; filters[6].setMaterial('Al');
	f8  = filters[7]; filters[7].setOrderValue(512); filters[7].setThickness(200) ; filters[7].setMaterial('Mo');
	f9  = filters[8]; filters[8].setOrderValue(128); filters[8].setThickness(5121); filters[8].setMaterial('Al');
	f10 = filters[9]; filters[9].setOrderValue(16);  filters[9].setThickness(648) ; filters[9].setMaterial('Al');
	f11 = filters[10]; filters[10].setOrderValue(64);filters[10].setThickness(2560); filters[10].setMaterial('Al');
	f12 = filters[11]; filters[11].setOrderValue(32);filters[11].setThickness(1318); filters[11].setMaterial('Al');

	filterset = FilterSet('filterset', filters);
	filterset.setEnergyDevice(dcm1energy);
	#filterset.setAttenuationRange(0, 255);
	filterset.setAttenuationRange(0, 4095);

	atten = filter;

else:
	filterset = DummyScannable('filterset')

#print "-------------------------------------------------------------------"
print "Note: Use f1, f2, ... to f12 for individual filter"
print "Note: Use filterset for the whole filter set"
print "For example: 'pos filterset' to get the current filter position and attenuation"
print "             'pos filterset 31' to change the attenuation to 31"
