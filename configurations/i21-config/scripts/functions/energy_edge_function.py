'''
Created on 5 Dec 2023

@author: fy65
'''
from lookup.csv_lookup import load_lookup_table_from_csv_file
from gda.factory import Finder
from gda.configuration.properties import LocalProperties

edge_lookup_file = str(LocalProperties.get("gda.config")) + "/lookupTables/edge_lookup.csv"

def edge(name, sgm_grating = None, filename = edge_lookup_file):
    from scannable.continuous.continuous_energy_scannables import energy
    lookup_table, header, unit = load_lookup_table_from_csv_file(filename, 2, units_row_exist=True)
    sgm_grating_scannable = Finder.find(header[1])
    if not sgm_grating:
        #if sgm grating select is not provided, get it from the device
        sgm_grating = str(sgm_grating_scannable.getPosition())
        sgm_grating_provided = False
    else:
        sgm_grating_provided = True
   
    if (name, sgm_grating) not in lookup_table.keys():
        raise ValueError("Look up keys %r is not in the given look up table file %s" % ((name, sgm_grating), filename ))
    
    motor_positions = lookup_table[(name, sgm_grating)]
    scannables = [Finder.find(scannable_name) if name != 'energy' else energy for scannable_name in header[2:]]

    if sgm_grating_provided:
        print("move sgmGratingSelect to %s" % sgm_grating)
        sgm_grating_scannable.asynchronuousMoveTo(sgm_grating)
        
    print('\n'.join("move {} to {} {}".format(*k) for k in zip(header[2:], motor_positions, unit[2:])))
    [scannable.asynchronuousMoveTo(float(position)) for scannable, position in zip(scannables, motor_positions)]
    sgm_grating_scannable.waitWhileBusy()
    [scannable.waitWhileBusy() for scannable in scannables]
    print("move to edge %s completed." % name)

def display_edge_table():
    lookuptable, header, units = load_lookup_table_from_csv_file(edge_lookup_file, 2, units_row_exist=True)

    print(''.join((("%18s" if isinstance(v, str) else "%18.4f") % v for v in header)))
    print(''.join([("%18s" if isinstance(v, str) else "%18.4f") % v for v in units]))
    for key, value in sorted(lookuptable.iteritems()):
        data = [key[i] for i in range(len(key))] + [value[i] for i in range(len(value))]
        print(''.join([("%18s" if isinstance(v, str) else "%18.4f") % v for v in data]))

if __name__ == "__main__":
    display_edge_table()       
   