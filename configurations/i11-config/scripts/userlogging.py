'''
Automatic user logbook of experimental data

Intended to replace to use of 

    fh = open('/long/absolute/path/to/log/directory', 'a')
    line = str(x()) + ', ' + str(y())) + ', ' + str(z()) + '\\n'
    fh.write(line)

The same behaviour can be achieved using the UserLog with the following

    logbook = UserLog('relative/path', (x, y, z))
    logbook.record()

By default, filenames are relative to the visit directory although if an absolute path is given,
that will be used instead. Subdirectories can be used (eg 'spool/abcd.log' will write to the spool
directory).

The above format assumes x, y and z are scannables. If other values are needed in the logbook, they
can be passed in as a map of name to function providing the value. eg

    logbook = UserLog('filename', (x, y, z), {'epoch': time.time})

will include a unix epoch timestamp for each record.

@author: qan22331
'''
import logging
from os import path
from contextlib import contextmanager
from collections import OrderedDict

from gdascripts.pd.dummy_pds import ZeroInputExtraFieldsDummyPD
from gdaserver import command_server

from gda.data import NumTracker
from gda.jython import InterfaceProvider

logger = logging.getLogger('gda.script.userlogging')

SCAN_NUMBER = 'scan_number'

def _parse_providers(*a, **kw):
    """Combine list of scannables and map of name:provider"""
    providers = OrderedDict(**kw)
    for i, p in enumerate(a):
        if hasattr(p, 'name'):
            providers[p.name] = p
        else:
            providers['value_' + str(i)] = p
    return providers

def _setup_output(filename):
    """
    Get the filepath of the output file

    If the parent directory does not exist, try and create it
    """
    output = path.join(InterfaceProvider.getPathConstructor().getVisitDirectory(), filename)
    logger.debug('Creating user log to write to %s', output)
    if path.exists(output) and not path.isfile(output):
        raise ValueError('filename exists and is not a file')
    if not path.exists(path.dirname(output)):
        print 'Creating parent directory for user log'
        import os
        os.makedirs(path.dirname(output))
    return output

def _csv_header(fields):
    """Format a CSV header from a map of fields"""
    return ','.join(fields) + '\n'
def _csv_data(fields):
    """Format a CSV row from a map of fields"""
    return ', '.join(str(v) for _, v in fields.items()) + '\n'

def getformatters(mode):
    """Get header and line formatters for the given mode"""
    if mode == 'csv':
        return _csv_header, _csv_data
    elif mode == 'json':
        import json
        return lambda x: '', lambda x: json.dumps(x)+'\n'

class UserLog(object):
    def __init__(self, filename, scannables=(), other=None, include_scan_number=True, mode='csv', stdout=False):
        self.filename = _setup_output(filename)
        other = other or {}
        self.providers = _parse_providers(*scannables, **other)
        if include_scan_number and SCAN_NUMBER not in self.providers:
            self.providers[SCAN_NUMBER] = self._scan_number
        self.listener = _ScanListener(self.record)
        self._depth = 0
        self.formatheader, self.formatdata = getformatters(mode)
        self.init = False
        self.stdout = stdout

    @property
    @contextmanager
    def scans(self):
        logger.debug('Entering auto logging block')
        if self._depth == 0:
            command_server.addDefault(self.listener)
        self._depth += 1
        yield
        logger.debug('Leaving auto logging block')
        if self._depth == 1:
            command_server.removeDefault(self.listener)
        self._depth -= 1
    
    def _write_header(self):
        with open(self.filename, 'a') as out:
            out.write(self.formatheader(self.providers))
    
    def record(self):
        """Write out a single record"""
        if not self.init:
            self._write_header()
            self.init = True
        data = self._current_data()
        if self.stdout:
            print ', '.join(k + ': ' + str(v) for k, v in data.items())
        with open(self.filename, 'a') as out:
            out.write(self.formatdata(data))
    
    def _current_data(self):
        return {k: v() for k, v in self.providers.items()}

    def _scan_number(self):
        """Get the current scan number or empty string if no scan is running"""
        if self.listener.in_scan:
            return NumTracker().currentFileNumber
        else:
            return ''

class _ScanListener(ZeroInputExtraFieldsDummyPD):
    """Listener that calls a function at the start of every scan"""
    def __init__(self, fn, *a, **kw):
        """
        Create a scan listener that runs fn(*a, **kw) at the start of each scan
        
        Args:
            fn - The function to run
            *a - positional arguments to pass to the function (fn)
            **kw - keyword arguments to pass to the function (fn)
        """
        super(_ScanListener, self).__init__('foo')
        self.fn = fn
        self.args = a
        self.kwargs = kw
        self.in_scan = False
    def atScanStart(self):
        self.in_scan = True
        self.fn(*self.args, **self.kwargs)
    def atScanEnd(self):
        self.in_scan = False

