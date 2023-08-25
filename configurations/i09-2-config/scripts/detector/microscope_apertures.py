'''
Created on 25 Aug 2023

@author: fy65
'''
from gdaserver import gaussian_select, fourier_select  # @UnresolvedImport

MOVE_COMPLETED = "Move completed"

#Gaussian Positioner position names
def FA1():
    print("Move Gaussian to '3.5 mm'")
    gaussian_select.moveTo("3.5 mm")
    print(MOVE_COMPLETED)
    
def FAgrid():
    print("Move Gaussian to 'Gauss grid'")
    gaussian_select.moveTo("Gauss grid")
    print(MOVE_COMPLETED)
    
def FA3():
    print("Move Gaussian to '1.5 mm'")
    gaussian_select.moveTo("1.5 mm")
    print(MOVE_COMPLETED)
    
def FA4():
    print("Move Gaussian to '800 um'")
    gaussian_select.moveTo("800 um")
    print(MOVE_COMPLETED)
    
def FA5():
    print("Move Gaussian to '500 um'")
    gaussian_select.moveTo("500 um")
    print(MOVE_COMPLETED)
    
def FA6():
    print("Move Gaussian to '300 um'")
    gaussian_select.moveTo("300 um")
    print(MOVE_COMPLETED)
    
def FA7():
    print("Move Gaussian to '150 um'")
    gaussian_select.moveTo("150 um")
    print(MOVE_COMPLETED)
    
def FA8():
    print("Move Gaussian to '100 um'")
    gaussian_select.moveTo("100 um")
    print(MOVE_COMPLETED)
    
def FA9():
    print("Move Gaussian to '40 um'")
    gaussian_select.moveTo("40 um")
    print(MOVE_COMPLETED)
    
#Fourier Position position names
def CA1():
    print("Move Fourier to 'open'")
    fourier_select.moveTo("open")
    print(MOVE_COMPLETED)
    
def CAgrid():
    print("Move Fourier to 'k grid'")
    fourier_select.moveTo("k grid")
    print(MOVE_COMPLETED)
    
def CA3():
    print("Move Fourier to 'PEEM 1'")
    fourier_select.moveTo("PEEM 1")
    print(MOVE_COMPLETED)
    
def CA4():
    print("Move Fourier to 'PEEM 2'")
    fourier_select.moveTo("PEEM 2")
    print(MOVE_COMPLETED)
    
def CA5():
    print("Move Fourier to 'PEEM 3'")
    fourier_select.moveTo("PEEM 3")
    print(MOVE_COMPLETED)
    
from gda.jython.commands.GeneralCommands import alias
alias("FA1")    
alias("FAgrid")    
alias("FA3")    
alias("FA4")    
alias("FA5")    
alias("FA6")    
alias("FA7")    
alias("FA8")    
alias("FA9")    

alias("CA1")    
alias("CAgrid")    
alias("CA3")    
alias("CA4")    
alias("CA5")    
