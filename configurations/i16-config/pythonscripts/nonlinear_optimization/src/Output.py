'''
Created on 9 Jul 2013

@author: James
'''
import numpy as np
from random import *
from initial_setup import*

from gail_shapley import*
#from genetic import *

from xlwt import *
import os

#os.chdir("G:\optimisation")
#os.chdir("/media/sf_Dropbox/workspace/nonlinear_optimization/spreadsheets")
#os.chdir("C:\Users\James\Documents\Oxford\optimisation")
os.chdir("/dls_sw/i16/software/gda/config/pythonscripts/nonlinear_optimization/spreadsheets")
center=easyxf('alignment: horizontal centre;')


def statistics(book):
    d_num_preferences={key: 0 for key in range(number_preferences)}
    for name in names_only:
        num=len(d_preferences[name])
        for n in range(num):
            d_num_preferences[n]+=1
        
    d_preferences_stat={key: 0 for key in range(number_preferences+1)}    
    for x_0 in range(len(names_only)*time_periods):    
        period=int(x_0/len(names_only))
        x=x_0%len(names_only)
        person=names_only[x]
        
        experiment=d_doing[person][period]
        if  experiment in d_preferences[person]:
            preference_count=len(d_preferences[person])
            preference_number=(-1*(d_preferences[person].index(experiment)-preference_count))
            d_preferences_stat[preference_number]+=(1/periods_dict[experiment])
    percentage_dictionary={key: 0 for key in range(number_preferences+1)}
    
    for pref in range(number_preferences):
        percentage=float(d_preferences_stat[pref+1])/d_num_preferences[pref]
        percentage_dictionary[pref+1]=percentage
        
        
               
        
    statistics_sheet = book.add_sheet('statistics', cell_overwrite_ok=True)
    
    statistics_sheet.write(0,0,"choice" ,center)
    statistics_sheet.write(0,1,"Percentage of people doing that preference" ,center)
    for i in range(number_preferences):
        x=i+1
        statistics_sheet.write(x,0,"# %d\t choice" %(x),center)
        
    for i in range(number_preferences):
        x=i+1   
        percent=percentage_dictionary[i+1]
      
        statistics_sheet.write(x,1," %f\t %%" %(percent*100),center)
    return statistics_sheet
    
    
def people_timetable(book):
    timetable_sheet = book.add_sheet('timetable', cell_overwrite_ok=True)
    
    for i in range(time_periods):
        y=i+1
        timetable_sheet.write(0,y,"period %d\n" %(y),center)
    for name in names_only:
        timetable_sheet.write(names_only.index(name)+1,0,name)#A1 is blank
           
    for x_0 in range(len(names_only)):
        for y_0 in range(time_periods):
            x=x_0+1
            y=y_0+1
            person=names_only[x_0]
            experiment=d_doing[person][y_0]
            if experiment in d_preferences[person]:
                    timetable_sheet.write(x,y,experiment,easyxf('alignment: horizontal centre;'  'pattern: pattern solid, fore_colour green;'))
            else:
                timetable_sheet.write(x,y,experiment,center)
            
    return timetable_sheet


def computer_array(book):
    computer_array_sheet = book.add_sheet('computer_array', cell_overwrite_ok=True)
    for experiment in experiments_only:
        computer_array_sheet.write(0,experiments_only.index(experiment)+2,experiment,center)
    for i in range(time_periods):
        for name in names_only:
            x=(i*len(names_only))+(names_only.index(name)+1)
            computer_array_sheet.write(x,1,name)
        x_0=int(1+(i*len(names_only)))
        x_1=x_0-1+len(names_only)
        computer_array_sheet.write_merge(x_0,x_1, 0, 0, "period %d\n" %(i+1)) 
    
    for x in range(len(names_only)*time_periods):
        person=names_only[int(x%len(names_only))]
        for y in range(len(experiments_only)):
            if timetable_arr[x][y]==1:
                if experiments_only[y] in d_preferences[person]:
                    computer_array_sheet.write(x+1,y+2,5-int(d_preferences[person].index(experiments_only[y])),easyxf('alignment: horizontal centre;'  'pattern: pattern solid, fore_colour green;'))
                else:
                    computer_array_sheet.write(x+1,y+2,0,easyxf('alignment: horizontal centre;'  'pattern: pattern solid, fore_colour yellow;'))
    
            else:
                computer_array_sheet.write(x+1,y+2,"-",easyxf('alignment: horizontal centre;'  ))
    
        
    return computer_array_sheet



def user_timetable(book):
    user_timetable_sheet = book.add_sheet('user timetable', cell_overwrite_ok=True)
    for experiment in experiments_only:
        user_timetable_sheet.write(0,experiments_only.index(experiment)+1,experiment,center)
   
    for name in names_only:
        x=(names_only.index(name)+1)
        user_timetable_sheet.write(x,0,name)
         
    
    
    for x_0 in range(len(names_only)*time_periods):
        period=int(x_0/len(names_only))
        x=x_0%len(names_only)
        person=names_only[x]
        for y in range(len(experiments_only)):
            if timetable_arr[x_0][y]==1:
                if experiments_only[y] in d_preferences[person]:
                    user_timetable_sheet.write(x+1,y+1,period+1,easyxf('alignment: horizontal centre;'  'pattern: pattern solid, fore_colour green;'))
                else:
                    user_timetable_sheet.write(x+1,y+1,period+1,easyxf('alignment: horizontal centre;'  'pattern: pattern solid, fore_colour yellow;'))
    
            
            
        
    return user_timetable_sheet



def output():
    book = Workbook()
    timetable_sheet=people_timetable(book)
    computer_array_sheet=computer_array(book)
    user_timetable_sheet=user_timetable(book)
    statistics_sheet=statistics(book)
    book.save('output.xls')
#for i in range(preferences_sheet.nrows):
#
output()
f=0