'''
Created on 2 Jul 2013

@author: James
'''
import os
import xlrd
import numpy as np
import time
# need to change directory to where excel document is
#os.chdir("G:\optimisation")
#os.chdir("/media/sf_Dropbox/workspace/nonlinear_optimization/spreadsheets")
os.chdir("/dls_sw/i16/software/gda/config/pythonscripts/nonlinear_optimization/spreadsheets")
#os.chdir("C:\Users\James\Documents\Oxford\optimisation")
#open workbook with preferences and correlation
#workbook_input= xlrd.open_workbook('preferences.xls')
workbook_input= xlrd.open_workbook('preferences_2014_v3.xls')
#workbook_input= xlrd.open_workbook('preferences_tmp1.xls')
key_values=workbook_input.sheet_by_name('key_values')
preferences_sheet= workbook_input.sheet_by_name('candiate_preferences')#Sheet with candidate preferences in it
correlation_sheet= workbook_input.sheet_by_name('experiment_correlation')#Sheet with correlation array--> how closely correlated different experiments are
periods_sheet=workbook_input.sheet_by_name('periods')

t_0=time.clock()

def initialise_values(key_values):
    
    val=(key_values.col_values(1))
    time_periods=int(val[0])
    number_preferences=int(val[1])
    max_number=int(val[2])
    return time_periods, number_preferences, max_number

time_periods, number_preferences, max_number= initialise_values(key_values)


#candidate names, experiment list, dictionary of preferences, dictionary of exclusions for each candidate
def initialise(preferences_sheet):
    #list of candidate names
    names=[]
    names.append(preferences_sheet.col_values(0))
    names=names[0]
    #list of names only
    names_only= [x for x in names if  x not in ""]
    
   
    
    #list of experiments
    experiments=[]
    experiments.append(preferences_sheet.row_values(0))
    experiments=experiments[0]
    #list  of experiments only
    experiments_only= [x for x in experiments if  x not in ""]
        
    
    #dictionary of preferences for each candidate
    d_preferences={key: None for key in names_only}
    #dictionary of exclusions for each candidate
    d_exclusions={key: None for key in names_only}
    #Goes through all candidates by name and adds their preferences/exclusions to the relevant dictionary
    for name in names_only:
        i=names.index(name)# returns index of relevant row in spreadsheet
        preference_list=[""]*number_preferences# 4 item list
        exclusion_list=[]#list of exclusions for that candidate
        p=preferences_sheet.row_values(i)
        for e in range(len(p[1:])):
            if p[1:][e]==0 or p[1:][e]=="":#tests if element is blank or 0 --> in neither list
                continue
            elif isinstance(p[1:][e], float) is not True and isinstance(p[1:][e], int) is not True :# char therefore exclusion
                exclusion_list.append(experiments_only[e])
            else:#Must be in preferences
                preference_list[int(number_preferences-p[1:][e])]=experiments_only[e]# Goes in preference list in correct index--> last preference index 0 first preference index [no. time periods]
            
        while "" in preference_list:
            preference_list.remove("")
        
        
        d_preferences[name]=preference_list
        d_exclusions[name]=exclusion_list
        
    return  names_only, experiments_only, d_preferences, d_exclusions


def initialise_periods(periods_sheet):
    keys=[]
    keys.append(periods_sheet.row_values(0))    
    keys=keys[0][1:]
    keys=[x for x in keys if x not in [0,""]]


    values_1=[]
    values_1.append(periods_sheet.row_values(1))    
    values_1=values_1[0][1:]
    values_1=[int(x) for x in values_1 if x not in [0,""]]
    
    periods_dict= dict(zip(keys,values_1)) 

    values_2=[]
    values_2.append(periods_sheet.row_values(2))    
    values_2=values_2[0][1:]
    values_2=[ x.split(",")[:-1] for x in values_2 if x not in [0,""]]# all elements must end in a comma
    for x in range(len(values_2)):
        for y in range(len(values_2[x])):
            z=values_2[x][y]
            values_2[x][y]=int(z)-1
        
    starting_periods_dict= dict(zip(keys,values_2))




    
    
    
    return periods_dict, starting_periods_dict



#initialise arrays
def initialise_arrays(experiments_only,correlation_sheet,names_only):     
    #array of correlation
    def initialise_correlation_array(experiments_only,correlation_sheet):
        correlation_arr=np.ones((len(experiments_only),len(experiments_only)),dtype=np.int)# initial array all 1
        for x in range(len(experiments_only)):
            for y in range(len(experiments_only)):
                correlation_arr[x][y]=correlation_sheet.cell_value(x+1,y+1)
        return correlation_arr# correleation array is cell values (correlation array is equal to its transpose
    
    #timetable array          
    def initialise_timetable_array(names_only,experiments_only):
        timetable_arr=np.zeros((len(names_only)*time_periods,len(experiments_only)),dtype=np.int)  
        return timetable_arr
   
    correlation_arr=initialise_correlation_array(experiments_only,correlation_sheet)
    timetable_arr=initialise_timetable_array(names_only,experiments_only)
    return correlation_arr,   timetable_arr    

#initialises an array of all 0s in same dimensions as timetable_arr
def initialise_fitness_array(names_only,experiments_only):
        fitness_arr=np.zeros((len(names_only)*time_periods,len(experiments_only)))
        return fitness_arr




names_only, experiments_only, d_preferences, d_exclusions=initialise(preferences_sheet)
correlation_arr, timetable_arr,  =initialise_arrays(experiments_only,correlation_sheet,names_only)
fitness_arr=initialise_fitness_array(names_only,experiments_only)
periods_dict, starting_periods_dict=initialise_periods(periods_sheet)        



#fitness of single element
def fitness_element(x,y,timetable_arr,correlation_arr):
    #returns preference score  --> 1st=4 ... 4th=1  everything else=0
    def fitness_preference(x,y):
        name=names_only[x%(len(names_only))]#name of candidate element being tested
        experiment=experiments_only[y]# experiment they are doing
        if experiment in d_preferences[name]:
            p_value=(1+number_preferences-len(d_preferences[name]))*(number_preferences-len(d_preferences[name]))+d_preferences[name].index(experiment)+3#experiment is in that candidate's preferences
        #if d_preferences[name][-1]==experiment:
         #   p_value=20
        
        else:
            p_value=1
        return p_value
    
    #returns number of people doing experiment
    def fitness_overcrowding(x,y,timetable_arr):
        period=int(x/len(names_only))# 0 denotes first period  (x is an integer --> returns whole number (rounds down))
        first_index=period*len(names_only)# first index of period in timetable_arr
        total_people=timetable_arr[first_index:(first_index+len(names_only)),y].sum()#adds all people doing experiment in that period
        return total_people
    
    #returns correlation of 4 experiments done by each candidate experiment index is the index of the element working out
    def fitness_correlation(x,experiment_index):
        correlation_sum=0# sum of correlation factors for that experiment
        x_0=x%len(names_only)#index of person being tested
        for i in range(time_periods):#goes through all experiments they are doing sums correlation factors
            x_current=i*len(names_only)+x_0#x value in timetable_arr
            for y in range(len(experiments_only)):
                if timetable_arr[x_current][y]==1:
                    correlation_sum+=correlation_arr[experiment_index][y]
                else:
                    continue
        return correlation_sum
    
    #contributions to fitness equation
    p_value=fitness_preference(x,y)
    total_people=fitness_overcrowding(x,y,timetable_arr)
    correlation_sum=fitness_correlation(x,y)
    
    #fitness equation
    def fitness_eqn(p_value,total_people,correlation_sum):
        val=((float(p_value*(6-total_people)))*correlation_sum)
        return val
    
    return fitness_eqn(p_value,total_people,correlation_sum)


#total fitness --> places all the fitness of a single element of the timetable array in a new array (fitness_arr) and sums the values of all the elements.
def total_fitness(names_only,experiments_only,d_preferences,fitness_arr,timetable_arr):
    for x in range(len(names_only)*time_periods):
        for y in range(len(experiments_only)):
            if timetable_arr[x][y]==1:
                fitness_arr[x][y]=fitness_element(x,y,timetable_arr,correlation_arr)
            else:
                fitness_arr[x][y]=0
    sum_fitness=fitness_arr.sum()
    return sum_fitness


current_fitness= total_fitness(names_only,experiments_only,d_preferences,fitness_arr,timetable_arr)  
print periods_dict, starting_periods_dict
print current_fitness 
