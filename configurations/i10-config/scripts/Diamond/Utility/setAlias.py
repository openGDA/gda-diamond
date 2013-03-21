
from Diamond.PseudoDevices.AliasDevice import AliasDeviceClass;

print "-------------------------------------------------------------------"
print "Enable the setAlias/setGdaAlias functions"
print "Usage: "
print "     setAlias('aliasName', 'AliasedJythonExpression')"
print "or:"
print "     setGdaAlias('aliasName', 'AliasedJythonExpression')"
print "For example:"
print "    setGdaAlias('t1', 'testMotor1.moveTo(1)')"
print "will create an aliase 't1' command to move the testMotor1 to 1 effectively"


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
