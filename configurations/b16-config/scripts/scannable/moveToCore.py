from gda.epics import CAClient

class DynamicPvManager(object):
    
    def __init__(self, pvroot):
        self.pvroot = pvroot
        self.clients = {}

    def __getitem__(self, pvname):
        try:
            return self.clients[pvname]
        except KeyError:
            self.add(pvname)
            return self.clients[pvname]
            
    def add(self, pvname):
        self.clients[pvname] = CAClient(self.pvroot + pvname)
        self.clients[pvname].configure()
