'''
Created on 5 Jul 2013

@author: James
'''
import copy
import numpy as np
from random import *
from initial_setup import*




#assigns correct number of experiments to each person
def assign_experiments():
    d_pref=copy.deepcopy(d_preferences)# deep copy --> ensures d_preferences is maintained
    
    d_experiments_doing={key: [] for key in names_only}# dictionary of experiments everyone is doing
    e_available=[]
    for n in range(len(experiments_only)):
        e_available.append([experiments_only[n]]*len(starting_periods_dict[experiments_only[n]]))
    e_available=[ex for sub_e in e_available for ex in sub_e]
    e_available=e_available*(max_number)
    unalocated_people=list(names_only*time_periods)
    while len(unalocated_people)!=0:
        allocated="No"
        ind=int(random()*len(unalocated_people))
        person=unalocated_people[ind]# random person from those left to be allocated in this loop
        periods_left=unalocated_people.count(person)
        
              
        if len(d_pref[person])!=0:#sees if there are no preferences left to be allocated
           
            for i in range(len(d_pref[person])):# loop obtains highest preference
                experiment=d_pref[person][i]
               
                
                if  periods_dict[experiment]<=periods_left and experiment in e_available:
                    new_experiment=experiment
                    allocated="Yes"#person has been allocated experiment
           
                else:
                    (d_pref[person][i])="//#//"
                    
                    continue
            while "//#//" in d_pref[person]:
                d_pref[person].remove("//#//")
            
            if new_experiment=="s":
                    allocated="No"
            
            if allocated=="Yes":
                d_pref[person].remove(new_experiment)
                e_available.remove(new_experiment)
            else:
                continue
        
        
        while allocated=="No":# assigns random experiment  --> possible change so allocates experiment which occurs most and isnt  inthose excluded    i.e least people doing it
                        
            ind=int(random()*len(experiments_only))# random experiment from those available
            new_experiment=experiments_only[ind]
            if new_experiment  in e_available and new_experiment not in d_experiments_doing[person] and new_experiment not in d_exclusions[person] and new_experiment not in d_preferences[person]:#tests if the experiment is in exclusions for that person
                if periods_dict[new_experiment]<=periods_left:
                    e_available.remove(new_experiment)
                    allocated="Yes"
                else:
                    allocated="No"
                    continue
                
            else:
                continue
        
       
        
        if allocated=="Yes":#  remove this (test)
           
            d_experiments_doing[person].append(new_experiment)
            for i in range(int(periods_dict[new_experiment])):
                unalocated_people.remove(person)

        else:
            print  "error - couldn't allocate experiment"
        
        

    
    return d_experiments_doing


#assign each experiment to a time
def assign_times(d_experiments_doing):
    d_doing={key: [""]*time_periods for key in names_only}
    d_experiments_at_each_time={key:[0]*time_periods for key in experiments_only} # dictionary with how many people are doing that experiment at each time in list (index0 is first time period, 1 is 2nd)
    d_times_allocated={key:[] for key in names_only}
    to_be_allocated=list(names_only)*time_periods
    
    
    while len(to_be_allocated)!=0:
        

        ind=int(random()*len(to_be_allocated))
        person=to_be_allocated[ind]#
        
        # allocates longest experiment first
        experiments_left=d_experiments_doing[person]
        longest_time=0
        if experiments_left ==[''] or experiments_left ==[""] or experiments_left ==[]:
            x=raw_input()
        for test_e in experiments_left:
            if periods_dict[test_e]>longest_time:
                longest_time=periods_dict[test_e]
                experiment=test_e
                
        periods_allocated=d_times_allocated[person]# periods already allocated for that person
        allocation_list=list(d_experiments_at_each_time[experiment])
        starting_periods=starting_periods_dict[experiment]
        
        
        #set all periods allocated to max people
        for n in periods_allocated:
            allocation_list[n]=max_number
        
        for n in range(len(allocation_list)):
            if n not in starting_periods:
                allocation_list[n]=max_number
            else:
                continue
                
            
        period=allocation_list.index(min(allocation_list))# index of the minimum value in the list of people doing that experiment
        
        for i in range(periods_dict[experiment]):

            d_doing[person][period+i]=experiment# dictionary with experiment index denoting period
            d_times_allocated[person].append(period+i)# adds period to dictionary under persons name           
            x=names_only.index(person)+((period+i)*len(names_only))# x coordinate in timetable array
            y=experiments_only.index(experiment)# y coordinate
            timetable_arr[x][y]=1 # prints to timetable
            
            d_experiments_at_each_time[experiment][period+i]+=1
            
            to_be_allocated.remove(person)#removes person from list to be allocated
            
        d_experiments_doing[person].remove(experiment)# removes experiment from dictionary from those still to be allocated for that person
    return timetable_arr, d_doing

d_experiments_doing=assign_experiments()
print d_experiments_doing
timetable_arr, d_doing=assign_times(d_experiments_doing)
print d_doing
print d_preferences
print timetable_arr
