from Diamond.Analysis.AnalyserNx import AnalyserNxDetectorClass
from Diamond.Analysis.AnalyserNx import AnalyserNxWithRectangularROIClass

merlinstats = AnalyserNxDetectorClass("merlinstats", merlin, merlin_for_snaps, [MinMaxSumMeanDeviationProcessor()], panelName="Area Detector")
merlinroi = AnalyserNxWithRectangularROIClass("merlinroi", merlin, merlin_for_snaps, [MinMaxSumMeanDeviationProcessor()], panelName="Area Detector")
merlinroisum = AnalyserNxWithRectangularROIClass("merlinroisum", merlin, merlin_for_snaps, [SumProcessor()], panelName="Area Detector")

merlinstats.setAlive(True)
merlinroi.setAlive(True)
merlinroisum.setAlive(True)
