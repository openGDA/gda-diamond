#import __main__
from __main__ import gca, plot, axis

def fit(func, aXis=None):
    '''
    fit(func): fit first line in current axis using quickfit function func
    fit(func, axis): do the same for the line in a specified axis
    fit is designed to be simple with limited functionality
    Use fit function directly for a more sophistcated fit
    '''
    if aXis==None:
        aXis=gca()
    [xData, yData]=aXis.get_lines()[0].get_xydata().transpose()
    print func.fit(xData, yData)
    plot(xData, func(xData),'r-'); axis('tight')
