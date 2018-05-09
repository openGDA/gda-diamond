from gda.jython import InterfaceProvider
def alias():
    """
    function to list the motors
    """
    s="Usage: \n\talias functionName\n\nwhere functionName is a function in the global namespace.\nThis dynamically adds a function to the extended syntax.\n"
    s+="List of aliased command:\n"
    m=InterfaceProvider.getAliasedCommandProvider().getAliasedCommands()
    for i in m:
        s+= "\t" + i+"\n"
    return s
        