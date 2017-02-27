from peem.usePEEM_tcpip import uv
from peem.leem_instances import leem2000
from gda.jython.commands.GeneralCommands import alias

def reconnect():
    print('-> reconnect uview2000')
    uv.reconnect()
    print('-> reconnect leem2000')
    leem2000.reconnect()

#add alias!!!!!!!!!!!!!!
alias("reconnect")
