'''
functions to set or save motor positions for specified energy edge and SGM grating selection.

set_edge function takes 2 or 3 parameters - edge label and grating (SLVS1 or SLVS2). It moves any scannables 
defined in the header of the lookup table. 3rd parameter is optional lookup file path.

save_edge function takes 1 or 2 parameters - edge label. It saves new edge label along with current positions 
of scannables defined in the header of the lookup table. 2nd parameter is optional lookup file path. 

Created on Oct 7, 2022

@author: fy65
'''
import csv
from gda.factory import Finder
from time import sleep
import os
import numbers

EDGE_GRATING_TABLE = "lookupTables/edge_grating_table.csv"
GDA_CONGIG_PROPERTY = "gda.config"

def load_lookup_table(filename):
    with open(filename) as csv_data:
        reader = csv.reader(csv_data)
        rows = [row for row in reader if row or not row.startswith('#')]
        header = rows[0]
        unit = rows[1]

    lookuptable={}
    for row in rows[2:]:
        #print(row)
        lookuptable[(row[0],row[1])]=[float(item) if item else None for item in row[2:]]
    return lookuptable, header, unit


def is_busy(scannables):
    _busy = False
    for scannable in scannables:
        _busy = _busy or scannable.isBusy()
    return _busy


def set_edge(edge, grating, lookup_table = EDGE_GRATING_TABLE):
    '''move energy and motors positions to the given edge and grating selection
    '''
    from scannable.continuous.continuous_energy_scannables import energy
    if os.path.isabs(lookup_table):
        filename = str(lookup_table)
    else:
        from gda.configuration.properties import LocalProperties
        filename = str(LocalProperties.get('gda.config')+os.pathsep+lookup_table)
    lookuptable, header, unit = load_lookup_table(filename)  # @UnusedVariable
    scannable_names = header[1:]
    scannables = [Finder.find(name) if name != 'energy' else energy for name in scannable_names]
    try:
        positions = lookuptable[(edge,grating)]
    except KeyError as e:
        print("Lookup table does not have key (%s, %s)" % (edge, grating))
        raise e
    if all(v is None for v in positions):
        print("No motor position value for (%s, %s) available in lookup table %s!" % (edge, grating, filename))
        return
    positions.insert(0, grating)
    print('\n'.join('move {0} to {1}'.format(*k) for k in zip(scannable_names, positions)))
    for scannable, position in zip(scannables, positions):
        if position is None:
            print("no position value available for scannable %s" % scannable.getName())
        else:
            scannable.asynchronousMoveTo(position)
    while is_busy(scannables):
        sleep(0.25)
    print("\nmove to (%s, %s) completed." % (edge, grating))
    

def save_edge(edge, lookup_table = EDGE_GRATING_TABLE, keep_order=True):
    '''save new edge or update an existing edge motors' position data in lookup table file given.
    The lookup_table file is default to ${gda.config}/lookupTables/edge_grating_table.csv. User can specify another file with absolute file path.
    '''
    if keep_order:
        save_edge_keep_order(edge, lookup_table)
    else:
        save_edge_not_keep_order(edge, lookup_table)
        
    
def save_edge_keep_order(edge, lookup_table = EDGE_GRATING_TABLE):
    '''save new edge or update an existing edge motors' position data in lookup table file given. It keeps the original data order in the file.
    The lookup_table file is default to ${gda.config}/lookupTables/edge_grating_table.csv. User can specify another file with absolute file path.
    '''
    from scannable.continuous.continuous_energy_scannables import energy
    if os.path.isabs(lookup_table):
        filename = str(lookup_table)
    else:
        from gda.configuration.properties import LocalProperties
        filename = str(LocalProperties.get(GDA_CONGIG_PROPERTY) + os.path.sep + lookup_table)
    lookuptable, header, units = load_lookup_table(filename)  # @UnusedVariable
    scannable_names = header[1:]
    scannables = [Finder.find(name) if name != 'energy' else energy for name in scannable_names] 
    scannable_values = [ round(float(v),4) if isinstance(v, numbers.Number) else str(v) for v in [scannable.getPosition() for scannable in scannables]]
    _updated = False
    from  tempfile import NamedTemporaryFile
    import shutil
    temp_file =  NamedTemporaryFile(delete=False)
    with open(filename, 'r') as csv_file, temp_file:
        reader = csv.DictReader(csv_file, fieldnames=header)
        writer = csv.DictWriter(temp_file, fieldnames=header)
        for row in reader:
            if row[header[0]] == edge and row[header[1]] == scannable_values[0]:
                print("\nUpdate edge (%s, %s)" % (edge, scannable_values[0]))
                _updated = True
                for i in range(len(header[2:])):
                    print("Update '{0}' from {1} to {2}".format(scannable_names[i+1], row[header[i+2]], scannable_values[i+1]))
                    row[header[i+2]] = scannable_values[i+1]
            writer.writerow(row)
        # new edge data are added
        if not _updated:
            print("\nAppend new edge (%s, %s) to lookup table" % (edge, scannable_values[0]))
            new_row = {header[0]: edge}
            for head, value in zip(header[1:], scannable_values):
                print("set '{0}' to {1}".format(head, value))
                new_row[head] = value
            writer.writerow(new_row)
            
    shutil.move(temp_file.name, filename)       

    if _updated:
        print("\nEdge '%s' is updated in lookup table %s" % (edge, filename))
    else:
        print("\nEdge '%s' is added in lookup table %s" % (edge, filename))

def save_edge_not_keep_order(edge, lookup_table = EDGE_GRATING_TABLE):
    '''save new edge or update an existing edge motors' position data in lookup table file given.It does not keep the original data order in the file.
    The lookup_table file is default to ${gda.config}/lookupTables/edge_grating_table.csv. User can specify another file with absolute file path.
    '''
    from scannable.continuous.continuous_energy_scannables import energy
    if os.path.isabs(lookup_table):
        filename = str(lookup_table)
    else:
        from gda.configuration.properties import LocalProperties
        filename = str(LocalProperties.get(GDA_CONGIG_PROPERTY) + os.pathsep + lookup_table)
    lookuptable, header, units = load_lookup_table(filename)  # @UnusedVariable
    scannable_names = header[1:]
    scannables = [Finder.find(name) if name != 'energy' else energy for name in scannable_names] 
    scannable_values = [ round(float(v),4) if isinstance(v, numbers.Number) else str(v) for v in [scannable.getPosition() for scannable in scannables]]
    if (edge, scannable_values[0]) in lookuptable.keys():
        print("\nUpdate (%s, %s)" % (edge, scannable_values[0]))
        _updated = True
        print('\n'.join("Update '{0}' from {1} to {2}".format(*k) for k in zip(scannable_names[1:], lookuptable[(edge, scannable_values[0])], scannable_values[1:])))
    else:
        print("\nAdd new edge (%s, %s) with following data" % (edge, scannable_values[0]))
        _updated = False
        print('\n'.join("'{0}' at {1}".format(*k) for k in zip(scannable_names[1:], scannable_values[1:])))
    lookuptable[(edge, scannable_values[0])] = scannable_values[1:]
    with open(filename, "w") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)
        writer.writerow(units)
        for _edge, _grating in lookuptable.keys():
            writer.writerow([_edge, _grating] + lookuptable[(_edge, _grating)])
    if _updated:
        print("Edge '%s' is updated in lookup table %s" % (edge, filename))
    else:
        print("Edge '%s' is added in lookup table %s" % (edge, filename))
        

def test_edge():
    lookuptable, header, unit = load_lookup_table(str("../../lookupTables/edge_grating_table.csv"))
    for key, value in lookuptable.iteritems():
        print(key, value)
    print('\n')
    print(lookuptable)
    print(header)
    print(unit)
    print(lookuptable[("V L-edge","SVLS1")])
    try:
        print(lookuptable[("V L-edge","SVLS3")])
    except KeyError as e:
        print("Key (%s, %s) is not in the lookup table." % ("V L-edge","SVLS3") )
        raise e
    
if __name__ == "__main__":
    test_edge()