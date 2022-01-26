'''
Created on 6 Jul 2013

@author: James
'''
import numpy as np
from random import *
from initial_setup import*
from suboptimal_array_creation import*
#from genetic import *
import matplotlib.pyplot as plt
#from random_table import*
termination_value=40# max number of iterations

periods_dict, starting_periods_dict

#Works out total number of people doing a specific experiment in timetable_arr in the same period as the x value
def total_people(x,i,timetable_arr):
        period=int(x/len(names_only))# period x is in; 0 denotes first period  (x is an integer --> returns whole number (rounds down)
        first_index=period*len(names_only)#First index of the period
        number_people=timetable_arr[first_index:(first_index+len(names_only)),i].sum()#works out how many people are doing the experiment in that period
        return number_people


#test if they would prefer to do a different experiment at that time
def different_experiment_test(x,y,timetable_arr,d_doing,possible_changes):
    fitness_arr=initialise_fitness_array(names_only,experiments_only)#fitness array set to zeros
    current_fitness=total_fitness(names_only,experiments_only,d_preferences,fitness_arr,timetable_arr)#current value of fitness (before any changes made)
    fitness_list=[0]*len(experiments_only)#elements in fitness list will be the fitness of the new array if the corresponding experiment was chosen
    person=names_only[x%len(names_only)]# person being tested
    
    current_experiment=experiments_only[y]
    starting_period=int(x/len(names_only))# starting  period  of experiment being tested
    experiment_length=periods_dict[current_experiment]# number of periods experiment takes
    
    
    fitness_dict={}
    possible_experiments=experiments_only
    for experi in experiments_only:
        if experi in d_doing[person] or experi in d_exclusions[person] or periods_dict[experi]>experiment_length:
            possible_experiments.remove(experi)
        else:
            continue
    
    
    possible_experiments_list=[]
    
    for i in range(experiment_length):
        period=starting_period+i
        for experi in possible_experiments:
            x_0=period*len(names_only)
            y_test=experiments_only.index(experi)
            period_possible_experiments=possible_experiments
            if total_people(x_0,y_test,timetable_arr)>5:
                period_possible_experiments.remove(experi)
            else:
                continue
            possible_experiments_list.append([period_possible_experiments])
            
    
    
        
    for i in range(experiment_length):
        period="period_%d" %(i)
        fitness_dict[period]=""#List of total fitness if experiment was switched with the one in the corresponding period
    
    test_timetable=timetable_arr.copy()
    

    
    
          
    test_timetable=timetable_arr.copy()
    for i in range(experiment_length):
        test_timetable[x+(i*len(experiments_only))][y]=0# sets timetable_arr so no experiment is assigned before test
    #go through each experiment at that time and see if they would prefer to do it
    #POSSIBLE alteration--> only test elements affected
    for i in range(len(experiments_only)):
        #experiment can only be changed to experiments they aren't already doing and not in exclusions
        if experiments_only[i] in d_doing[person]: 
            fitness_list[i]=0
        elif experiments_only[i] in d_exclusions[person]:
            fitness_list[i]=0
        #test if the max number of people are already assigned in the relevant period
        elif total_people(x,i,timetable_arr)>5:
            fitness_list[i]=0
        #Experiment is available to the candidate --> ass fitness value to fitness_list
        else:
            test_timetable[x][i]=1
            fitness_list[i]=total_fitness(names_only,experiments_only,d_preferences,fitness_arr,test_timetable)
            test_timetable[x][i]=0#returns test_timetable to original
    
    #tests if fitness can be increased
    if max(fitness_list)>current_fitness:#Yes fitness can be increased
        timetable_arr[x][y]=0#removes current experiment from timetable_arr 
        i=fitness_list.index(max(fitness_list))# index of max value in fitness_list -->same as index of experiment
        timetable_arr[x][i]=1#Adds new experiment to timetable _arr
        d_doing[person][d_doing[person].index(experiments_only[y])]=experiments_only[i]#Replaces old experiment with new one in dictionary of experiments doing (stays in correct index)
        possible_changes= timetable_arr.copy()
        y=i#y value that can be switched in switch_experiment_test() is now i
        change="Yes"
    
    else:#no change
        timetable_arr[x][y]=1#resets timetable array to before
        change="No"#removes element --> ensures isn't re tested
       
    
    return timetable_arr, possible_changes, d_doing, change, y




#test if they would prefer to do the current experiment at a different time
def switch_experiment_test(x,y,timetable_arr,d_doing,possible_changes,change):
    
    fitness_arr=initialise_fitness_array(names_only,experiments_only)#fitness array set to zeros
    current_fitness=total_fitness(names_only,experiments_only,d_preferences,fitness_arr,timetable_arr)
    person=names_only[x%len(names_only)]# person being tested
    current_experiment=experiments_only[y]
    starting_period=int(x/len(names_only))# starting  period  of experiment being tested
    experiment_length=periods_dict[current_experiment]# number of periods experiment takes
    
    
    fitness_list=[""]*len(starting_periods_dict[current_experiment])#List of total fitness if experiment was switched with the one in the corresponding period
    
    test_timetable=timetable_arr.copy()
    

    for i in range(len(starting_periods_dict[current_experiment])): 
        starting_period_test=starting_periods_dict[current_experiment][i]
        x_0=int(names_only.index(person)+(starting_period_test*len(names_only)))#x coordinate  of experiment in array
        
        
        #  list of experiments that will change period
        experiments_switching=[]
        for n in range(experiment_length):
            period=starting_period_test+n
            experiments_switching.append(d_doing[person][period])
            
        #test moving test experiment to new period will mean too many     
        # can't have more that 6 people in one period
        #current experiment moving to new period
        if total_people(x_0,y,timetable_arr)>6:
            fitness_list[i]=0 #--> will mean that the person moving to new period will have at least 7 people in it.
        
        #tests if experiment in new period mean too many people if moved to current period
        for n in range(experiment_length):
            experiment_test=experiments_switching[n]
            y_test=experiments_only.index(experiment_test)
            x_test= x+n*len(names_only)
            if total_people(x_test,y_test,timetable_arr)>5:
                fitness_list[i]=0   
            
            #test if experiment will mean overlap
            if periods_dict[experiment_test]>(periods_dict[current_experiment]-n):
                fitness_list[i]=0 
        
        if fitness_list[i]=="":#Acceptable switch    
            if experiment_length>1:
                z=1
            
            for n in range(experiment_length):
            
            #removes experiments from period moving to
                experiment_n=experiments_switching[n]
                y_n=experiments_only.index(experiment_n)
                x_n= x_0+n*len(names_only)
                test_timetable[x_n][y_n]=0
                
            #remove current experiment from current period    
                x_m=x+n*len(names_only)
                test_timetable[x_m][y]=0
            
            #current experiment to  new  period
                test_timetable[x_n][y]=1
            
            
            #new experiments  to current period
                
                test_timetable[x_m][y_n]=1
            
            
            #fitness test    
            fitness_list[i]=total_fitness(names_only,experiments_only,d_preferences,fitness_arr,test_timetable)
           
            #return timetable array to previous
            for n in range(experiment_length):
            #return experiments from period moving to
                experiment_n=experiments_switching[n]
                y_n=experiments_only.index(experiment_n)
                x_n= x_0+n*len(names_only)
                test_timetable[x_n][y_n]=1
            
            #return current experiment to current period    
                x_m=x+n*len(names_only)
                test_timetable[x_m][y]=1
            
            #remove experiment from new  period
                test_timetable[x_n][y]=0
            
            #remove new experiments  from current period
                test_timetable[x_m][y_n]=0
            
    #test  if fitness can be increased        
    if max(fitness_list)>current_fitness:#Fitness can be increased
        
        new_starting_period=starting_periods_dict[current_experiment][fitness_list.index(max(fitness_list))]# period current experiment will move to
        x_0=int(names_only.index(person)+(new_starting_period*len(names_only)))#x coordinate  of experiment in array
        
        experiments_switching=[]
        for n in range(experiment_length):
            period=new_starting_period+n
            experiments_switching.append(d_doing[person][period])
        
        
        for n in range(experiment_length):
            #removes experiments from period moving to
                experiment_n=experiments_switching[n]
                y_n=experiments_only.index(experiment_n)
                x_n= x_0+n*len(names_only)
                timetable_arr[x_n][y_n]=0
                
            #remove current experiment from current period    
                x_m=x+n*len(names_only)
                timetable_arr[x_m][y]=0
            
            #current experiment to  new  period
                timetable_arr[x_n][y]=1
            
            
            #new experiments  to current period
                timetable_arr[x_m][y_n]=1
            
                d_doing[person][starting_period+n]=experiment_n#Replaces current experiment with new one in dictionary of experiments doing in current period
                d_doing[person][new_starting_period+n]=experiments_only[y]#Replaces new experiment with current one in dictionary of experiments doing in new period
        possible_changes= timetable_arr.copy()
        
        start_loop="Yes"# loop returns to x=0 y=0
        
        change="Yes"
        
        
    if change=="No":#no change
        for n in range(experiment_length):
            if current_experiment== "I11":
                z=1
            if x+n*len(names_only)>120:
                z=raw_input()
            x_0=x+n*len(names_only)
            possible_changes[x_0][y]=0#removes element --> ensures isn't re tested  
        start_loop="No"
    return timetable_arr, possible_changes, d_doing, current_fitness,start_loop


#array possible_change is experiments that haven't previously been tested
def Gail(timetable_arr,d_doing):
    possible_changes=timetable_arr.copy()
    iterations=0
    plotting_list=[]
    while (possible_changes==0).all() != True and iterations < termination_value:
        iterations+=1
        start_loop="No"
        
        for x in range(len(names_only)*time_periods):
            for y in range(len(experiments_only)):
                if possible_changes[x][y]==1:
                    if start_loop!="Yes":
                        #timetable_arr, possible_changes, d_doing, change, y=different_experiment_test(x,y,timetable_arr,d_doing,possible_changes)# test if they would prefer to do a different experiment at that time returns: timetable, dictionary of experiments everyone is doing and if there was a change
                        change="No"
                        timetable_arr, possible_changes, d_doing, current_fitness,start_loop=switch_experiment_test(x,y,timetable_arr,d_doing,possible_changes,change)## test if the fitness can be increased by switching experiment at that period: returns timetable, dictionary of experiments everyone is doing and if there was a change
                    else:
                        continue
                else:
                    continue 
           
                    
                    
                    
                    
              
        plotting_list.append(current_fitness)     
        print current_fitness
    print timetable_arr
    return plotting_list, iterations

plotting_list, iterations= Gail(timetable_arr, d_doing)
gail_time= time.clock()-t_0
print gail_time
iteration_list= np.arange(0, iterations+1, 1)
plt.plot(plotting_list)
plt.ylabel('fitness')
plt.xlabel('iteration')
plt.axis([0,len(iteration_list)+2 , plotting_list[0], plotting_list[-1]])
plt.show()