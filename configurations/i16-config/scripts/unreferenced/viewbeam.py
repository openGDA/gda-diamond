#roidb = scroi=DetectorDataProcessorWithRoi('roidb', pil2m, [SumMaxPositionAndValue()])
#roidb.setRoi(1088,1577,1128,1624)
#roirb = scroi=DetectorDataProcessorWithRoi('roirb', pil2m, [SumMaxPositionAndValue()])
#roirb.setRoi(1088,1477,1128,1576)
def bsin():
	pos xps3m2 10.94 #bsv
	pos xps3m1 7.93   #bsh

def bsout():
	pos xps3m2 6.75 #bsv
	pos xps3m1 5   #bsh

def viewbeam():
	pos x1 0
	pos ss [.02 0.02]
	pos atten 255
	bsout()
	scan x 1 1 1 p2ms 0.1
#	bsin()
def zalign():
	scancn sz 0.1 31 p2ms 0.1 roidb
	foundedge=edge(0,'sz','roidb_sum')[1]
	print 'going to ' + str(foundedge)
	go foundedge
	scancn sz 0.01 31 p2ms 0.1 roidb
	foundedge=edge(0,'sz','roidb_sum')[1]
	print 'going to ' + str(foundedge)
	go foundedge

	