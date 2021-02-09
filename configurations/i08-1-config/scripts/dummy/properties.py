
from gda.factory import Finder
import json

print("Running properties.py")

rcp = Finder.find("RCPController")

detectors_property = "uk.ac.diamond.daq.mapping.ui.experiment.detectorssection.detectors"
region_and_path_property = "uk.ac.diamond.daq.mapping.ui.experiment.regionandpathsection.regionandpath"

def det_reset():
    rcp.resetPreference(detectors_property)

def det_set(props):
    rcp.setPreference(detectors_property, json.dumps(props))

def rp_reset():
    rcp.resetPreference(region_and_path_property)

def rp_set(props):
    rcp.setPreference(region_and_path_property, json.dumps(props))

det1 = {"Andor software": 0.1} # <detector name>:<exposure time>
det2 = {"Simulated motors for mapping": 0.3}
det3 = {"Andor software": "invalid"}
det4 = {"Fred": 0.1}
det5 = {"Simulated motors for mapping": None}
det6 = {"Fred": 1.2, "Bert": 0.45}
det7 = {"Andor software": 1}
det8 = {"Simulated motors for mapping": 0.3, "Andor software": 0.1}

rp1 = {"region": "Centred Rectangle", "path": "Raster", "xCentre": 450, "xRange": 0.1, "yCentre": 425, "yRange": 0.12, "xAxisStep": 0.03, "yAxisStep": 0.04, "alternating": True, "continuous": False, "orientation": "vertical"}
rp1a = {"region": "Centred Rectangle", "path": "Raster", "xCentre": 350, "xRange": 0.15, "yCentre": 325, "yRange": 0.22, "xAxisStep": 0.035, "yAxisStep": 0.045, "alternating": False, "continuous": True, "orientation": "horizontal"}

rp2 = {"region": "Rectangle", "path": "Grid", "xStart": 50, "xStop": 100, "yStart": 50, "yStop": 100, "xAxisPoints": 6, "yAxisPoints": 7, "alternating": True, "continuous": False, "orientation": "vertical"}
rp2a = {"region": "Rectangle", "path": "Grid", "xStart": 70, "xStop": 120, "yStart": 70, "yStop": 120, "xAxisPoints": 8, "yAxisPoints": 9, "alternating": False, "continuous": True, "orientation": "horizontal"}

rp3 = {"region": "Circle", "path": "Grid", "xCentre": 60, "yCentre": 55, "radius": 12}
rp3a = {"region": "Circle", "path": "Grid", "xCentre": 70, "yCentre": 65, "radius": 14}

rp4 = {"region": "Circle", "path": "Spiral", "xCentre": 60, "yCentre": 55, "radius": 12, "scale": 0.8}
rp4a = {"region": "Circle", "path": "Spiral", "xCentre": 70, "yCentre": 65, "radius": 14, "scale": 0.74}

rp5 = {"region": "Line", "path": "Equal Spacing", "xStart": 50, "xStop": 100, "yStart": 50, "yStop": 100}
rp5a = {"region": "Line", "path": "Step", "xStart": 60, "xStop": 90, "yStart": 54, "yStop": 97}

rp6 = {"region": "Point", "path": "Single point", "xPosition": 53.3, "yPosition": 42.2}
rp6a = {"region": "Point", "path": "Single point", "xPosition": 55.8, "yPosition": 49.9}

rp7 = {"region": "Rectangle", "path": "Random Offset Grid", "offset": 3.4, "seed": 4629}
rp7a = {"region": "Rectangle", "path": "Random Offset Grid", "offset": 2.56, "seed": 3852}

rp8 = {"region": "Rectangle", "path": "Lissajous Curve", "a": 3.4, "b": 2.75, "points": 50}
rp8a = {"region": "Rectangle", "path": "Lissajous Curve", "a": 9.21, "b": 8.2, "points": 42}

rp9 = {"path": "Raster"}

rp10 = {"path": "Grid"}

rp11 = {"path": "Fred"}

rp12 = {"region": "Fred"}
