'''
Created on 17 Apr 2018

@author: fy65
'''
import csv

DEBUG=False

def loadCVSTable(filename):
    with open(filename) as csv_data:
        reader = csv.reader(csv_data)
    
        # eliminate blank rows if they exist
        rows = [row for row in reader if row]
        headings = rows[0] # get headings
        units = row[1] # get units
    
        table = {}
        for row in rows[2:]:
            # append the data item to the end of the dictionary entry
            # set the default value of [] if this key has not been seen
            for col_header, data_column in zip(headings, row):
                table.setdefault(col_header, []).append(float(data_column))
        if DEBUG:
            for key in table.keys():
                print key + ':' + str(table[key])
            
    return table

if DEBUG:
    table=loadCVSTable("../../lookupTables/idu_circ_neg_energy2motorPosition.csv")
    for key in table.keys():
        print dict(zip(table['energy'], table[key]))
