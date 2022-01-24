import time

class tictoc:
        def __init__(self):
                self.start=time.time()

        def __repr__(self):
                return time.ctime()+' Elapsed time: '+str((time.time()-self.start))

        def reset(self):
                self.start=time.time()