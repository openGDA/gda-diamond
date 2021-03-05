from gda.factory import Finder
import json

print("Running gui_automation.py")

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

det1 = {"Xspress3 software": 0.1} # <detector name>:<exposure time>
det2 = {"Simulated motors for mapping": 0.3}
det3 = {"Xspress3 software": "invalid"}
det4 = {"Simulated motors for mapping": 0.3, "Xspress3 software": 0.1}

rp1 = {"region": "Centred Rectangle", "path": "Raster", "xCentre": 4.5, "xRange": 0.1, "yCentre": -4.3, "yRange": 0.12, "xAxisStep": 0.03, "yAxisStep": 0.04, "alternating": True, "continuous": False, "orientation": "vertical"}
rp1a = {"region": "Centred Rectangle", "path": "Raster", "xCentre": 3.6, "xRange": 0.15, "yCentre": 2.1, "yRange": 0.22, "xAxisStep": 0.035, "yAxisStep": 0.045, "alternating": False, "continuous": True, "orientation": "horizontal"}

rp2 = {"region": "Rectangle", "path": "Grid", "xStart": 50, "xStop": 100, "yStart": 50, "yStop": 100, "xAxisPoints": 6, "yAxisPoints": 7, "alternating": True, "continuous": False, "orientation": "vertical"}
rp2a = {"region": "Rectangle", "path": "Grid", "xStart": 70, "xStop": 120, "yStart": 70, "yStop": 120, "xAxisPoints": 8, "yAxisPoints": 9, "alternating": False, "continuous": True, "orientation": "horizontal"}

rp3 = {"region": "Circle", "path": "Grid", "xCentre": 6.0, "yCentre": 5.15, "radius": 0.12}
rp3a = {"region": "Circle", "path": "Grid", "xCentre": 7.0, "yCentre": 2.5, "radius": 0.14}

rp4 = {"region": "Circle", "path": "Spiral", "xCentre": 6.0, "yCentre": 5.15, "radius": 0.12, "scale": 0.8}
rp4a = {"region": "Circle", "path": "Spiral", "xCentre": 7.0, "yCentre": 2.1, "radius": 0.14, "scale": 0.74}

rp5 = {"region": "Line", "path": "Equal Spacing", "xStart": 5.0, "xStop": 6.3, "yStart": 5.0, "yStop": 5.2, "points": 4}
rp5a = {"region": "Line", "path": "Equal Spacing", "xStart": 4.2, "xStop": 4.6, "yStart": -1.4, "yStop": 0.98, "points": 9}

rp5b = {"region": "Line", "path": "Step", "xStart": 6.0, "xStop": 6.9, "yStart": -3.2, "yStop": -1.2, "step": 0.4, "alternating": True, "continuous": False}
rp5c = {"region": "Line", "path": "Step", "xStart": 6.5, "xStop": 6.7, "yStart": 0.12, "yStop": 0.85, "step": 1.2, "alternating": False, "continuous": True}

rp6 = {"region": "Point", "path": "Single point", "xPosition": 5.33, "yPosition": 4.2}
rp6a = {"region": "Point", "path": "Single point", "xPosition": 5.58, "yPosition": 4.9}

rp7 = {"region": "Centred Rectangle", "path": "Random Offset Grid", "offset": 3.4, "seed": 4629, "xAxisPoints": 10, "yAxisPoints": 10}
rp7a = {"region": "Centred Rectangle", "path": "Random Offset Grid", "offset": 2.56, "seed": 3852, "xAxisPoints": 15, "yAxisPoints": 15}

rp8 = {"region": "Centred Rectangle", "path": "Lissajous Curve", "a": 3.4, "b": 2.75, "points": 50}
rp8a = {"region": "Centred Rectangle", "path": "Lissajous Curve", "a": 9.21, "b": 8.2, "points": 42}

rp9 = {"region": "Centred Rectangle", "path": "Ptychography Grid", "overlap": 0.001, "randomOffset": 2.75, "alternating": True, "continuous": False}
rp9a = {"region": "Centred Rectangle", "path": "Ptychography Grid", "overlap": 0.002, "randomOffset": 8.2, "alternating": False, "continuous": True}
