'''
Created on 15 Feb 2011

@author: fy65
'''

from threading import Thread
def sum_datasets(datasets):
    #{0: [1,2,3], 1: [3,4,5], 2: [6,7,8]}
    lists = [x.tolist() for x in datasets.values()]
    if len(lists) == 1:
        return lists[0]
    data = zip(*tuple(lists))
    #[(1,3,6), (2,4,7)...]
    data = [float(sum(xs)) / len(xs) for xs in data]
    #[3.333, ...]
    return data


class SaveData(Thread):
    def __init__(self,group=None, target=None, name=None, args=(), kwargs={}):
        Thread.__init__(self, group, target, name, args, kwargs)
        self.file=None
        self.data=[]
         
    def run(self):
        self.save(self._args, self._kwargs)
        
    def save(self, args=(), kwargs={}):
            self.data = sum_datasets(kwargs)
            print "%s: saving data to %s" % (args[2], args[0])
            self.file=open(args[0], args[1])
            for each in self.data:
                self.file.write("%s\n"%each)
            self.file.close()
            print "%s: save data to %s completed." % (args[2], args[0])

