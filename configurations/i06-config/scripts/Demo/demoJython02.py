
print "-------------- Jython Basics ------------------------"

str01="hello world";
print str01.upper();

x=1e6+0.000001e-4
y=123.45
format="%32.20g" #32 dig width, 20 
print type(x)
print(format  %x)
print("%32.20g, %8.3f"  %(x,y))


def swap(a, b):
    return b,a
    
x=100; y=200;
[x,y]=swap(x,y);
print x,y

#Fibonacci series implementation 1:
a,b=0,1; #more than one variable can be assigned together in one line
while(b < 5000):
    print b, #a trailing comma avoids the newline after the output
    a,b=b,a+b;

print"\n";


# list example
l1=[]; #an empty list
l2=[1,2,3]
l3=[1,2,3],[2,5,6],[7,8,9] # a tuple
l4=[[1,2,3],[2,5,6],[7,8,9]] # a list

myList=["abc", "def", 123, 3+4j, 784.164]; print myList;
print myList[2:4]; 
myList[0:2]=[100, 200]; #replace the list content
print myList;

myList[2]=[]; #remove one item
print myList;

myList[2:] = myList[3:];
print myList

myList.pop(2); print myList;

#Fibonacci series implementation 2:
fList=[0,1,"end"]; l=len(fList)-1;
while (l < 20):
    fList[l:l]=[fList[l-2]+fList[l-1]]; #insert new item before "end"
    l=len(fList)-1;
print "The Fibonacci is:", fList; #note a space is inserted between items automatically


import funs
print dir(funs) #to find out what are defined in a module

funs.fib(100);
aliasFun = funs.fib;
aliasFun(200)


#if structure
x=int(raw_input("Please input a number:"))# input from keyboard
if x<0:
    x=0; print "Negative changed to zero"
elif x==0:
    print "ZERO"
elif x ==1:
    print "SINGLE"
else:
    print "MORE"

#for sturecure
#In Python, for statement always iterates over the items of a sequence
#(a list or a string), in the order that they appear in the sequence
for n in range(2, 10):
    for x in range(2, n):
        if n % x == 0:
            print n, 'equals', x, '*', n/x
            break
    else:
        print n, "is a prime number"

#tulip is readable only list
t1=()
t2=(1,)
t3=(1,2,3)
t4=((1,2),(3,4))


# map is the key:value pairs of hash table
h1={}
h2={1:"one",2:"two",3:"three"} #name:value pairs
h3={"x":1,"ints":(1,2,3)}

import math
x=int(raw_input("Please enter a positive number:"));
try:
    root=math.sqrt(x);
except:
    print "wrong 01"
else:
    print "The root of", x, "is", root;


#exec can transfer a string to the Jython for execution
x,y=100,200;
codeFragment01=raw_input("Please enter some code (e.g. 'print x+y'):");
exec codeFragment01;

#eval is the same as exec but only accept Jython string.
#4codeFragment02=str(input("Please enter some code (e.g. 'print x+y'):"));
#result=eval(codeFragment02);
#print "result if eval is:" ,result;


print "-------------- OS environment ------------------------"
import os
env=os.environ; print env;
wd=os.getcwd(); print wd
execfile("C:\\Dev\\JythonDev\\testPyDev\\src\\root\\nested\\example.py");

import sys
print sys.path
import example



print "-------------- Using Java from Jython ------------------------"

#import Java packages as needed
import java.lang as lang

#Invoke the Java static method:
lang.System.out.println("Hello Jython from Java");

#Create Java instance the same way as create Python object, without using the Java new keyword
myStr = lang.String("Zot");

#The Java method can be invoked in two way:
#1. bounded way
print myStr.startsWith("Z")

#2. Unbounded way
print lang.String.startsWith(myStr, "Z");
  
#jarrays
import jarray
x=jarray.zeros(200,"i");
print x;

import java.lang.Math
y=java.lang.Math.sqrt(256);
print y;
