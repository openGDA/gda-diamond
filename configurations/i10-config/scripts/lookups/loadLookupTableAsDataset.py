'''
Created on 06-Jul-2020

@author: fy65
'''
import csv

def loadDataset(filename):
    '''read a CSV file storing the lookup table data and return a 2-dimensional numerical data set.
    Expects a single header line at the row 0.
    '''
    with open(filename, 'rb') as csvfile:
        lines = csv.reader(csvfile)
        dataset = list(lines)[1:] #skip the header line
        columns = len(next(lines)) # find how many columns in the file
        for x in range(len(dataset)-1):
            for y in range(columns):
                dataset[x][y] = float(dataset[x][y])
    return dataset