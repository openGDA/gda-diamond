wherescannables=[tth,th,chi,phi,h,k,l,energy]
wascannables = [tth, th,chi,phi,dsu,dsd,eta,ttp,thp,py,pz,alpha,difx,lgf,lgb,lgm,sx,sy,sz]

class PositionWrapper(object):
    def __init__(self, scannables):
        self.scannables = scannables
    def __call__(self):
        for scannable in self.scannables:
            print pos(scannable)
        
wh=PositionWrapper(wherescannables)
wa=PositionWrapper(wascannables)
alias('wh')
alias('wa')
