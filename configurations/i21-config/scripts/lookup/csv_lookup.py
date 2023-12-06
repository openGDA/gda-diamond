'''
a generic function to create lookup table with one or more keys and optional header and units from CSV file

Created on 5 Dec 2023

@author: fy65
'''
import csv

def load_lookup_table_from_csv_file(filename, number_of_keys, header_row_exist = True, units_row_exist = False):
    with open(filename) as csv_data:
        reader = csv.reader(csv_data)
        #skip blank row or comment row - comment must be in first column
        rows = [row for row in reader if row and not row[0].startswith('#')]

        start_data_row = 0
        if header_row_exist:
            header = rows[0]
            start_data_row += 1
        if units_row_exist:
            units = rows[1]
            start_data_row += 1

    lookuptable={}
    for row in rows[start_data_row:]:
        key_tuple = tuple([row[col_index] for col_index in range(number_of_keys)])
        lookuptable[key_tuple]=[float(item) for item in row[number_of_keys:]]
    return lookuptable, header, units  

def test():
    lookuptable, header, units = load_lookup_table_from_csv_file("../../lookupTables/edge_lookup.csv", 2, units_row_exist=True)

    print(''.join((("%18s" if isinstance(v, str) else "%18.4f") % v for v in header)))
    print(''.join([("%18s" if isinstance(v, str) else "%18.4f") % v for v in units]))
    for key, value in sorted(lookuptable.iteritems()):
        data = [key[i] for i in range(len(key))] + [value[i] for i in range(len(value))]
        print(''.join([("%18s" if isinstance(v, str) else "%18.4f") % v for v in data]))

if __name__ == "__main__":
    test()