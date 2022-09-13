from Diamond.PseudoDevices.MetadataHeaderDevice import MetadataHeaderDeviceClass

# Create header object for detectors to use
pilatusHeader = MetadataHeaderDeviceClass("pilatusHeader");


from gdascripts.scannable.dummy import SingleInputStringDummy

# Device used for recording arbitrary strings in metadata
note = SingleInputStringDummy('note')

# Create detector related pixel metadata
# These are set manually during experiment so initialise to large negative number
from gdascripts.pd.dummy_pds import MultiInputExtraFieldsDummyPD


def makeDummyPD(name):
    device = MultiInputExtraFieldsDummyPD(name, [name], [])
    device.setOutputFormat(["%.0f"])
    device.moveTo(-99999999)
    return device

dpsx_zero = makeDummyPD("dpsx_zero")
dpsx_zero.setOutputFormat(["%f"])
dpsy_zero = makeDummyPD("dpsy_zero")
dpsy_zero.setOutputFormat(["%f"])
dpsz_zero = makeDummyPD("dpsz_zero")
dpsz_zero.setOutputFormat(["%f"])
dpsz2_zero = makeDummyPD("dpsz2_zero")
dpsz2_zero.setOutputFormat(["%f"])

dps_cpx = makeDummyPD("dps_cpx")
dps_cpy = makeDummyPD("dps_cpy")

diff1_cpx = makeDummyPD("diff1_cpx")
diff1_cpy = makeDummyPD("diff1_cpy")

diff2_cpx = makeDummyPD("diff2_cpx")
diff2_cpy = makeDummyPD("diff2_cpy")

