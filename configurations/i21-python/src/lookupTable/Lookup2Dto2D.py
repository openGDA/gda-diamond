'''
This module defines functions for 2 variable lookup and return another 2 variable from 4 column table.
The lookup is reversible, i.e. it can lookup values in the first 2 column and return values from the next 2 columns, 
or lookup values in the last 2 columns and return values from the first 2 columns.
It supports values at points (i.e. in table rows) that do not form a regular grid. 

The implementation utilises kNN - k Nearest Neighbour Algorithm, and the outputs are linearly interpolated from all data points within a specified window centred at the lookupTable point.
The size of the specified window for each variable can be estimated from the lookupTable table values for that variable, but, in order to ensure there is always return values for the lookupTable,
it is recommended that you must set the window size th be greater than the maximum difference between any two adjacent points. 

In our table here (LinearAngle.csv), we set window size 0.5, 0.5, 0.763, 5.26 for gap, row phase, polarisation, energy, respectively. 
Number of data points used for the linear interpolation is capped to 10 in this software.

Created on 17 Aug 2016

@author: fy65
'''

import csv
import random
from __builtin__ import pow
import math
import operator 
from scipy.interpolate import griddata

trainingSet=[]
testSet=[]
lookupTableFilename=''
lookupTableLoaded=False

def loadDataset(filename, split, trainingSet=[] , testSet=[]):
    '''loads a CSV with the provided filename and splits it randomly into train and test datasets using the provided split ratio.
    '''
    global lookupTableFilename
    global lookupTableLoaded
    with open(filename, 'rb') as csvfile:
        lines = csv.reader(csvfile)
        dataset = list(lines)[1:] #skip the header line
        for x in range(len(dataset)-1):
            for y in range(4):
                dataset[x][y] = float(dataset[x][y])
            if random.random() < split:
                trainingSet.append(dataset[x])
            else:
                testSet.append(dataset[x])
        
        lookupTableFilename=filename
        lookupTableLoaded=True

    
def euclideanDistance(instance1, instance2, index=[]):
    '''calculate the similarity between any two given data instances.
    This is defined as the square root of the sum of the squared differences between the two arrays of numbers.
    It also provides control of which fields to include in the distance calculation.
    '''
    distance = 0
    for x in index:
        distance += pow((instance1[x] - instance2[x]), 2)*[1,1,1,1][x] #weighting on index
    return math.sqrt(distance)

def getNeighbors(trainingSet, testInstance, k, index=[]):
    '''collect the k most similar instances for a given unseen instance. 
    calculating the distance for all instances and selecting a subset with the smallest distance values.
    '''
    distances = []
    for x in range(len(trainingSet)):
        dist = euclideanDistance(testInstance, trainingSet[x], index)
        distances.append((trainingSet[x], dist))
    distances.sort(key=operator.itemgetter(1))
    neighbors = []
    for x in range(k):
        neighbors.append(distances[x][0])
    return neighbors

def checkIfWithinCircle(instance1, instance2, resolution=[], index=[]):
    '''check if the given instance2 falls within the circle centred at instance1 
    with a radius defined by the delta values for the given index items
    '''
    distance = 0
    radiusSquared=0
    for x in index:
        distance += pow((instance1[x] - instance2[x]), 2)
    for r in resolution:
        radiusSquared +=pow(r/2,2)
    if distance < radiusSquared:
        return True
    return False
    
def getPointsWithinCircle(trainingSet, testInstance, resolution=[], index=[]):
    '''return a list of all instances that fall within the circle centred at testInstance 
    with a radius defined by the delta values for the given index items
    '''
    pointsInCircle=[]
    for x in range(len(trainingSet)):
        if checkIfWithinCircle(testInstance, trainingSet[x], resolution, index):
            pointsInCircle.append(trainingSet[x])
    return pointsInCircle


def forwardLookup(gap, rowphase, filename="LinearAngle.csv"):
    if not lookupTableLoaded or lookupTableFilename!=filename:
        loadDataset(filename, 1, trainingSet, testSet)
    testInstance=[float(gap),float(rowphase),0,0]
    #neighbors = getNeighbors(trainingSet, testInstance, 10, [0,1])
    datasetInCircle=getPointsWithinCircle(trainingSet, testInstance, [0.5,0.5], [0,1])
    if len(datasetInCircle)==0:
        raise ValueError, "Input values are outside the lookupTable table boundaries."
    points=[[t[0],t[1]] for t in datasetInCircle]
    values=[(t[2],t[3]) for t in datasetInCircle]
    value = griddata(points, values, testInstance[:2], method='linear')
    return list(value[0])

def reverseLookup(polarisation, energy, filename="LinearAngle.csv"):
    if not lookupTableLoaded or lookupTableFilename!=filename:
        loadDataset(filename, 1, trainingSet, testSet)
    testInstance=[0,0,float(polarisation),float(energy)]
    #neighbors = getNeighbors(trainingSet, testInstance, 10, [2,3])
    datasetInCircle=getPointsWithinCircle(trainingSet, testInstance, [2,15], [2,3])
    if len(datasetInCircle)==0:
        raise ValueError, "Input values are outside the lookupTable table boundaries."
    points=[[t[2],t[3]] for t in datasetInCircle]
    values=[(t[0],t[1]) for t in datasetInCircle]
    value = griddata(points, values, testInstance[2:], method='linear')
    return list(value[0])
    
def main():
    trainingSet=[]
    testSet=[]
    loadDataset('LinearAngle.csv', 1, trainingSet, testSet)
    print 'Train: ' + repr(len(trainingSet))
    print 'Test: ' + repr(len(testSet))
    print
    
    testInstance = [41.65, 19.4, -50, 1000] #[26.4, 20.9, -71.689, 865.78]
    ##print testSet
    #testInstance=testSet[3]
    print "Test Case: " + str(testInstance)
    print
    k = 10
    neighbors = getNeighbors(trainingSet, testInstance, k, [2,3])
    print
    print "reverse lookupTable: 'gap,rowphase=func(polarisation,energy)'"
    print "sorted neighbours:"
    print(neighbors)
    datasetInCircle=getPointsWithinCircle(neighbors, testInstance, [0.763,5.26], [2,3])
    print(datasetInCircle)
    if len(datasetInCircle)==0:
        raise Exception("Cannot find any dataset within specified instance window. Your lookupTable parameters may be outside the lookupTable table boundaries.")
    points=[[t[2],t[3]] for t in datasetInCircle]
    values=[(t[0],t[1]) for t in datasetInCircle]
    value = griddata(points, values, testInstance[2:], method='linear')
    print value
    
    neighbors = getNeighbors(trainingSet, testInstance, k, [0,1])
    print "forward lookupTable: 'polarisation,energy=func(gap,rowphase)'"
    print "sorted neighbours:"
    print(neighbors)
    datasetInCircle=getPointsWithinCircle(neighbors, testInstance, [0.5,0.5], [0,1])
    print(datasetInCircle)
    if len(datasetInCircle)==0:
        raise ValueError, "Input values are outside the lookupTable table boundaries."
    points=[[t[0],t[1]] for t in datasetInCircle]
    values=[(t[2],t[3]) for t in datasetInCircle]
    value = griddata(points, values, testInstance[:2], method='linear')
    print value

if __name__ == "__main__":
    #main()
    print reverseLookup(-30, 800)
    print forwardLookup(25, 17)
    print reverseLookup(-89.773250524, 823.7374929759999)
    print forwardLookup(27.1374738, 28.0)
    
