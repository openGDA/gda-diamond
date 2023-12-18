from gda.device.scannable import ScannableBase
from gda.epics import CAClient
from math import sqrt

class EPICSODQBPMClass(ScannableBase):
	'''PD for OD QBPM device
	Inputs: None
	Outputs: Range, C1, C2, C3, C4, X, Y
	self.set_range(value) - set gain 0 = highest
	calibration sequence:
	self.dark_current()	save dark current at current gain (beam off)
	self.set_zero()	calibrate zero x,y (beam on)
	self.setxy(xval, yval)	calibrate gains to give position in mm (go to xval, yval; beam on) - NOT TESTED
	Additional methods: config() loads qbpm parameters'''

	#	a=A1*(current4-A2) etc
	#	X=GX*(a-b)/(a+b) etc
	#	a,b,c,d=chan 4,2,1,3

	def __init__(self, name, pvrootstring,help=None):
		self.setName(name);
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
		#[self.A1,self.A2,self.B1,self.B2,self.C1,self.C2,self.D1,self.D2,self.GX,	self.GY]=xyparamvec
		self.pvrootstring=pvrootstring
		self.setInputNames([])
		self.setExtraNames(['Range','C1','C2','C3','C4','X','Y']);
		#self.setReportingUnits([' ','uA','uA','uA','uA','mm','mm'])
		self.setOutputFormat(['%.0f','%.9f','%.9f','%.9f','%.9f','%.3f','%.3f'])
		self.setLevel(9)
		self.rangecli=CAClient(pvrootstring+':RANGE_MENU');self.rangecli.configure()
		self.c1cli=CAClient(pvrootstring+':PHD1:I');self.c1cli.configure()
		self.c2cli=CAClient(pvrootstring+':PHD2:I');self.c2cli.configure()
		self.c3cli=CAClient(pvrootstring+':PHD3:I');self.c3cli.configure()
		self.c4cli=CAClient(pvrootstring+':PHD4:I');self.c4cli.configure()
		self.xcli=CAClient(pvrootstring+':XPOS');self.xcli.configure()
		self.ycli=CAClient(pvrootstring+':YPOS');self.ycli.configure()
		self.IR1cli=CAClient(pvrootstring+':PHD1:I_R');self.IR1cli.configure()
		self.IR2cli=CAClient(pvrootstring+':PHD2:I_R');self.IR2cli.configure()
		self.IR3cli=CAClient(pvrootstring+':PHD3:I_R');self.IR3cli.configure()
		self.IR4cli=CAClient(pvrootstring+':PHD4:I_R');self.IR4cli.configure()


	def getPosition(self):
		self.rangestring=self.rangecli.caget()
		self.c1string=self.c1cli.caget()
		self.c2string=self.c2cli.caget()
		self.c3string=self.c3cli.caget()
		self.c4string=self.c4cli.caget()
		self.xstring=self.xcli.caget()
		self.ystring=self.ycli.caget()
		return [float(self.rangestring),float(self.c1string), float(self.c2string),float(self.c3string),float(self.c4string),float(self.xstring),float(self.ystring)]

#	def asynchronousMoveTo(self,new_position):
#		self.rangecli.caput(new_position)

	def isBusy(self):
		return 0

	def set_params(self,params):
		[A1,A2,B1,B2,C1,C2,D1,D2,GX,GY]=params
		self.configcli=CAClient(self.pvrootstring+':A1_SP');self.configcli.configure(); self.configcli.caput(A1); self.configcli.clearup();
		self.configcli=CAClient(self.pvrootstring+':A2_SP');self.configcli.configure(); self.configcli.caput(A2); self.configcli.clearup();
		self.configcli=CAClient(self.pvrootstring+':B1_SP');self.configcli.configure(); self.configcli.caput(B1); self.configcli.clearup();
		self.configcli=CAClient(self.pvrootstring+':B2_SP');self.configcli.configure(); self.configcli.caput(B2); self.configcli.clearup();
		self.configcli=CAClient(self.pvrootstring+':C1_SP');self.configcli.configure(); self.configcli.caput(C1); self.configcli.clearup();
		self.configcli=CAClient(self.pvrootstring+':C2_SP');self.configcli.configure(); self.configcli.caput(C2); self.configcli.clearup();
		self.configcli=CAClient(self.pvrootstring+':D1_SP');self.configcli.configure(); self.configcli.caput(D1); self.configcli.clearup();
		self.configcli=CAClient(self.pvrootstring+':D2_SP');self.configcli.configure(); self.configcli.caput(D2); self.configcli.clearup();
		self.configcli=CAClient(self.pvrootstring+':GX_SP');self.configcli.configure(); self.configcli.caput(GX); self.configcli.clearup();
		self.configcli=CAClient(self.pvrootstring+':GY_SP');self.configcli.configure(); self.configcli.caput(GY); self.configcli.clearup();

	def get_params(self):
		self.configcli=CAClient(self.pvrootstring+':A1_SP');self.configcli.configure(); A1=float(self.configcli.caget());self.configcli.clearup()
		self.configcli=CAClient(self.pvrootstring+':A2_SP');self.configcli.configure(); A2=float(self.configcli.caget()); self.configcli.clearup()
		self.configcli=CAClient(self.pvrootstring+':B1_SP');self.configcli.configure(); B1=float(self.configcli.caget()); self.configcli.clearup()
		self.configcli=CAClient(self.pvrootstring+':B2_SP');self.configcli.configure(); B2=float(self.configcli.caget()); self.configcli.clearup()
		self.configcli=CAClient(self.pvrootstring+':C1_SP');self.configcli.configure(); C1=float(self.configcli.caget()); self.configcli.clearup()
		self.configcli=CAClient(self.pvrootstring+':C2_SP');self.configcli.configure(); C2=float(self.configcli.caget()); self.configcli.clearup()
		self.configcli=CAClient(self.pvrootstring+':D1_SP');self.configcli.configure(); D1=float(self.configcli.caget()); self.configcli.clearup()
		self.configcli=CAClient(self.pvrootstring+':D2_SP');self.configcli.configure(); D2=float(self.configcli.caget()); self.configcli.clearup()
		self.configcli=CAClient(self.pvrootstring+':GX_SP');self.configcli.configure(); GX=float(self.configcli.caget()); self.configcli.clearup()
		self.configcli=CAClient(self.pvrootstring+':GY_SP');self.configcli.configure(); GY=float(self.configcli.caget()); self.configcli.clearup()
		return [A1,A2,B1,B2,C1,C2,D1,D2,GX,GY]

	def get_rawcounts(self):
		self.IR1=float(self.IR1cli.caget())
		self.IR2=float(self.IR2cli.caget())
		self.IR3=float(self.IR3cli.caget())
		self.IR4=float(self.IR4cli.caget())
		return [self.IR1, self.IR2, self.IR3, self.IR4]

	def set_range(self, newrange):
		self.rangecli.caput(newrange)

	def factory_reset(self):
		params=[A1,A2,B1,B2,C1,C2,D1,D2,GX,GY]=[1,0,1,0,1,0,1,0,1,1]
		self.set_params(params)
		
	def dark_current(self):
		#offsets not persistent - do dark current with beam off
		[A1,A2,B1,B2,C1,C2,D1,D2,GX,GY]=self.get_params()

		self.configcli=CAClient(self.pvrootstring+':PHD4:I_R');self.configcli.configure(); A2=float(self.configcli.caget()); self.configcli.clearup()
		self.configcli=CAClient(self.pvrootstring+':PHD2:I_R');self.configcli.configure(); B2=float(self.configcli.caget()); self.configcli.clearup()
		self.configcli=CAClient(self.pvrootstring+':PHD1:I_R');self.configcli.configure(); C2=float(self.configcli.caget()); self.configcli.clearup()
		self.configcli=CAClient(self.pvrootstring+':PHD3:I_R');self.configcli.configure(); D2=float(self.configcli.caget()); self.configcli.clearup()
		self.set_params([A1,A2,B1,B2,C1,C2,D1,D2,GX,GY])
		print 'new dark currents (i4,i2,i1,i3):', [A2, B2, C2, D2]

	def set_zero(self):
		#do with beam on
		[ic,ib,id,ia]=self.get_rawcounts()
		[A1,A2,B1,B2,C1,C2,D1,D2,GX,GY]=self.get_params()
		A1B1=A1*B1; C1D1=C1*D1;	#get products
		A1_B1=(ib-B2)/(ia-A2);		#calculate ratio X=0
		C1_D1=(id-D2)/(ic-C2);		#calculate ratio Y=0
		#re-calc A1, B1 etc for zero X,Y but keep ratio at current value
		[A1, B1, C1, D1]=[sqrt(A1B1*A1_B1), sqrt(A1B1/A1_B1), sqrt(C1D1*C1_D1), sqrt(C1D1/C1_D1)]
		self.set_params([A1,A2,B1,B2,C1,C2,D1,D2,GX,GY])

	def set_xy(self,x,y):
		#do with beam on
		[ic,ib,id,ia]=self.get_rawcounts()
		[A1,A2,B1,B2,C1,C2,D1,D2,GX,GY]=self.get_params()
		[a,b,c,d]=[A1*(ia-A2), B1*(ib-B2),C1*(ic-C2), D1*(id-D2)]
		[GX, GY]=[x*(a+b)/(a-b),y*(c+d)/(c-d)]
		#print [A1,A2,B1,B2,C1,C2,D1,D2,GX,GY]
		self.set_params([A1,A2,B1,B2,C1,C2,D1,D2,GX,GY])

qbpm1=EPICSODQBPMClass('QBPM1','BL11I-DI-QBPM-01',help='Current amp for QBPM1 in optic hutch')
qbpm3=EPICSODQBPMClass('QBPM3','BL11I-DI-QBPM-03',help='Current amp for QBPM3 in experimental hutch')
qbpm2=EPICSODQBPMClass('QBPM2','BL11I-DI-QBPM-02',help='Current amp for QBPM2 in optic hutch')


class ReadSingleValueFromVectorPDClass(ScannableBase):
	'''
	PD with single output and no imput
	Reads value from specified index of an existing PD
	'''
	def __init__(self,pd,index,name,format,help=None):
		self.setName(name);
		if help is not None: self.__doc__+='\nHelp specific to '+self.name+':\n'+help
		self.setInputNames([])
		self.setExtraNames([name]);
		self.setOutputFormat([format])
		self.setLevel(9)
		self.index=index
		self.pd=pd

	def getPosition(self):
		return self.pd()[self.index]
	
	def isBusy(self):
		return self.pd.isBusy()

vpos=ReadSingleValueFromVectorPDClass(qbpm1,6,'vpos','%.4f',help='qbpm vertical position (Y)')
hpos=ReadSingleValueFromVectorPDClass(qbpm1,5,'hpos','%.4f',help='qbpm horizontal position (X)')
