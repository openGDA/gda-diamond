'''
Created on 25 Oct 2017

@author: fy65
'''
import csv

with open("/dls/i06/epics/lookup/gaptoeV10_85_16_66.csv", 'rb') as csvfile:
    lines = csv.reader(csvfile)

    dataset = list(lines)[2:]

    for each in dataset:
        x=[]
        for each2 in each:
            x.append(float(each2))
            
        print x
        print x[10]
            