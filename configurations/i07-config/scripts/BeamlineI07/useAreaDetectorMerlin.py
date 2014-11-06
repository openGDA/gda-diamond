from Diamond.Analysis.AnalyserNx import AnalyserNxDetectorClass
from Diamond.Analysis.AnalyserNx import AnalyserNxWithRectangularROIClass

merlinstats = AnalyserNxDetectorClass("merlinstats", merlin, _merlin_for_snaps, [MinMaxSumMeanDeviationProcessor()], panelName="Area Detector")
merlinroi = AnalyserNxWithRectangularROIClass("merlinroi", merlin, _merlin_for_snaps, [MinMaxSumMeanDeviationProcessor()], panelName="Area Detector")
merlinroisum = AnalyserNxWithRectangularROIClass("merlinroisum", merlin, _merlin_for_snaps, [SumProcessor()], panelName="Area Detector")

merlinstats.setAlive(True)
merlinroi.setAlive(True)
merlinroisum.setAlive(True)