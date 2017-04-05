from gda.device.scannable import PseudoDevice
import diffcalc

class diffcalc_matrix_metadata(PseudoDevice):

    def __init__(self, name, prefix, matrix_cmd):
        self.name = name
        self.inputNames = []
        self.extraNames = ["%s_%d%d" % (prefix, j, i) for j in xrange(0, 3)
                for i in xrange(0, 3)]
        self.outputFormat = ["%5.5g"] * 9
        self.matrix_cmd = matrix_cmd

    def getPosition(self):
        try:
            m = eval(self.matrix_cmd, globals())
            return [m[j][i] for j in xrange(0, 3) for i in xrange(0, 3)]
        except(TypeError, diffcalc.utils.DiffcalcException):
            return [0] * 9

class diffcalc_xtal_metadata(PseudoDevice):

    def __init__(self, name, lattice_cmd):
        self.name = name
        self.inputNames = []
        self.extraNames = ["latt_a", "latt_b", "latt_c",
                "latt_alpha", "latt_beta", "latt_gamma"]
        self.outputFormat = ["%5.5g"] * 6
        self.lattice_cmd = lattice_cmd

    def getPosition(self):
        try:
            l = eval(self.lattice_cmd, globals())
            return [l["crystal"][p] for p in ["a", "b", "c", "alpha", "beta", "gamma"]]
        except(TypeError, diffcalc.utils.DiffcalcException):
            return [0] * 6
