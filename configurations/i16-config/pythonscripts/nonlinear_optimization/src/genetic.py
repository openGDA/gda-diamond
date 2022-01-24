'''
Created on 9 Jul 2013

@author: James
'''
import numpy as np
from random import *
from initial_setup import*
import matplotlib.pyplot as plt

#population=20#number of particles
#number_killed=8
#mutation_prob=0.1
#generations=15

population=100#number of particles
number_killed=35
mutation_prob=0.1
generations=20000


#Works out total number of people doing a specific experiment in timetable_arr in the same period as the x value
def total_people(x,i,timetable_arr):
        period=int(x/len(names_only))# period x is in; 0 denotes first period  (x is an integer --> returns whole number (rounds down)
        first_index=period*len(names_only)#First index of the period
        number_people=timetable_arr[first_index:(first_index+len(names_only)),i].sum()#works out how many people are doing the experiment in that period
        return number_people

def random_timetable():
    experiment=""  
    d_doing={key: [""]*time_periods for key in names_only}
    timetable_arr=np.zeros((len(names_only)*time_periods,len(experiments_only)),dtype=np.int)
    
    for n in range(time_periods):
        for x in range(len(names_only)):
            
            person=names_only[x]
            if d_doing[person][n]== "":
                time_period_0=n*len(names_only)
                number_people=max_number
                experiment=""
                while experiment=="" or  experiment in d_doing[person] or experiment in d_exclusions[person] or number_people>(max_number-1) or n not in starting_periods_dict[experiment]:         
                    y= int(random()*len(experiments_only))
                    experiment=experiments_only[y]
                    number_people=total_people(time_period_0,y,timetable_arr)
                    
                
                for i in range(periods_dict[experiment]):
                    d_doing[person][n+i]=experiment
                    x_person_value=(n+i)*len(names_only)+x
                    timetable_arr[x_person_value][y]=1
    return timetable_arr, d_doing

timetable_arr, d_doing=random_timetable()
print timetable_arr, d_doing



def initialise_population():
    array_dictionary={}
    fitness_dictionary={}
    d_doing_dictionary={}
    population_list=[]
    for n in range(population):
        particle_name="particle_%d" % (n)# particle reference name
        timetable_arr, d_doing=random_timetable()
        fitness=total_fitness(names_only,experiments_only,d_preferences,fitness_arr,timetable_arr)
        array_dictionary.update({particle_name:timetable_arr})
        fitness_dictionary.update({particle_name:fitness})
        d_doing_dictionary.update({particle_name:d_doing})
        max_fitness=max(fitness_dictionary.values())
        population_list.append(particle_name)
    return array_dictionary, fitness_dictionary,d_doing_dictionary, max_fitness, population_list
     
  
array_dictionary,  fitness_dictionary, d_doing_dictionary,  max_fitness_0, population_list=initialise_population()




def select_parents(population_list):
    parent_1=population_list[int(random()*len(population_list))]#ensures same particle not chosen twice
    population_list.remove(parent_1)
    parent_2=population_list[int(random()*len(population_list))]
    population_list.append(parent_1)
    return parent_1,  parent_2


def create_child(p_1, p_2,d_doing_dictionary):
    new_individual_array=np.zeros((len(names_only)*time_periods,len(experiments_only)),dtype=np.int)
    sum_fitness=fitness_dictionary[p_1]+fitness_dictionary[parent_2]
    p_1_weighting=fitness_dictionary[p_1]/sum_fitness
    d_doing={key: [""]*time_periods for key in names_only}
    for i in range(len(names_only)*time_periods):
        person=names_only[i%len(names_only)]
        period=int(i/len(names_only))
        while d_doing[person][period]=="":
            if random() < p_1_weighting:
                y=list(array_dictionary[p_1][i]).index(1)
                experiment=experiments_only[y]
                if period in starting_periods_dict[experiment]:
                    for n in range(periods_dict[experiment]):
                        period_1=period+n
                        x=period_1*len(names_only)+names_only.index(person)
                        new_individual_array[x]=array_dictionary[p_1][x]#gene from parent 1
                        d_doing[person][period_1]=d_doing_dictionary[p_1][person][period_1]
            else:
                y=list(array_dictionary[p_2][i]).index(1)
                experiment=experiments_only[y]
                if period in starting_periods_dict[experiment]:
                    for n in range(periods_dict[experiment]):
                        period_1=period+n
                        x=period_1*len(names_only)+names_only.index(person)
                        new_individual_array[x]=array_dictionary[p_2][x]#gene from parent 2
                        d_doing[person][period_1]=d_doing_dictionary[p_2][person][period_1]
    
    
            
    return new_individual_array, d_doing




def mutation(new_individual_array, d_doing):

        
    for i in range(len(names_only)*time_periods):
        
        if random()<mutation_prob:
            person=names_only[i%len(names_only)]
            period=int(i/len(names_only))
            current_y=list(new_individual_array[i]).index(1)
            current_experiment=experiments_only[current_y]
            current_length=periods_dict[current_experiment]
            for n in range(current_length):
                if d_doing[person][period-n]==current_experiment:
                    starting_period=period-n
            for n in range(current_length):# set all current experiment to 0
                period_1=starting_period+n
                x=period_1*len(names_only)+names_only.index(person)
                new_individual_array[x]=[0]*len(experiments_only)
                d_doing[person][period_1]=""
                
            for n in range(current_length):  
                period_1=starting_period+n
                x=period_1*len(names_only)+names_only.index(person)
                if list(new_individual_array[x])==[0]*len(experiments_only):
                    new_experiment=""
                    duration=0
                    while new_experiment=="" or new_experiment in d_doing[person] or period_1+duration>starting_period+current_length or period_1 not in starting_periods_dict[new_experiment]:
                        y=int(random()*len(experiments_only))
                        new_experiment=experiments_only[y]
                        duration=periods_dict[new_experiment]
                    for m in range(duration):
                        d_doing[person][period_1+m]=new_experiment
                        x=(period_1+m)*len(names_only)+names_only.index(person)
                        new_individual_array[x][y]=1

            
        
    
    return  new_individual_array, d_doing


def hard_constraint_test(new_individual_array, d_doing):
    outcome="survives"
    for n in range(time_periods):
        for x_0 in range(len(names_only)):
            x=n*len(names_only)+x_0
            person=names_only[x_0]
            experiment=d_doing[person][n]
            experiment_index=experiments_only.index(experiment)
            number_people=number_people=total_people(x,experiment_index,new_individual_array)
            if  d_doing[person].count(experiment)!=periods_dict[experiment] or experiment in d_exclusions[person]:
                outcome="dies"
    
            elif number_people>(max_number-1):
                outcome="dies"
            else:
                continue
        return outcome
 


    
#while termination != true
#kills individuals --> sets fitness to 0
plotting_list=[max_fitness_0]

for n in range(generations):
    
    for a in range(number_killed):
        min_fitness=min(fitness_dictionary.values())
        for name in fitness_dictionary.keys():
            if fitness_dictionary[name]==min_fitness:
                remove_name=name
        fitness_dictionary[remove_name]=""
        d_doing_dictionary[remove_name]={}
        population_list.remove(remove_name)
        array_dictionary[remove_name]=np.zeros((len(names_only)*time_periods,len(experiments_only)),dtype=np.int)
        
    #create new population
    while "" in fitness_dictionary.values():
        new_individual_array=np.zeros((len(names_only)*time_periods,len(experiments_only)),dtype=np.int)
        for name in fitness_dictionary.keys():
            if fitness_dictionary[name]=="":
                particle_name=name
       
        #parent_1, parent_2="",""
        parent_1, parent_2=select_parents(population_list)# randomly select two individuals
        new_individual_array, d_doing=create_child(parent_1, parent_2,d_doing_dictionary)
        if hard_constraint_test(new_individual_array, d_doing)=="survives":
            new_individual_array, d_doing=mutation(new_individual_array, d_doing)
        
        
        if hard_constraint_test(new_individual_array, d_doing)=="survives":
            fitness=total_fitness(names_only,experiments_only,d_preferences,fitness_arr,new_individual_array)
            d_doing_dictionary[particle_name]=d_doing
            population_list.append(particle_name)
            array_dictionary[particle_name]=new_individual_array
            fitness_dictionary[particle_name]=fitness
        
    
    max_fitness=max(fitness_dictionary.values())
    
    plotting_list.append(max_fitness)
    
    print max_fitness
for name in fitness_dictionary.keys():
            if fitness_dictionary[name]==max_fitness:
                particle_name=name
timetable_arr=array_dictionary[particle_name]
d_doing=d_doing_dictionary[particle_name]
print timetable_arr
generation_list= np.arange(0, generations+1, 1)
plt.plot(plotting_list)
plt.ylabel('max fitness')
plt.xlabel('generation')
plt.axis([0,len(generation_list)+2 , max_fitness_0, max_fitness])
plt.show()
# fix so it works on workstations (hopefully).
# plot(plotting_list)
# ylabel('max fitness')
# xlabel('generation')
# axis([0,len(generation_list)+2 , max_fitness_0, max_fitness])
# show()
