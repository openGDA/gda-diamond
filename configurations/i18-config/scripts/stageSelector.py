
class StageSelector():

    def __init__(self,samplePreparer,map):
        self.samplePreparer = samplePreparer
        self.map = map

    def __call__(self, *args):
        if len(args) == 1:
            self.stageUsed = int(args[0])
        else:
            print "One argument should be provided (1 for stage 1 and 3 for stage 3."
            return
        self.map.setStage(self.stageUsed)
        self.samplePreparer.setStage(self.stageUsed)

        print "Map and energy scans (Xas, Xanes and Qexafs) are using stage ",self.stageUsed