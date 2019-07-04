from gda.scan import ScanPositionProvider

class XMCDScanPositionProvider(ScanPositionProvider):
    def __init__(self, name, numberOfImages, pols, energies):
        self.name = name
        self.pols = tuple(pols)
        self.energies = tuple(energies)
        self.numberOfImages = numberOfImages
        self.start = 0
        self.stop = 0
        self.step = 0
        self.values=[]

    # Python functions

    def __repr__(self):
        return "XMCDScanPositionProvider(name='%s', numberOfImages=%i, pols=%r, energies=%r)" % (self.name, self.numberOfImages, self.pols, self.energies)

    def __str__(self):
        return "%s: count=%r" % (self.__repr__(), self.size())

    # public interface ScanPositionProvider

    def get(self, index):
        return self.values[index]

    def size(self):
        self.values=[]
        for pol in self.pols:
            for energy in self.energies:
                for image in range(self.numberOfImages):
                    self.values.append([image, pol, energy])
        return len(self.values)

