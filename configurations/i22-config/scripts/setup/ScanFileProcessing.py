from gdascripts.analysis.datasetprocessor.oned import GaussianEdge, GaussianPeakAndBackground
from gdascripts.analysis.io import ScanFileLoader
import scisoftpy as dnp
import os
from gdascripts.scan.process.ScanDataProcessorResult import ScanDataProcessorResult
import sys


class FileProcessResult:
    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            setattr(self, k, v)

def getFileProcessor(scanProcessor):#, namespace):
    def process1d(file_desc, *scannables):
        """Perform 1d processing on scan

        input:
        - file: this can be the number, name or the full path
        - scannables: (optional) the scannables (either directly or by name) to use for the
          processing. If none are given, two will be chosen but not necessarily the same ones
          chosen at the end of the scan.

        output:
        - a results object is added to the namespace so individual values can be accessed
          eg. results.peak.pos
        - if a variable called results already exists, it will not be overwritten and the
          results will be returned instead
        examples:
        process1d(12345) -> perform processing on file 12345
        process1d(12345, x, bs1diode) -> perform processing using scannables x and bsdiode
        process1d("i22-12132.nxs", "x", "tmp-scannable") -> use scannables x and "tmp-scannable"
          if tmp-scannable no longer exists, referencing it by name is required

        If the function has been aliased in gda, you can omit the brackets and commas
        eg: process1d 12345 x bsdiode

        The processing done is the same as that at the end of a scan although the results
        might be slightly different due to the fitting routine.
        """

        return _fileProcess(file_desc, scannables, processor=scanProcessor)#, ns=namespace)
    return process1d

def _fileProcess(file_desc, scannables, processor=None):#, ns=None):
    if not processor:
        print "No processors provided"
        return

    data = ScanFileLoader.ScanFileLoader(file_desc).getSFH()
    if not data:
        print "No data returned"
        return

    paths = _getPaths(data, scannables)

    snames = [path[path.rfind('/') + 1:] for path in paths]
    print "x: %s, y: %s" %tuple(snames)
    x_data, y_data = _getDatasets(data, paths)

    if not len(x_data.shape) == len(y_data.shape) == 1:
        print "Can only process 1D data"
        return

    fit_results = []
    results = FileProcessResult()
    error = None
    try:
        dnp.plot.clear(name="Scan Plot 1")
        dnp.plot.plot(x_data, y_data, name="Scan Plot 1")
        for sp in processor.processors:
            res = sp.process(x_data, y_data)
            fit_results.append(res)
            setattr(results,sp.name,FileProcessResult(**res.resultsDict))
    except ValueError, e:
        error = "Could not process file: %s" %e

    if error:
        print error
    else:
        print '\n'.join([res.report for res in fit_results])

    ns = processor.rootNamespaceDict
    if ns.has_key('results') and not isinstance(ns['results'], FileProcessResult):
        print "not overriding results object"
        return results
    else:
        ns['results'] = results

def _getDatasets(data, paths):
    return [_getData(data, path) for path in paths]

def _getPaths(data, scannables):
    if scannables:
        paths = _getScannablePaths(data, scannables)
    else:
        paths = _getDefaultPaths(data)

    if len(paths) < 2:
#         print "Not enough scannables to plot"
        raise ValueError("Not enough scannables to plot")
    if len(paths) > 2:
        print "Too many scannables, only first two will be used"
    paths = paths[:2]
    return paths


def _getDefaultPaths(data):
    defaults = []
    primary = None
    for path in list(data.getNames()):
        if "default" in path:
            try:
                md = data.getMetadata()
                if md.getMetaValue("%s@primary" %path):
                    primary = path
                else:
                    defaults.append(path)
            except Exception, e:
                "Couldn't read metadata"
    if primary:
        defaults.insert(0, primary)
    return defaults

def _getScannablePaths(data, scannables):
    paths = []
    for s in scannables:
        try:
            name = (s.inputNames + s.extraNames)[0]
        except AttributeError:
            name = str(s)
        for path in list(data.getNames()):
            if name in path:
                paths.append(path)
                break
    if len(paths) != len(scannables):
        print "Not all scannables found"
    return paths

def _getData(data, scannable):
    try:
        names = list(scannable.getExtraNames()) + list(scannable.getInputNames())
        dataset = data.getLazyDataset(scannable.getName() + "." + names[0]).getSlice(None)
    except AttributeError, ae:
        #scannable is a path
        dataset = data.getLazyDataset(scannable).getSlice(None)
    return dnp.array(dataset)
