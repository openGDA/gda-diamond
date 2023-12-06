'''
functions to set or save motor positions for specified energy edge and SGM grating selection.

set_edge function takes 1, 2 or 3 parameters - edge name is essential, sgm grating (SLVS1, SVLS2 or SLVS3) is optional 
- it is not given it uses current sgm grating in EPICS device. 
It moves all scannables defined in the header of the lookup table if position value are exist. 3rd parameter is optional lookup file path.

save_edge function takes 1 or 2 parameters - edge label. It saves new edge label along with current positions 
of scannables defined in the header of the lookup table. 2nd parameter is optional lookup file path. 

Created on Oct 7, 2022
Updated on Dec 6, 2023

@author: fy65
'''
import csv
from gda.factory import Finder
from time import sleep
import os
import numbers
from lookup.csv_lookup import load_lookup_table_from_csv_file

EDGE_GRATING_TABLE = "lookupTables/edge_lookup.csv"
GDA_CONGIG_PROPERTY = "gda.config"


def is_busy(scannables):
    _busy = False
    for scannable in scannables:
        _busy = _busy or scannable.isBusy()
    return _busy

def load_lookup_table(lookup_table):
    if os.path.isabs(lookup_table):
        filename = str(lookup_table)
    else:
        from gda.configuration.properties import LocalProperties
        filename = os.path.join(str(LocalProperties.get('gda.config')), lookup_table)
    lookuptable, header, unit = load_lookup_table_from_csv_file(filename, 2, units_row_exist=True)
    return header, lookuptable, filename, unit

def set_edge(edge, sgm_grating = None, lookup_table = EDGE_GRATING_TABLE):
    '''move energy and motors positions to the given edge and sgm_grating selection
    '''
    from scannable.continuous.continuous_energy_scannables import energy
    
    header, lookuptable, filename, unit = load_lookup_table(lookup_table)
    
    scannable_names = header[1:]
    scannables = [Finder.find(name) if name != 'energy' else energy for name in scannable_names]
    
    if not sgm_grating:
        sgm_grating = str(scannables[0].getPosition())
        sgm_grating_provided = False
    else:
        sgm_grating_provided = True
        
    try:
        positions = lookuptable[(edge,sgm_grating)]
    except KeyError as e:
        print("Lookup table does not have key (%s, %s)" % (edge, sgm_grating))
        raise e
    #handle empty row
    if all(v is None for v in positions):
        print("No motor position value for (%s, %s) available in lookup table %s!" % (edge, sgm_grating, filename))
        return
    
    if sgm_grating_provided:
        print("move %s to %s" % (scannables[0].getName(), sgm_grating))
        scannables[0].asynchronuousMoveTo(sgm_grating)
        
    print('\n'.join('move {0} to {1} {2}'.format(*k) for k in zip(scannable_names[1:], positions, unit)))
    for scannable, position in zip(scannables[1:], positions):
        if position is None:
            print("no position value available for scannable %s" % scannable.getName())
        else:
            scannable.asynchronousMoveTo(position)
            
    while is_busy(scannables):
        sleep(0.25)
    print("\nmove to (%s, %s) completed." % (edge, sgm_grating))
    

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
    The lookup_table file is default to ${gda.config}/lookupTables/edge_lookup.csv.
    '''
    from scannable.continuous.continuous_energy_scannables import energy
    header, _, filename, _ = load_lookup_table(lookup_table)
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
    The lookup_table file is default to ${gda.config}/lookupTables/edge_grating_table.csv.
    '''
    from scannable.continuous.continuous_energy_scannables import energy
    header, lookuptable, filename, unit = load_lookup_table(lookup_table)
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
        writer.writerow(unit)
        for _edge, _grating in lookuptable.keys():
            writer.writerow([_edge, _grating] + lookuptable[(_edge, _grating)])
    if _updated:
        print("Edge '%s' is updated in lookup table %s" % (edge, filename))
    else:
        print("Edge '%s' is added in lookup table %s" % (edge, filename))
        
def display_edge_table(lookup_table = EDGE_GRATING_TABLE):
    header, lookuptable, filename, unit = load_lookup_table(lookup_table)
    print(''.join((("%18s" if isinstance(v, str) else "%18.4f") % v for v in header)))
    print(''.join([("%18s" if isinstance(v, str) else "%18.4f") % v for v in unit]))
    for key, value in sorted(lookuptable.iteritems()):
        data = [key[i] for i in range(len(key))] + [value[i] for i in range(len(value))]
        print(''.join([("%18s" if isinstance(v, str) else "%18.4f") % v for v in data]))
    print("\nFile location at %s" % filename) 
        
           
def test_edge():
    header, lookuptable, filename, unit = load_lookup_table(EDGE_GRATING_TABLE)
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
        # raise e
    
if __name__ == "__main__":
    test_edge()
    print('')
    display_edge_table()
    