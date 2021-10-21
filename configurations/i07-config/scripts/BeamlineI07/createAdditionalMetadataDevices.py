
from gda.jython.commands.ScannableCommands import add_default;

from Diamond.PseudoDevices.MetadataHeaderDevice import MetadataHeaderDeviceClass

pilatusHeader = MetadataHeaderDeviceClass("pilatusHeader");


from gdascripts.scannable.dummy import SingleInputStringDummy
note = SingleInputStringDummy('note')


from gdascripts.pd.dummy_pds import MultiInputExtraFieldsDummyPD

centralPixel = MultiInputExtraFieldsDummyPD('centralPixel', ['centralPixel_x','centralPixel_y'], [])
centralPixel.setOutputFormat(['%.0f', '%.0f'])
centralPixel.moveTo((-99999999, -99999999))
