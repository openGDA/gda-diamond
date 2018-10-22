import math
import scisoftpy as dnp



#To create a mesh grid

#def grid(xList, yList):
xList=range(5); yList=range(3);

x=dnp.arange(len(xList) * len(yList));
x=x.reshape([len(xList), len(yList)]);






