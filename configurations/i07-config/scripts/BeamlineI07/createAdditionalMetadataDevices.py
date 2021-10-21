from Diamond.PseudoDevices.MetadataHeaderDevice import MetadataHeaderDeviceClass

# Create header object for detectors to use
pilatusHeader = MetadataHeaderDeviceClass("pilatusHeader");


from gdascripts.scannable.dummy import SingleInputStringDummy

# Device used for recording arbitrary strings in metadata
note = SingleInputStringDummy('note')


from gdascripts.pd.dummy_pds import MultiInputExtraFieldsDummyPD

centralPixel = MultiInputExtraFieldsDummyPD('centralPixel', ['centralPixel_x','centralPixel_y'], [])
centralPixel.setOutputFormat(['%.0f', '%.0f'])
centralPixel.moveTo((-99999999, -99999999))
