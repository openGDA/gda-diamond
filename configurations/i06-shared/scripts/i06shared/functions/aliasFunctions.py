'''
Generic code sections from original BeamlineI06/beamline.py in GDA8.38
Created on 25 Jan 2017

@author: fy65
'''
from gda.jython.commands.GeneralCommands import alias
print "-"*100
print "Enable the setAlias/setGdaAlias functions"
print "Usage: "
print "     setAlias('aliasName', 'AliasedJythonExpression')"
print "or:"
print "     setGdaAlias('aliasName', 'AliasedJythonExpression')"
print "For example:"
print "    setGdaAlias('t1', 'testMotor1.moveTo(1)')"
print "will create an alias 't1' command to move the testMotor1 to 1 effectively"


from Diamond.PseudoDevices.AliasDevice import AliasDeviceClass;

#Use the AliasDeviceClass to setup an alias
def setAlias(aliasName, gdaExpression):
    exec(aliasName+"=None") in globals();
    globals()[aliasName]=AliasDeviceClass(aliasName, gdaExpression);

#Use the GDA alias function to setup an alias
def setGdaAlias(aliasName, gdaExpression):
#    b="exec('"+gdaExpression+"') in globals()";
    a="def "+ aliasName + "():\n\t" + "exec('" + gdaExpression + "') in globals()" + "\n";
    exec(a) in globals();
    alias(aliasName);


#Usage: 
#setAlias("t1", "testMotor1.moveTo(1)");

#setGdaAlias("t2", "testMotor1.moveTo(2)");
