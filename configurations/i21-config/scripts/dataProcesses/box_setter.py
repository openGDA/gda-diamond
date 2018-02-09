'''

Contains function to set angle of box regions of interest

'''

import scisoftpy as dnp

_PROCESS_NAME = 'RIXS elastic line reduction'
_SANE_PROCESS_NAME = dnp.dictutils.sanitise_name(_PROCESS_NAME, False)
_PROCESSED_FILENAME_BIT_ = '_processed_elastic_line'

def _read_slope(fn, r=0):
    t = dnp.io.load(fn, warn=False)  # @UndefinedVariable
    e = dnp.nexus.find_class(t, dnp.nexus.NXentry)[0][1]
    p = dnp.nexus.find_class(e, dnp.nexus.NXprocess)[0][1]
    notes = dnp.nexus.find_class(p, dnp.nexus.NXnote)
    found = False
    for n, g in notes:
        n = g['name'][...].item(0)
        if _PROCESS_NAME == n:
            # group exists
            found = True
            break
    if not found:
        raise ValueError('File not a elastic line fit file')
    
    for n,v in e['auxiliary'].items():
        if n.endswith(_PROCESS_NAME) or n.endswith(_SANE_PROCESS_NAME):
            slopes = v['line_%d_m/data' % r][...]
            return slopes.item(0)
    raise ValueError('Slope not found in file')

_VISIT = 'cm16767-*'

def set_visit(visit):
    '''
    Set current visit
    '''
    global _VISIT
    _VISIT = visit

def _find_i21_scan_file(scan, visit=None, data_dir='/dls/i21/data', year=None, prefix='i21-'):
    '''
    Get processed file
    :param scan: scan number or scan file or elastic fit file
    :param visit: visit-ID, such as cm1234-1 (defaults to data_dir and its sub-directories)
    :param data_dir: beamline data directory, such as '/dls/i21/data'
    :param year: calendar year (defaults to visit directory and any year in range 2000-99)
    :param prefix: prefix to file name of scan file (defaults to 'i21-')
    '''
    if visit is None:
        visit = _VISIT
    fn = dnp.io.find_scan_files(scan, data_dir, visit=visit, year=year, prefix=prefix, ending='.nxs')  # @UndefinedVariable
    if not fn:
        raise ValueError, 'Could not find scan NeXus file'
    
    return fn[0]

# fn1 = '/scratch/images/i21/rixs/i21-34771_processed_elastic_line_171208_142912.nxs'
# fn2 = '/scratch/images/i21/rixs/i21-38196_processed_elastic_line_180126_114908.nxs'

def _get_slope_from_file(scan, prefix='i21-'):
    from os import path
    if isinstance(scan, int):
        fn = _find_i21_scan_file(scan, prefix=prefix)
    elif isinstance(scan, str):
        fn = scan
    else:
        raise ValueError('scan can only be string or number')
    
    lp = len(prefix)
    if not path.isabs(fn):
        fn = path.basename(fn)
        if not fn.startswith(prefix):
            raise ValueError('File %s does not with correct prefix: %s' % (fn, prefix))
        fn = _find_i21_scan_file(fn[lp:lp+5], prefix=prefix)
    elif not path.basename(fn).startswith(prefix):
        raise ValueError('File %s does not with correct prefix: %s' % (fn, prefix))
    
    if not _PROCESSED_FILENAME_BIT_ in fn:
        from glob import glob, iglob
        pfp = path.basename(fn)[:lp+5] # processed file prefix
        pfg = pfp + _PROCESSED_FILENAME_BIT_+ '*.nxs'
        pd = path.dirname(fn)
        l = glob(path.join(pd, pfg))
        if len(l) == 0:
            pd = path.join(pd, '..')
            l = glob(path.join(pd, pfg))
        if len(l) == 0:
            pd = path.join(pd, 'processing')
            l = glob(path.join(pd, pfg))
        if len(l) == 0:
            raise ValueError('Could not find processed fit file: %s' % fn)
        if len(l) == 1:
            fn = l[0]
        else:
            fn = sorted(l, key=path.getmtime)[-1] # latest only

    slope = _read_slope(fn)
    print('Slope %g found in file %s' % (slope, fn))
    return slope

def set_box(scan_or_slope, name='andor_cam: EPICS Array'):
    '''
    Set box profile to given slope
    :param scan_or_slope: scan number or scan file
     or processed elastic line fit file
     or slope of elastic line (as a float)
    :param name: name of plot view with box region of interest
    '''
    _SUFFIX = 'elastic_line'
    if isinstance(scan_or_slope, int):
        if scan_or_slope == 0:
            raise ValueError('Integer zero is not allowed: use 0.0 to reset slope')
        scan_or_slope = _get_slope_from_file(scan_or_slope)
    elif isinstance(scan_or_slope, str):
        scan_or_slope = _get_slope_from_file(scan_or_slope)

    from math import atan
    angle = atan(scan_or_slope)

    boxes = dnp.plot.getrects(name=name)
    if boxes is None:
        print('No box regions of interest found!')
        return

    for b in boxes.values():
        b.angle = angle
    dnp.plot.setrois(boxes, name=name)

# print _read_slope(fn2)
# set_box(-0.022, name='Dataset Plot')
# print _get_slope_from_file('/scratch/images/i21/rixs/i21-38196.nxs')
# print _get_slope_from_file('/scratch/images/i21/rixs/i21-38196_processed_elastic_line_180119_165545.nxs')

# set_box('/scratch/images/i21/rixs/i21-38196.nxs', name='Dataset Plot')
# set_box('/scratch/images/i21/rixs/i21-38196_processed_elastic_line_180119_165545.nxs', name='Dataset Plot')

