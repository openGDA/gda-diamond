from scannable.detector import princeton
from gdascripts.scannable.detector.ProcessingDetectorWrapper import ProcessingDetectorWrapper

reload(princeton)

ccddet = princeton.PrincetonDetector('ccddet', x2trig, readout_time=2, filename_fmt='/dls/i16/data/2012/mt7277-1/ccddata/test%i.TIF')

ccd = ProcessingDetectorWrapper('ccd', ccddet, [], root_datadir='/dls/i16/data/2012/mt7277-1/', panel_name_rcp='Plot 1', iFileLoader=TIFFImageLoader, fileLoadTimout=24*3600) 
ccd.display_image = False

ccd.processors=[DetectorDataProcessorWithRoi('max', ccd, [SumMaxPositionAndValue()], False)]

ccdroi = DetectorDataProcessor('ccdroi', ccd, [SumMaxPositionAndValue()])