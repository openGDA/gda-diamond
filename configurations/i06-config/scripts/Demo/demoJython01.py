#
#   Introducing Jython
#

#   Jython is a scripting language, so you can define variables easily:

number = 12
hello = "Hello"

#to print:

print hello
print number
print "Number is: " + `ten`

#program control:

for i in range(5):
	Thread.sleep(1000)  # this pauses the script for 1 second
	print i

value = 10
if (value == 10):
	print "value is 10"

i = 0
while i < 2:
	print i
	i += 1

#    Note that you don't have to tell the script the start or end of the for loop with braces or and "end for" type statement
#    Instead, the script knows what is inside the for-loop by the indentation of the lines
#    You must use tabs to indent lines!

# to create code for reuse, define a function using the def command:

def myFunction():
	print "You've used my function!"

myFunction()


#    To use extra modules from Java, Jython or which you have written yourself, use the import command:

import demo_module
demo_module.myMethod()


#About how to raise and catch user defined exception
try:
    #check something first. if it's not OK, raise an exception and quit
    a=1;
    if a == 1:
        raise Exception('Something wrong because a equals to 1, the script will quit!', 'More reasons here:');
    
    #The check passed, continue:
    print "The checking is OK, to continute...";
    
except Exception, inst:
    print "Check failed!";
    x, y = inst;          # __getitem__ allows args to be unpacked directly
    print x;
    print y;
    


# namespaces:

# scripts and the command-line on the Scripting Terminal tab have the same namespace,
# so if you define an object or variable in one, you can access it from the other

