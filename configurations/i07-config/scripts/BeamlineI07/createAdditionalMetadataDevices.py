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
    device = MultiInputExtraFieldsDummyPD(name, [name + ".x", name + ".y"], [])
    device.setOutputFormat(["%.0f", "%.0f"])
    device.moveTo((-99999999, -99999999))
    return device

dpsx_zero = makeDummyPD("dpsx_zero")
dpsy1_zero = makeDummyPD("dpsy1_zero")
dpsy2_zero = makeDummyPD("dpsy2_zero")
dpsz_zero = makeDummyPD("dpsz_zero")

dps_cpx = makeDummyPD("dps_cpx")
dps_cpy = makeDummyPD("dps_cpy")

diff1_cpx = makeDummyPD("diff1_cpx")
diff1_cpy = makeDummyPD("diff1_cpy")

diff2_cpx = makeDummyPD("diff2_cpx")
diff2_cpy = makeDummyPD("diff2_cpy")

