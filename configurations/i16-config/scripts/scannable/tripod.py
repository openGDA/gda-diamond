from gda.device.scannable import ScannableMotionBase
from gda.device.scannable.scannablegroup import ScannableGroup,\
    ScannableMotionWithScannableFieldsBase
from gdascripts.scannable.dummy import SingleInputDummy
from scisoftpy.external import create_function
import scisoftpy.external
reload(scisoftpy.external)


GDA_EXTERNAL_PATH = "/dls_sw/i16/software/gda/workspace_git/gda-mt.git/configurations/i16-config/pythonscripts/gda_external"

print "Importing scannable.tripod. This calls the python code: '%s/tripod.p'y" % GDA_EXTERNAL_PATH

tool_to_base = create_function("tool_to_base",
                               module="tripod",
                               extra_path=[GDA_EXTERNAL_PATH],
                               dls_module="python/ana") # scipy")  # SEE SCI-1795
#def tool_to_base(x, y, z, alpha1, alpha2, alpha3):
""" Input tool position: x, y, z, alpha1, alpha2, alpha3 in (in mm and degrees).
    Calculate base settings: x1, x2, x3, y1, y2, y3 (all in mm)
"""


base_to_tool = create_function("base_to_tool",
                               module="tripod",
                               extra_path=[GDA_EXTERNAL_PATH],
                               dls_module="python/ana") # scipy")  # SEE SCI-1795
#def base_to_tool(x1, x2, x3, y1, y2, y3):
""" Input base settings : x1, x2, x3, y1, y2, y3 (all in mm)
    Calculate tool position: x, y, z, alpha1, alpha2, alpha3 (in mm and degrees)
"""





class TripodToolBase(ScannableMotionWithScannableFieldsBase):
    
    def __init__(self, name, tripod_base_scannable_group,
                 print_base_target=False, prepend_name_to_output_fields=True,
                 l=None, t=None, psi=None, c=None, theta=None, BX=None, BY=None):
        self.name = name
        preface = self.name + '_' if prepend_name_to_output_fields else ''
        self.inputNames = [preface + s for s in ['x', 'y', 'z', 'alpha1', 'alpha2', 'alpha3']]
        self.extraNames = []  # 'X1', 'X2', 'X3', 'Y1', 'Y2', 'Y3']
        self.outputFormat = ['% 10.5f'] * 6
        self.tripod_base_scannable_group = tripod_base_scannable_group
        self.print_base_target = print_base_target
        self.prepend_name_to_output_fields = prepend_name_to_output_fields
        self.geom = {'l':l, 't':t, 'psi':psi, 'c':c, 'theta':theta, 'BX':BX, 'BY':BY}
        
        self.autoCompletePartialMoveToTargets=True  # inherited property
        self.usePositionAtScanStartWhenCompletingPartialMoves=True  # inherited property
    
    def rawAsynchronousMoveTo(self, tool_position):
        base_position = list(tool_to_base(*tool_position, **self.geom))
        if self.print_base_target:
            lines = []
            lines.append(self.tripod_base_scannable_group.name + "-->")
            for name, fmt, position in zip(self.tripod_base_scannable_group.inputNames,
                                           self.tripod_base_scannable_group.outputFormat,base_position):
                lines.append(" " + name.ljust(6) + ": " + str(fmt%position))
            print '\n'.join(lines)
        self.tripod_base_scannable_group.asynchronousMoveTo(base_position)
        
    def rawGetPosition(self):
        base_position = list(self.tripod_base_scannable_group.getPosition())
        tool_position = list(base_to_tool(*base_position, **self.geom))
        return tool_position  # + base_position
        
    def waitWhileBusy(self):
        self.tripod_base_scannable_group.waitWhileBusy()
        
    def isBusy(self):
        return self.tripod_base_scannable_group.isBusy()
        
    def __str__(self):
        lines = []
        lines.append(self.name + "::")
        for name, fmt, position in zip(self.inputNames, self.outputFormat, self.getPosition()):
            lines.append(" " + name.ljust(6) + ": " + str(fmt%position))
        return '\n'.join(lines)


kbmbase_dummyX1 = SingleInputDummy('kbmbase_dummyX1')
kbmbase_dummyX2 = SingleInputDummy('kbmbase_dummyX2')
kbmbase_dummyX3 = SingleInputDummy('kbmbase_dummyX3')
kbmbase_dummyY1 = SingleInputDummy('kbmbase_dummyY1')
kbmbase_dummyY2 = SingleInputDummy('kbmbase_dummyY2')
kbmbase_dummyY3 = SingleInputDummy('kbmbase_dummyY3')

kbmbase_dummy = ScannableGroup("kbmbase_dummy", [kbmbase_dummyX1, kbmbase_dummyX2, kbmbase_dummyX3,kbmbase_dummyY1, kbmbase_dummyY2, kbmbase_dummyY3])
#kbmtool_dummy = TripodToolBase("kbmtool_dummy", kbmbase_dummy, print_base_target=True)