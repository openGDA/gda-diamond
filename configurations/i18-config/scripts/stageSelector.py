
class StageSelector():

    def __init__(self,map):
        self.map = map

    def __call__(self, *args):
        if len(args) == 1:
            self.stageUsed = int(args[0])
        else:
            print "One argument should be provided (1 for stage 1 and 3 for stage 3."
            return
        self.map.setStage(self.stageUsed)

        print "Maps are now using stage ",self.stageUsed